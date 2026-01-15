import subprocess
import os

# 엑셀 새로고침 스크립트 실행
script_dir = os.path.dirname(os.path.abspath(__file__))
refresh_script = os.path.join(script_dir, 'excelrefresh_time_delay.py')

subprocess.run(["python", refresh_script])

print("✅ 엑셀 리프레시 작업이 완료되었습니다.")
exit(0)
