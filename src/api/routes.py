from fastapi import HTTPException
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


async def run_refresh():
    """
    Triggers the process to refresh all Excel files in the database.
    This is a non-blocking call; the process runs in the background.
    """
    try:
        # In a real-world scenario, this should be a background task (e.g., with Celery or FastAPI's BackgroundTasks)
        # For this local CLI tool, a simple call is sufficient.
        excel_refresher.run_all_refreshes(
            refresh_delay=settings.refresh_delay,
            inter_file_delay=settings.inter_file_delay
        )
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
