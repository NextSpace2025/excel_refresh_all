import os
import json
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .ocr_processor import OnDeviceOCR
from .lmstudio_client import LMStudioClient
from .data_loader import ExcelToDBLoader

# 전역 인스턴스 초기화
ocr_engine = OnDeviceOCR(gpu=False)
lm_client = LMStudioClient()
db_loader = ExcelToDBLoader("chatbot_data.db")

# 세션별 대화 기록 저장
conversation_sessions: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    use_data: bool = True

class ExcelLoadRequest(BaseModel):
    file_path: str
    sheet_name: Optional[str] = None
    table_name: Optional[str] = None

class LMStudioConfigRequest(BaseModel):
    base_url: str
    model: Optional[str] = "local-model"

class SQLQueryRequest(BaseModel):
    question: str
    table_name: Optional[str] = None

class OCRProcessRequest(BaseModel):
    file_path: str
    max_length: int = 30

class OCRBatchRequest(BaseModel):
    folder_path: str
    max_length: int = 30
    log_filename: str = "ocr_batch_process.log"

# --- 챗봇 및 데이터 관련 함수 ---

async def check_lmstudio_status():
    """LM Studio 연결 상태 확인"""
    return lm_client.check_connection()

async def configure_lmstudio(config: LMStudioConfigRequest):
    """LM Studio 설정 변경"""
    lm_client.base_url = config.base_url.rstrip("/")
    if config.model:
        lm_client.model = config.model
    return {"status": "success", "base_url": lm_client.base_url, "model": lm_client.model}

async def load_excel(request: ExcelLoadRequest):
    """엑셀 파일을 DB로 로드"""
    try:
        result = db_loader.load_excel_to_db(
            request.file_path, 
            request.sheet_name, 
            request.table_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_loaded_data():
    """로드된 파일 목록 조회"""
    return {"files": db_loader.get_loaded_files()}

async def get_table_data(table_name: str, limit: int = 100):
    """테이블 데이터 조회"""
    return db_loader.query_table(table_name, limit)

async def get_table_summary(table_name: str):
    """테이블 요약 정보 조회"""
    return db_loader.get_data_summary(table_name)

async def search_data(query: str, table_name: Optional[str] = None):
    """데이터 검색"""
    return db_loader.search_data(query, table_name)

async def chat(request: ChatRequest):
    """챗봇 대화 수행"""
    context = ""
    data_used = []

    if request.use_data:
        # 간단한 키워드 기반 데이터 검색을 컨텍스트로 활용
        search_results = db_loader.search_data(request.message)
        if search_results:
            context = json.dumps(search_results[:5], ensure_ascii=False)
            data_used = search_results[:5]

    history = conversation_sessions.get(request.session_id, [])
    response = lm_client.chat(
        request.message, 
        context=context, 
        conversation_history=history
    )

    if response["status"] == "success":
        # 대화 기록 업데이트
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": response["message"]})
        conversation_sessions[request.session_id] = history[-10:]  # 최근 10개 유지

    return {
        "response": response.get("message", "응답을 생성할 수 없습니다."),
        "data_used": data_used,
        "status": response["status"]
    }

async def clear_session(session_id: str):
    """대화 세션 초기화"""
    conversation_sessions[session_id] = []
    return {"status": "success", "message": f"Session {session_id} cleared"}

async def ask_with_sql(request: SQLQueryRequest):
    """자연어 질문을 SQL로 변환하여 실행"""
    # 테이블 스키마 정보 수집
    files = db_loader.get_loaded_files()
    table_info = ""
    for f in files:
        if not request.table_name or f['table_name'] == request.table_name:
            summary = db_loader.get_data_summary(f['table_name'])
            table_info += f"Table: {f['table_name']}, Columns: {[c['name'] for c in summary['columns']]}\n"

    sql_res = lm_client.generate_sql_query(request.question, table_info)
    if sql_res["status"] == "success":
        data = db_loader.execute_sql(sql_res["sql"])
        return {"sql": sql_res["sql"], "data": data}
    else:
        raise HTTPException(status_code=500, detail="SQL 생성 실패")

# --- OCR 관련 함수 ---

async def process_single_ocr(request: OCRProcessRequest):
    """단일 파일 OCR 및 이름 변경"""
    try:
        new_path = ocr_engine.organize_file_by_ocr(request.file_path, request.max_length)
        return {
            "status": "success",
            "original_path": request.file_path,
            "new_path": new_path,
            "filename": os.path.basename(new_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_batch_ocr(request: OCRBatchRequest):
    """폴더 단위 배치 OCR 처리"""
    try:
        ocr_engine.batch_organize_images(request.folder_path, request.max_length, request.log_filename)
        log_path = os.path.join(request.folder_path, request.log_filename)
        return {"status": "success", "message": "배치 작업 완료", "log_path": log_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_ocr_to_excel(request: OCRProcessRequest):
    """OCR 수행 후 패턴을 추출하여 엑셀로 저장"""
    try:
        # 1. 텍스트 추출 및 필터링 (신뢰도 0.6 이상)
        results = ocr_engine.extract_filtered_text(request.file_path, min_confidence=0.6)
        
        # 2. 엑셀 파일 경로 생성 (원본파일명_extracted.xlsx)
        base_path = os.path.splitext(request.file_path)[0]
        excel_path = f"{base_path}_extracted.xlsx"
        
        # 3. 패턴 추출 및 엑셀 저장
        ocr_engine.save_to_excel(results, excel_path)
        
        return {"status": "success", "excel_path": excel_path, "data_count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def get_local_image(path: str):
    """로컬 이미지 파일을 미리보기용으로 반환"""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="이미지 파일을 찾을 수 없습니다.")
    # 보안을 위해 이미지 확장자 체크 등을 추가할 수 있습니다.
    return FileResponse(path)
