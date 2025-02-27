from uuid import UUID

import pytest

from docuflow.models.document import Document, DocumentStatus, DocumentType


def test_document_creation():
    """Test creating a document with minimal required fields."""
    doc = Document(
        filename="test.pdf",
        file_type=DocumentType.PDF,
        file_path="/path/to/test.pdf"
    )
    
    assert isinstance(doc.id, UUID)
    assert doc.filename == "test.pdf"
    assert doc.file_type == DocumentType.PDF
    assert doc.status == DocumentStatus.PENDING
    assert doc.file_path == "/path/to/test.pdf"
    assert doc.processed_path is None
    assert doc.error_message is None
    assert isinstance(doc.metadata, dict)
    assert len(doc.metadata) == 0


def test_document_type_enum():
    """Test DocumentType enum values."""
    assert DocumentType.PDF == "pdf"
    assert DocumentType.DOCX == "docx"
    assert DocumentType.IMAGE == "image"
    assert DocumentType.HTML == "html"
    assert DocumentType.UNKNOWN == "unknown"


def test_document_status_enum():
    """Test DocumentStatus enum values."""
    assert DocumentStatus.PENDING == "pending"
    assert DocumentStatus.PROCESSING == "processing"
    assert DocumentStatus.PROCESSED == "processed"
    assert DocumentStatus.FAILED == "failed"


def test_document_serialization():
    """Test document serialization to dict."""
    doc = Document(
        filename="test.pdf",
        file_type=DocumentType.PDF,
        file_path="/path/to/test.pdf",
        metadata={"pages": 5}
    )
    
    doc_dict = doc.model_dump()
    assert isinstance(doc_dict, dict)
    assert doc_dict["filename"] == "test.pdf"
    assert doc_dict["file_type"] == "pdf"
    assert doc_dict["status"] == "pending"
    assert doc_dict["file_path"] == "/path/to/test.pdf"
    assert doc_dict["metadata"] == {"pages": 5}