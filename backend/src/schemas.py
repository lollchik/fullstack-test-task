from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class FileItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    original_name: str
    mime_type: str
    size: int
    processing_status: str
    scan_status: str | None
    scan_details: str | None
    metadata_json: dict | None
    requires_attention: bool
    created_at: datetime
    updated_at: datetime


class FileUpdate(BaseModel):
    title: str


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    file_id: UUID
    level: str
    message: str
    created_at: datetime
