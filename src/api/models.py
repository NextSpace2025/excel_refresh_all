from pydantic import BaseModel
from typing import List


class FilePath(BaseModel):
    path: str


class FilePathWithId(BaseModel):
    id: int
    file_path: str


class RefreshSettings(BaseModel):
    refresh_delay: int = 10
    inter_file_delay: int = 5
