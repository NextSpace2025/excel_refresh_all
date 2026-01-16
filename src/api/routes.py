from fastapi import HTTPException, BackgroundTasks
from typing import List
from src.api.models import FilePath, FilePathWithId, RefreshSettings
from src.database import db_manager
from src.excel import excelrefresh_time_delay as excel_refresher
from src.database import place


# In-memory storage for settings (can be moved to a config file or DB later)
settings = RefreshSettings()


async def read_root():
    """Check if the API is running."""
    return {"message": "Welcome to the Excel Refresh API. See /docs for available endpoints."}


async def get_files():
    """Retrieves a list of all file paths stored in the database."""
    files = db_manager.get_all_paths_with_ids()
    return [{"id": id, "file_path": path} for id, path in files]


async def add_file(file: FilePath):
    """Adds a new file path to the database."""
    try:
        db_manager.add_path(file.path)
        return {"message": "File path added successfully.", "path": file.path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def update_file(file_id: int, file: FilePath):
    """Updates an existing file path identified by its ID."""
    success = db_manager.update_path_by_id(file_id, file.path)
    if not success:
        raise HTTPException(status_code=400, detail=f"Path '{file.path}' may already exist.")
    return {"message": f"File ID {file_id} updated successfully.", "new_path": file.path}


async def delete_file(file_id: int):
    """Deletes a file path from the database by its ID."""
    db_manager.delete_path_by_id(file_id)
    return {"message": f"File ID {file_id} deleted successfully."}


async def get_settings():
    """Retrieves the current refresh and inter-file delay settings."""
    return settings


async def update_settings(new_settings: RefreshSettings):
    """Updates the refresh and inter-file delay settings."""
    global settings
    settings = new_settings
    return {"message": "Settings updated successfully.", "new_settings": settings}


def _run_refresh_background(refresh_delay: int, inter_file_delay: int):
    """Background task to run Excel refresh process."""
    try:
        excel_refresher.run_all_refreshes(
            refresh_delay=refresh_delay,
            inter_file_delay=inter_file_delay
        )
    except Exception as e:
        print(f"Background refresh error: {e}")


async def run_refresh(background_tasks: BackgroundTasks = None):
    """
    Triggers the process to refresh all Excel files in the database.
    This is a non-blocking call; the process runs in the background.
    """
    import threading

    try:
        if background_tasks:
            background_tasks.add_task(
                _run_refresh_background,
                refresh_delay=settings.refresh_delay,
                inter_file_delay=settings.inter_file_delay
            )
        else:
            # BackgroundTasks가 없으면 스레드로 실행
            thread = threading.Thread(
                target=_run_refresh_background,
                args=(settings.refresh_delay, settings.inter_file_delay)
            )
            thread.start()
        return {"message": "Excel refresh process initiated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during the refresh process: {str(e)}")


async def init_database():
    """
    Populates the database with the initial list of files from `place.py`.
    This is useful for first-time setup.
    """
    try:
        place.populate_db_from_initial_list()
        return {"message": "Database successfully populated with the initial file list."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize database: {str(e)}")


async def browse_folder(path: str = None):
    """
    Browse folder structure and return files/folders.
    """
    import os

    if path is None or path == "":
        # 드라이브 목록 반환 (Windows)
        if os.name == 'nt':
            import string
            drives = []
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append({
                        "name": f"{letter}:",
                        "path": drive,
                        "type": "drive"
                    })
            return {"items": drives, "current_path": ""}
        else:
            path = "/"

    try:
        items = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            try:
                is_dir = os.path.isdir(full_path)
                # Excel 파일만 표시 (폴더는 항상 표시)
                if is_dir or name.lower().endswith(('.xlsx', '.xlsm', '.xls')):
                    items.append({
                        "name": name,
                        "path": full_path,
                        "type": "folder" if is_dir else "file"
                    })
            except PermissionError:
                continue

        # 폴더 먼저, 그 다음 파일 (이름순 정렬)
        items.sort(key=lambda x: (x["type"] != "folder", x["name"].lower()))

        return {"items": items, "current_path": path}
    except PermissionError:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="경로를 찾을 수 없습니다.")
