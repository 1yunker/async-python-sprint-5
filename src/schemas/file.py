from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileUpload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    path: str
    size: int


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    path: str
    size: int
    is_downloadable: bool


class UserFilesResponse(BaseModel):
    account_id: int
    files: list[FileResponse]
