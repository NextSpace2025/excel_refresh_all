"""
터미널 기반 인터페이스
"""
from src.database import db_manager
from src.excel import excelrefresh_time_delay as excel_refresher
from src.database import place


def show_menu():
    """메인 메뉴 표시"""
    print("\n" + "="*50)
    print("       Excel Refresh Manager - Terminal Mode")
    print("="*50)
    print("1. 파일 목록 보기")
    print("2. 파일 추가")
    print("3. 파일 삭제")
    print("4. Excel 새로고침 실행")
    print("5. 초기 데이터로 DB 초기화")
    print("0. 종료")
    print("="*50)


def list_files():
    """등록된 파일 목록 표시"""
    files = db_manager.get_all_paths_with_ids()
    if files:
        print("\n[등록된 파일 목록]")
        for id, path in files:
            print(f"  [{id}] {path}")
    else:
        print("\n등록된 파일이 없습니다.")
    return files


def add_file():
    """파일 추가"""
    path = input("추가할 파일 경로: ").strip()
    if path:
        try:
            db_manager.add_path(path)
            print(f"추가 완료: {path}")
        except Exception as e:
            print(f"오류: {e}")


def delete_file():
    """파일 삭제"""
    files = list_files()
    if files:
        file_id = input("삭제할 파일 ID: ").strip()
        if file_id.isdigit():
            db_manager.delete_path_by_id(int(file_id))
            print(f"ID {file_id} 삭제 완료")


def run_refresh():
    """Excel 새로고침 실행"""
    try:
        refresh_delay = input("새로고침 대기 시간 (초, 기본값 5): ").strip()
        inter_file_delay = input("파일 간 대기 시간 (초, 기본값 2): ").strip()
        refresh_delay = int(refresh_delay) if refresh_delay else 5
        inter_file_delay = int(inter_file_delay) if inter_file_delay else 2

        print("\nExcel 새로고침을 시작합니다...")
        excel_refresher.run_all_refreshes(
            refresh_delay=refresh_delay,
            inter_file_delay=inter_file_delay
        )
        print("새로고침 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")


def init_db():
    """DB 초기화"""
    try:
        place.populate_db_from_initial_list()
        print("DB 초기화 완료!")
    except Exception as e:
        print(f"오류: {e}")


def run():
    """터미널 모드 실행"""
    db_manager.create_table_if_not_exists()

    while True:
        show_menu()
        choice = input("선택: ").strip()

        if choice == "1":
            list_files()
        elif choice == "2":
            add_file()
        elif choice == "3":
            delete_file()
        elif choice == "4":
            run_refresh()
        elif choice == "5":
            init_db()
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break
        else:
            print("잘못된 선택입니다.")


if __name__ == "__main__":
    run()
