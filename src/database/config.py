"""
데이터베이스 초기화를 위한 엑셀 파일 경로 설정
"""

# 공통 경로 변수
COMPANY_SHARE = r"C:\Users\ikjin\(주)익진엔지니어링\공무 - 공무\01 집행정리"
ONEDRIVE_BASE = r"C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Data"

# 2024년 진행현장
YANGJU_OKJEONG = fr"{COMPANY_SHARE}\2024년 진행현장\양주옥정물류센터\양주옥정 집행내역서.xlsx"
SIHWA_LAGOON_2ND = fr"{COMPANY_SHARE}\2024년 진행현장\시화호라군인테라스2차\시화호라군인테라스2차 집행내역서.xlsx"
BYEOLLAE_XI_1 = fr"{COMPANY_SHARE}\2024년 진행현장\별내자이더스타 이그제큐티브\별내자이 집행내역서.xlsx"
BYEOLLAE_XI_2 = fr"{COMPANY_SHARE}\2024년 진행현장\별내자이더스타 이그제큐티브\별내자이 집행내역서(커튼월룩).xlsx"
CHANGWON_SANGNAM = fr"{COMPANY_SHARE}\2024년 진행현장\창원 상남동생활형숙박시설\창원 상남동 집행내역서.xlsx"

# 2023년 진행현장
SIHWA_LAGOON = fr"{COMPANY_SHARE}\2023년 진행현장\시화호 라군인테라스\시화호 라군인테라스 집행내역서.xlsx"
HYUNDAI_PREMIER = fr"{COMPANY_SHARE}\2023년 진행현장\현대프리미어캠퍼스 세마역\현대프리미어캠퍼스 세마역 집행내역서.xlsx"

# 2025년 집행현장
HILLSTATE_JANGAN = fr"{COMPANY_SHARE}\2025년 집행현장\힐스테이트 장안 라보니타\힐스테이트 장안 집행내역서.xlsx"

# 마스터 DB 파일
MASTER_DB = fr"{ONEDRIVE_BASE}\집행내역서(DB).xlsm"


# 초기화할 파일 목록 (순서대로 처리됨)
INITIAL_FILES = [
    YANGJU_OKJEONG,
    SIHWA_LAGOON,
    SIHWA_LAGOON_2ND,
    BYEOLLAE_XI_1,
    BYEOLLAE_XI_2,
    CHANGWON_SANGNAM,
    HILLSTATE_JANGAN,
    HYUNDAI_PREMIER,
    MASTER_DB,  # 마스터 DB는 항상 마지막
]
