from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    IMAGE = "image"
    HTML = "html"
    UNKNOWN = "unknown"


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    file_type: DocumentType
    status: DocumentStatus = DocumentStatus.PENDING
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    process_time: Optional[datetime] = None
    error_message: Optional[str] = None
    file_path: str
    processed_path: Optional[str] = None
    metadata: dict = Field(default_factory=dict)