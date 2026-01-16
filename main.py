from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from src.database import db_manager
from src.api.file_routes import router as file_router
from src.api.refresh_routes import router as refresh_router
from src.chatbot.router import router as chatbot_router


# --- Event Handlers ---
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Ensure the database and table exist on application startup."""
    db_manager.create_table_if_not_exists()
    print("FastAPI server started. Database is ready.")
    yield


# --- App Factory ---
def create_app(include_ui: bool = True) -> FastAPI:
    """FastAPI 앱 생성"""
    app = FastAPI(
        title="Excel Refresh API",
        description="An API to manage a list of Excel files and trigger a refresh process.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # API Routers
    app.include_router(file_router)
    app.include_router(refresh_router)

    if include_ui:
        # Static files & UI
        app.mount("/static", StaticFiles(directory="static"), name="static")
        app.include_router(chatbot_router)

        @app.get("/", summary="Web UI")
        async def serve_ui():
            return FileResponse("static/index.html")

    @app.get("/api", summary="API Status")
    async def read_root():
        return {"status": "ok", "message": "Excel Refresh API is running"}

    return app


# Default app instance (for uvicorn main:app)
app = create_app(include_ui=True)


def show_startup_menu() -> str:
    """시작 메뉴 표시"""
    print("\n" + "="*50)
    print("       Excel Refresh Manager")
    print("="*50)
    print("실행 모드를 선택하세요:")
    print()
    print("  1. API 서버 (UI 없음, API만 제공)")
    print("  2. 터미널 모드 (CLI 인터페이스)")
    print("  3. 웹 UI 모드 (브라우저에서 사용)")
    print()
    print("  0. 종료")
    print("="*50)
    return input("선택: ").strip()


if __name__ == "__main__":
    import uvicorn

    choice = show_startup_menu()

    if choice == "1":
        print("\nAPI 서버를 시작합니다...")
        print("API 문서: http://127.0.0.1:8000/docs")
        api_only_app = create_app(include_ui=False)
        uvicorn.run(api_only_app, host="127.0.0.1", port=8000)

    elif choice == "2":
        print("\n터미널 모드를 시작합니다...")
        from src.cli.terminal import run
        run()

    elif choice == "3":
        print("\n웹 UI 서버를 시작합니다...")
        print("브라우저에서 http://127.0.0.1:8000 접속하세요")
        uvicorn.run(app, host="127.0.0.1", port=8000)

    elif choice == "0":
        print("프로그램을 종료합니다.")
    else:
        print("잘못된 선택입니다. 프로그램을 종료합니다.")
