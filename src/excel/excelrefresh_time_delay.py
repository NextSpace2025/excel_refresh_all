import win32com.client
import time
import os

def refresh_excel(file_path, refresh_delay=10):
    try:
        print(f"🔄 새로고침 시작: {file_path}")
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False

        if not os.path.exists(file_path):
            print(f"❌ 파일 없음: {file_path}")
            return

        workbook = excel.Workbooks.Open(file_path)
        workbook.RefreshAll()
        print(f"✅ 새로고침 요청 완료. {refresh_delay}초 대기...")
        time.sleep(refresh_delay)

        workbook.Save()
        workbook.Close(False)
        excel.Quit()
        print(f"✅ 저장 및 종료 완료: {file_path}")

    except Exception as e:
        print(f"❌ 오류 발생 - {file_path}: {e}")

def refresh_and_run_macro(file_path, macro_name, refresh_delay=10):
    try:
        print(f"🔄 [후처리] 새로고침 + 매크로 실행 시작: {file_path}")
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False

        if not os.path.exists(file_path):
            print(f"❌ 파일 없음: {file_path}")
            return

        workbook = excel.Workbooks.Open(file_path)
        workbook.RefreshAll()
        print(f"✅ [후처리] 새로고침 요청 완료. {refresh_delay}초 대기...")
        time.sleep(refresh_delay)

        excel.Application.Run(macro_name)
        print(f"✅ [후처리] 매크로 실행 완료: {macro_name}")

        workbook.Save()
        workbook.Close(False)
        excel.Quit()
        print(f"✅ [후처리] 저장 및 종료 완료: {file_path}")

    except Exception as e:
        print(f"❌ [후처리] 오류 발생 - {file_path}: {e}")

def run_all_refreshes(refresh_delay=10, inter_file_delay=5):
    """
    Fetches the list of excel files from the database via place.py
    and runs the refresh process for all of them.
    """
    from src.database import db_manager
    excel_files = db_manager.get_all_paths()

    if not excel_files:
        print("No files found in the database. Add files using the 'add' command.")
        return

    for file in excel_files:
        refresh_excel(file, refresh_delay)
        print(f"⏳ 다음 파일까지 {inter_file_delay}초 대기 중...")
        time.sleep(inter_file_delay)

    # ✅ 후처리
    print(f"✨ 기본 새로고침 완료. 30초 후 후처리 작업을 시작합니다...")
    time.sleep(30)

    # 후처리 대상 파일이 DB에 있는지 확인
    from src.database.config import MASTER_DB
    if MASTER_DB in excel_files:
        macro_name = "CombineWithTableAndSource"
        refresh_and_run_macro(MASTER_DB, macro_name, refresh_delay)
    else:
        print(f"⚠️ 후처리 대상 파일({MASTER_DB})이 DB에 없습니다. 후처리 매크로를 실행하지 않습니다.")
    
    print("✅ 모든 작업 완료")

if __name__ == '__main__':
    # Interactive session is now handled by main.py
    # This block can be used for direct testing.
    print("Running refreshes with default delays (10s refresh, 5s inter-file)...")
    run_all_refreshes()
