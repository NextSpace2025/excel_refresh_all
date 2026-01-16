"""
챗봇 API Router
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
from typing import Optional

from . import chatbot_routes
from .chatbot_routes import (
    ChatRequest,
    ExcelLoadRequest,
    LMStudioConfigRequest,
    SQLQueryRequest,
    OCRProcessRequest,
    OCRBatchRequest
)

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


@router.get("", summary="Chatbot UI")
async def serve_chatbot_ui():
    return FileResponse("static/chatbot.html")


@router.get("/ocr-ui", summary="OCR Management UI")
async def serve_ocr_ui():
    return FileResponse("static/ocr.html")

@router.get("/status", summary="Check LM Studio Status")
async def chatbot_status():
    return await chatbot_routes.check_lmstudio_status()


@router.post("/config", summary="Configure LM Studio")
async def chatbot_config(config: LMStudioConfigRequest):
    return await chatbot_routes.configure_lmstudio(config)


@router.post("/load-excel", summary="Load Excel to DB")
async def chatbot_load_excel(request: ExcelLoadRequest):
    return await chatbot_routes.load_excel(request)


@router.get("/data", summary="Get Loaded Data")
async def chatbot_get_data():
    return await chatbot_routes.get_loaded_data()


@router.get("/data/{table_name}", summary="Get Table Data")
async def chatbot_get_table_data(table_name: str, limit: int = 100):
    return await chatbot_routes.get_table_data(table_name, limit)


@router.get("/data/{table_name}/summary", summary="Get Table Summary")
async def chatbot_get_table_summary(table_name: str):
    return await chatbot_routes.get_table_summary(table_name)


@router.get("/search", summary="Search Data")
async def chatbot_search(query: str, table_name: Optional[str] = None):
    return await chatbot_routes.search_data(query, table_name)


@router.post("/chat", summary="Chat with Bot")
async def chatbot_chat(request: ChatRequest):
    return await chatbot_routes.chat(request)


@router.post("/clear-session", summary="Clear Chat Session")
async def chatbot_clear_session(session_id: str = "default"):
    return await chatbot_routes.clear_session(session_id)


@router.post("/ask-sql", summary="Ask with SQL Generation")
async def chatbot_ask_sql(request: SQLQueryRequest):
    return await chatbot_routes.ask_with_sql(request)


@router.post("/ocr/process", summary="Process Single OCR")
async def chatbot_ocr_process(request: OCRProcessRequest):
    return await chatbot_routes.process_single_ocr(request)


@router.post("/ocr/to-excel", summary="Process OCR and Save to Excel with Patterns")
async def chatbot_ocr_to_excel(request: OCRProcessRequest):
    return await chatbot_routes.process_ocr_to_excel(request)


@router.post("/ocr/batch", summary="Process Batch OCR")
async def chatbot_ocr_batch(request: OCRBatchRequest):
    return await chatbot_routes.process_batch_ocr(request)


@router.get("/ocr/image", summary="Get Local Image for Preview")
async def chatbot_ocr_image(path: str):
    return await chatbot_routes.get_local_image(path)
