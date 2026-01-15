import sqlite3
import os
from pathlib import Path

# 프로젝트 루트 경로 (main.py가 있는 위치)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_FILE = str(PROJECT_ROOT / "excel_paths.db")
TABLE_NAME = "paths"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_table_if_not_exists():
    """Creates the file paths table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def add_path(file_path):
    """Adds a new file path to the database."""
    if not os.path.exists(file_path):
        print(f"Warning: Path does not exist: {file_path}")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO {TABLE_NAME} (file_path) VALUES (?)", (file_path,))
        conn.commit()
        print(f"Successfully added path: {file_path}")
    except sqlite3.IntegrityError:
        print(f"Path already exists in database: {file_path}")
    finally:
        conn.close()

def get_all_paths():
    """Retrieves all file paths from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT file_path FROM {TABLE_NAME}")
    paths = [row[0] for row in cursor.fetchall()]
    conn.close()
    return paths

def get_all_paths_with_ids():
    """Retrieves all file paths with their IDs from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, file_path FROM {TABLE_NAME}")
    paths = cursor.fetchall()
    conn.close()
    return paths

def update_path_by_id(path_id, new_file_path):
    """Updates a file path in the database identified by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE {TABLE_NAME} SET file_path = ? WHERE id = ?", (new_file_path, path_id))
        conn.commit()
        print(f"Successfully updated path ID {path_id}.")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: The path '{new_file_path}' already exists.")
        return False
    finally:
        conn.close()

def delete_path_by_id(path_id):
    """Deletes a file path from the database by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (path_id,))
    conn.commit()
    conn.close()
    print(f"Successfully deleted path ID {path_id}.")

