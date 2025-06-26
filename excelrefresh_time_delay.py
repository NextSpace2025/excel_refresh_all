import win32com.client
import time
import os

def refresh_excel(file_path):
    try:
        print(f"🔄 새로고침 시작: {file_path}")
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False

        if not os.path.exists(file_path):
            print(f"❌ 파일 없음: {file_path}")
            return

        workbook = excel.Workbooks.Open(file_path)
        workbook.RefreshAll()
        print(f"✅ 새로고침 요청 완료: {file_path}")
        time.sleep(10)

        workbook.Save()
        workbook.Close(False)
        excel.Quit()
        print(f"✅ 저장 및 종료 완료: {file_path}")

    except Exception as e:
        print(f"❌ 오류 발생 - {file_path}: {e}")

def refresh_and_run_macro(file_path, macro_name):
    try:
        print(f"🔄 [후처리] 새로고침 + 매크로 실행 시작: {file_path}")
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False

        if not os.path.exists(file_path):
            print(f"❌ 파일 없음: {file_path}")
            return

        workbook = excel.Workbooks.Open(file_path)
        workbook.RefreshAll()
        print(f"✅ [후처리] 새로고침 요청 완료: {file_path}")
        time.sleep(10)

        excel.Application.Run(macro_name)
        print(f"✅ [후처리] 매크로 실행 완료: {macro_name}")

        workbook.Save()
        workbook.Close(False)
        excel.Quit()
        print(f"✅ [후처리] 저장 및 종료 완료: {file_path}")

    except Exception as e:
        print(f"❌ [후처리] 오류 발생 - {file_path}: {e}")

if __name__ == '__main__':
    excel_files = [
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2024년 진행현장\양주옥정물류센터\양주옥정 집행내역서.xlsx",
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2023년 진행현장\시화호 라군인테라스\시화호 라군인테라스 집행내역서.xlsx",
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2024년 진행현장\시화호라군인테라스2차\시화호라군인테라스2차 집행내역서.xlsx",
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2024년 진행현장\별내자이더스타 이그제큐티브\별내자이 집행내역서.xlsx",
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2024년 진행현장\별내자이더스타 이그제큐티브\별내자이 집행내역서(커튼월룩).xlsx",
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2024년 진행현장\창원 상남동생활형숙박시설\창원 상남동 집행내역서.xlsx",
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2025년 집행현장\힐스테이트 장안 라보니타\힐스테이트 장안 집행내역서.xlsx",
        r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리\2023년 진행현장\현대프리미어캠퍼스 세마역\현대프리미어캠퍼스 세마역 집행내역서.xlsx",
        r"C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Data\집행내역서(DB).xlsm",
    ]

    for file in excel_files:
        refresh_excel(file)
        print("⏳ 다음 파일까지 5초 대기 중...")
        time.sleep(5)  # 각 파일 간 10초 간격

    # ✅ 후처리
    time.sleep(30)

    target_file = r"C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Data\집행내역서(DB).xlsmm"
    macro_name = "CombineWithTableAndSource"

    refresh_and_run_macro(target_file, macro_name)
    print("✅ 모든 작업 완료")
