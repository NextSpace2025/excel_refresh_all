from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from contextlib import asynccontextmanager
from src.api.models import FilePathWithId, FilePath, RefreshSettings
from src.api import routes
from src.database import db_manager

# --- Event Handlers ---
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Ensure the database and table exist on application startup."""
    db_manager.create_table_if_not_exists()
    print("FastAPI server started. Database is ready.")
    yield

# --- App Setup ---
app = FastAPI(
    title="Excel Refresh API",
    description="An API to manage a list of Excel files and trigger a refresh process.",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- API Endpoints ---

@app.get("/", summary="Web UI")
async def serve_ui():
    return FileResponse("static/index.html")

@app.get("/api", summary="API Status")
async def read_root():
    return await routes.read_root()

@app.get("/files", response_model=List[FilePathWithId], summary="List All Files")
async def get_files():
    return await routes.get_files()

@app.post("/files", summary="Add a New File")
async def add_file(file: FilePath):
    return await routes.add_file(file)

@app.put("/files/{file_id}", summary="Update a File Path")
async def update_file(file_id: int, file: FilePath):
    return await routes.update_file(file_id, file)

@app.delete("/files/{file_id}", summary="Delete a File")
async def delete_file(file_id: int):
    return await routes.delete_file(file_id)

@app.get("/settings", response_model=RefreshSettings, summary="Get Current Settings")
async def get_settings():
    return await routes.get_settings()

@app.post("/settings", summary="Update Settings")
async def update_settings(new_settings: RefreshSettings):
    return await routes.update_settings(new_settings)

@app.post("/run-refresh", summary="Run the Excel Refresh Process")
async def run_refresh():
    return await routes.run_refresh()

@app.post("/init-db", summary="Initialize Database")
async def init_database():
    return await routes.init_database()

# To run this server:ㅇ
# 1. Install dependencies: pip install -r requirements.txt
# 2. Start the server: uvicorn main:app --reload
# 3. Open your browser to http://127.0.0.1:8000/docs