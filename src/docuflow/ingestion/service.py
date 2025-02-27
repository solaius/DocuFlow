import magic
import os
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from ..models.document import Document, DocumentType


class IngestionService:
    def __init__(self, upload_dir: str, processed_dir: str):
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure upload and processed directories exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _detect_file_type(self, file_path: str) -> DocumentType:
        """Detect file type using python-magic."""
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        
        if mime_type == 'application/pdf':
            return DocumentType.PDF
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return DocumentType.DOCX
        elif mime_type.startswith('image/'):
            return DocumentType.IMAGE
        elif mime_type == 'text/html':
            return DocumentType.HTML
        
        # Try extension-based detection as fallback
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return DocumentType.PDF
        elif ext == '.docx':
            return DocumentType.DOCX
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return DocumentType.IMAGE
        elif ext in ['.html', '.htm']:
            return DocumentType.HTML
            
        return DocumentType.UNKNOWN

    async def ingest_file(self, file: UploadFile) -> Document:
        """
        Ingest a file into the system.
        
        Args:
            file: The uploaded file
            
        Returns:
            Document: Document metadata
        """
        # Save file to upload directory
        file_path = self.upload_dir / file.filename
        
        # Read file content and save
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create document metadata
        doc = Document(
            filename=file.filename,
            file_type=self._detect_file_type(str(file_path)),
            file_path=str(file_path),
            processed_path=None
        )
        
        return doc

    def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Get document metadata by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Optional[Document]: Document metadata if found
        """
        try:
            uuid_obj = UUID(doc_id)
            # In a real implementation, this would fetch from a database
            # For now, we'll return None to indicate document not found
            return None
        except ValueError:
            return None