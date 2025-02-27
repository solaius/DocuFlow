from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ...ingestion.service import IngestionService
from ...models.document import Document
from docuflow.config.config import settings

router = APIRouter()
ingestion_service = IngestionService(settings.UPLOAD_DIR, settings.PROCESSED_DIR)


@router.post("/upload", response_model=Document)
async def upload_document(file: UploadFile = File(...)) -> Document:
    """
    Upload a document for processing.
    
    Args:
        file: The file to upload
        
    Returns:
        Document: Document metadata
    """
    try:
        document = await ingestion_service.ingest_file(file)
        return document
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str) -> Document:
    """
    Get document metadata by ID.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document: Document metadata
    """
    document = ingestion_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document