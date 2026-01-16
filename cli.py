"""
Excel Refresh Manager CLI
사용법: python cli.py [명령어]

명령어:
    list        파일 목록 조회
    add <경로>  파일 추가
    delete <id> 파일 삭제
    settings    현재 설정 조회
    set <refresh> <inter>  설정 변경
    refresh     Excel 리프레시 실행
    init        DB 초기화
    status      API 서버 상태 확인
"""

import sys
import requests

API_URL = "http://127.0.0.1:8000"


def print_help():
    print("""
Excel Refresh Manager CLI
=========================

사용법: python cli.py [명령어]

명령어:
    list              파일 목록 조회
    add <경로>        파일 추가
    delete <id>       파일 삭제
    settings          현재 설정 조회
    set <r> <i>       설정 변경 (r: 리프레시 대기, i: 파일간 대기)
    refresh           Excel 리프레시 실행
    init              DB 초기화
    status            API 서버 상태 확인
    help              도움말 표시

예시:
    python cli.py list
    python cli.py add "C:\\data\\report.xlsx"
    python cli.py delete 3
    python cli.py set 10 5
    python cli.py refresh
""")


def api_request(method, endpoint, json=None):
    """API 요청 공통 함수"""
    try:
        url = f"{API_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=json)
        elif method == "DELETE":
            response = requests.delete(url)
        elif method == "PUT":
            response = requests.put(url, json=json)

        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        print("오류: 서버에 연결할 수 없습니다.")
        print(f"서버가 {API_URL} 에서 실행 중인지 확인하세요.")
        sys.exit(1)


def cmd_status():
    """서버 상태 확인"""
    data, _ = api_request("GET", "/api")
    print(f"서버 상태: {data.get('message', '연결됨')}")


def cmd_list():
    """파일 목록 조회"""
    data, _ = api_request("GET", "/files")
    if not data:
        print("등록된 파일이 없습니다.")
        return

    print(f"\n등록된 파일 ({len(data)}개)")
    print("-" * 60)
    for file in data:
        print(f"  [{file['id']:3}] {file['file_path']}")
    print("-" * 60)


def cmd_add(path):
    """파일 추가"""
    data, status = api_request("POST", "/files", {"path": path})
    if status == 200:
        print(f"추가 완료: {path}")
    else:
        print(f"오류: {data.get('detail', '추가 실패')}")


def cmd_delete(file_id):
    """파일 삭제"""
    data, status = api_request("DELETE", f"/files/{file_id}")
    if status == 200:
        print(f"삭제 완료: ID {file_id}")
    else:
        print(f"오류: {data.get('detail', '삭제 실패')}")


def cmd_settings():
    """설정 조회"""
    data, _ = api_request("GET", "/settings")
    print(f"\n현재 설정")
    print("-" * 30)
    print(f"  리프레시 대기 시간: {data['refresh_delay']}초")
    print(f"  파일 간 대기 시간:  {data['inter_file_delay']}초")
    print("-" * 30)


def cmd_set(refresh_delay, inter_file_delay):
    """설정 변경"""
    data, status = api_request("POST", "/settings", {
        "refresh_delay": int(refresh_delay),
        "inter_file_delay": int(inter_file_delay)
    })
    if status == 200:
        print(f"설정 변경 완료: 리프레시={refresh_delay}초, 파일간={inter_file_delay}초")
    else:
        print(f"오류: {data.get('detail', '설정 변경 실패')}")


def cmd_refresh():
    """리프레시 실행"""
    print("Excel 리프레시를 시작합니다...")
    data, status = api_request("POST", "/run-refresh")
    if status == 200:
        print(f"결과: {data.get('message', '실행됨')}")
    else:
        print(f"오류: {data.get('detail', '실행 실패')}")


def cmd_init():
    """DB 초기화"""
    data, status = api_request("POST", "/init-db")
    if status == 200:
        print(f"결과: {data.get('message', '초기화 완료')}")
    else:
        print(f"오류: {data.get('detail', '초기화 실패')}")


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].lower()

    if cmd == "help":
        print_help()
    elif cmd == "status":
        cmd_status()
    elif cmd == "list":
        cmd_list()
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("사용법: python cli.py add <파일경로>")
            return
        cmd_add(sys.argv[2])
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("사용법: python cli.py delete <파일ID>")
            return
        cmd_delete(sys.argv[2])
    elif cmd == "settings":
        cmd_settings()
    elif cmd == "set":
        if len(sys.argv) < 4:
            print("사용법: python cli.py set <리프레시대기> <파일간대기>")
            print("예시: python cli.py set 10 5")
            return
        cmd_set(sys.argv[2], sys.argv[3])
    elif cmd == "refresh":
        cmd_refresh()
    elif cmd == "init":
        cmd_init()
    else:
        print(f"알 수 없는 명령어: {cmd}")
        print("python cli.py help 로 도움말을 확인하세요.")


if __name__ == "__main__":
    main()
