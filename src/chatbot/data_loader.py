"""
엑셀 데이터를 SQLite DB로 변환하는 모듈
"""
import sqlite3
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ExcelToDBLoader:
    """엑셀 파일을 SQLite DB로 변환하는 클래스"""

    def __init__(self, db_path: str = "chatbot_data.db"):
        """
        Args:
            db_path: SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """데이터베이스 초기화 - 메타데이터 테이블 생성"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 로드된 파일 메타데이터 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loaded_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    file_name TEXT,
                    sheet_name TEXT,
                    table_name TEXT,
                    row_count INTEGER,
                    column_count INTEGER,
                    columns TEXT,
                    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def load_excel_to_db(
        self,
        excel_path: str,
        sheet_name: Optional[str] = None,
        table_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        엑셀 파일을 SQLite 테이블로 변환

        Args:
            excel_path: 엑셀 파일 경로
            sheet_name: 시트 이름 (None이면 첫 번째 시트)
            table_name: 생성할 테이블 이름 (None이면 파일명 기반으로 자동 생성)

        Returns:
            로드 결과 정보
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas가 설치되어 있지 않습니다. pip install pandas openpyxl 실행하세요.")

        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {excel_path}")

        # 파일명에서 테이블명 생성
        file_name = Path(excel_path).stem
        if table_name is None:
            # 특수문자 제거하고 테이블명 생성
            table_name = "".join(c if c.isalnum() or c == '_' else '_' for c in file_name)
            table_name = f"excel_{table_name}"

        # 엑셀 읽기
        try:
            if sheet_name:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_path)
                sheet_name = "Sheet1"  # 기본값
        except Exception as e:
            raise Exception(f"엑셀 파일 읽기 실패: {e}")

        # 컬럼명 정리 (공백, 특수문자 처리)
        df.columns = [
            "".join(c if c.isalnum() or c == '_' else '_' for c in str(col))
            for col in df.columns
        ]

        # SQLite에 저장
        with sqlite3.connect(self.db_path) as conn:
            # 기존 테이블 삭제 후 새로 생성
            df.to_sql(table_name, conn, if_exists='replace', index=False)

            # 메타데이터 저장
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO loaded_files
                (file_path, file_name, sheet_name, table_name, row_count, column_count, columns)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                excel_path,
                file_name,
                sheet_name,
                table_name,
                len(df),
                len(df.columns),
                ",".join(df.columns)
            ))
            conn.commit()

        return {
            "status": "success",
            "file_path": excel_path,
            "table_name": table_name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns)
        }

    def load_all_sheets(self, excel_path: str) -> List[Dict[str, Any]]:
        """
        엑셀 파일의 모든 시트를 각각의 테이블로 로드

        Args:
            excel_path: 엑셀 파일 경로

        Returns:
            각 시트별 로드 결과 리스트
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas가 설치되어 있지 않습니다.")

        # 모든 시트 이름 가져오기
        xl = pd.ExcelFile(excel_path)
        results = []

        for sheet in xl.sheet_names:
            file_name = Path(excel_path).stem
            table_name = f"excel_{file_name}_{sheet}".replace(" ", "_")
            table_name = "".join(c if c.isalnum() or c == '_' else '_' for c in table_name)

            try:
                result = self.load_excel_to_db(excel_path, sheet_name=sheet, table_name=table_name)
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "sheet_name": sheet,
                    "error": str(e)
                })

        return results

    def get_loaded_files(self) -> List[Dict[str, Any]]:
        """로드된 파일 목록 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM loaded_files ORDER BY loaded_at DESC")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def query_table(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """테이블 데이터 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def search_data(self, query: str, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        데이터 검색 (간단한 LIKE 검색)

        Args:
            query: 검색어
            table_name: 특정 테이블에서만 검색 (None이면 모든 테이블)

        Returns:
            검색 결과
        """
        results = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 검색할 테이블 목록
            if table_name:
                tables = [table_name]
            else:
                cursor.execute("""
                    SELECT table_name FROM loaded_files
                """)
                tables = [row[0] for row in cursor.fetchall()]

            for tbl in tables:
                try:
                    # 테이블의 모든 컬럼 가져오기
                    cursor.execute(f"PRAGMA table_info({tbl})")
                    columns = [row[1] for row in cursor.fetchall()]

                    # 각 컬럼에서 검색
                    conditions = " OR ".join([f"{col} LIKE ?" for col in columns])
                    search_term = f"%{query}%"
                    params = [search_term] * len(columns)

                    cursor.execute(f"""
                        SELECT * FROM {tbl} WHERE {conditions} LIMIT 50
                    """, params)

                    rows = cursor.fetchall()
                    for row in rows:
                        results.append({
                            "table": tbl,
                            "data": dict(zip(columns, row))
                        })
                except Exception as e:
                    continue

        return results

    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """테이블 스키마 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [
                {"name": row[1], "type": row[2]}
                for row in cursor.fetchall()
            ]

    def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        """
        SQL 쿼리 직접 실행 (SELECT만 허용)

        Args:
            sql: SQL 쿼리문

        Returns:
            쿼리 결과
        """
        # SELECT만 허용
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            raise ValueError("SELECT 쿼리만 실행할 수 있습니다.")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_data_summary(self, table_name: str) -> Dict[str, Any]:
        """테이블 데이터 요약 정보"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 행 수
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # 컬럼 정보
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]

            # 샘플 데이터 (처음 5행)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_rows = cursor.fetchall()
            col_names = [col["name"] for col in columns]
            sample_data = [dict(zip(col_names, row)) for row in sample_rows]

            return {
                "table_name": table_name,
                "row_count": row_count,
                "columns": columns,
                "sample_data": sample_data
            }


# 사용 예시
if __name__ == "__main__":
    loader = ExcelToDBLoader("chatbot_data.db")

    # 테스트
    print("ExcelToDBLoader 초기화 완료")
    print(f"DB 경로: {loader.db_path}")
