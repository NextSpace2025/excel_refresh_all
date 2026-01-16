from fastapi import APIRouter
from typing import List
from src.api.models import FilePathWithId, FilePath
from src.api import routes

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("", response_model=List[FilePathWithId], summary="List All Files")
async def get_files():
    return await routes.get_files()


@router.post("", summary="Add a New File")
async def add_file(file: FilePath):
    return await routes.add_file(file)


@router.put("/{file_id}", summary="Update a File Path")
async def update_file(file_id: int, file: FilePath):
    return await routes.update_file(file_id, file)


@router.delete("/{file_id}", summary="Delete a File")
async def delete_file(file_id: int):
    return await routes.delete_file(file_id)
