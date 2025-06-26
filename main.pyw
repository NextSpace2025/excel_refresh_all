import time
import subprocess

# 1. 엑셀 새로고침 스크립트 실행
subprocess.run(["python", r'C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Project\refresh\excelrefresh_time_delay.py'])


# # 2. 15초 대기
time.sleep(15)

# 3. DB 저장 스크립트 실행
subprocess.run(["python", r'C:\Users\ikjin\OneDrive - (주)익진엔지니어링\김재용\weapon\Project\refresh\xlsmtodb.py'])


print("모든 작업이 완료되었습니다.")
exit(0)
