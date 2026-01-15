import pandas as pd
import sqlite3
import os

def convert_xlsm_to_csv_and_db():
    # 1. 
    xlsm_path = r"C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Data\집행내역서(DB).xlsm"
    sheet_name = "Combined"

    # 2. 저장할 경로 (파일명 포함)
    csv_path = r"C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Data\Combined(DB).csv"
    db_path = r"C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Data\Combined(DB).db"

    try:
        # 3. 시트 불러오기
        df = pd.read_excel(xlsm_path, sheet_name=sheet_name)
        
        # 4. CSV 저장 (없으면 새로 생성됨)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV 저장 완료: {csv_path}")

        # 5. SQLite DB 저장 (파일 없으면 새로 생성됨)
        conn = sqlite3.connect(db_path)
        df.to_sql("Combined", conn, if_exists="replace", index=False)
        conn.close()
        print(f"✅ DB 저장 완료: {db_path}")

    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없습니다: {e}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    convert_xlsm_to_csv_and_db()
    # 그냥 위 코드들이 바로 실행되기 때문에 여기선 아무 것도 안 해도 됨
    pass