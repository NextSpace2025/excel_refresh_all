from fastapi import APIRouter
from src.api.models import RefreshSettings
from src.api import routes

router = APIRouter(tags=["Refresh"])


@router.get("/settings", response_model=RefreshSettings, summary="Get Current Settings")
async def get_settings():
    return await routes.get_settings()


@router.post("/settings", summary="Update Settings")
async def update_settings(new_settings: RefreshSettings):
    return await routes.update_settings(new_settings)


@router.post("/run-refresh", summary="Run the Excel Refresh Process")
async def run_refresh():
    return await routes.run_refresh()


@router.post("/init-db", summary="Initialize Database")
async def init_database():
    return await routes.init_database()
