from src.database import db_manager
from src.database.config import INITIAL_FILES


def populate_db_from_initial_list():
    """
    One-time function to populate the database with initial file paths.
    File paths are configured in config.py for easy management.
    """
    db_manager.create_table_if_not_exists()
    print(f"Adding {len(INITIAL_FILES)} files to the database...")
    for file_path in INITIAL_FILES:
        db_manager.add_path(file_path)
    print("Population complete.")
