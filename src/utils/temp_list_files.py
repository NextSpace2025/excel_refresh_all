from src.database import db_manager

def show_file_list():
    """Displays the list of files from the database."""
    print("--- 파일 목록 ---")
    db_manager.create_table_if_not_exists()
    all_paths = db_manager.get_all_paths_with_ids()
    if not all_paths:
        print("\n데이터베이스에 저장된 파일이 없습니다.")
        print("To populate the database with the initial list, run 'python main.py' and select option '9'.")
    else:
        for path_id, file_path in all_paths:
            print(f"  [{path_id}] {file_path}")
    print("-----------------\n")

if __name__ == '__main__':
    show_file_list()
