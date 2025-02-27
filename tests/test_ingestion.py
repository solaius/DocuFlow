import os
from pathlib import Path

import pytest
from fastapi import UploadFile

from docuflow.ingestion.service import IngestionService

from docuflow.models.document import DocumentType


@pytest.mark.asyncio
async def test_ingest_pdf(ingestion_service, sample_pdf):
    """Test ingesting a PDF file."""
    # Create an UploadFile instance
    with open(sample_pdf, "rb") as f:
        upload_file = UploadFile(
            filename=os.path.basename(sample_pdf),
            file=f
        )
        
        # Test ingestion
        doc = await ingestion_service.ingest_file(upload_file)
        
        # Verify document metadata
        assert doc.filename == os.path.basename(sample_pdf)
        assert doc.file_type == DocumentType.PDF
        assert os.path.exists(doc.file_path)
        assert doc.processed_path is None


@pytest.mark.asyncio
async def test_ingest_docx(ingestion_service, sample_docx):
    """Test ingesting a DOCX file."""
    # Create an UploadFile instance
    with open(sample_docx, "rb") as f:
        upload_file = UploadFile(
            filename=os.path.basename(sample_docx),
            file=f
        )
        
        # Test ingestion
        doc = await ingestion_service.ingest_file(upload_file)
        
        # Verify document metadata
        assert doc.filename == os.path.basename(sample_docx)
        assert doc.file_type == DocumentType.DOCX
        assert os.path.exists(doc.file_path)
        assert doc.processed_path is None


def test_directory_creation(temp_dir):
    """Test that the service creates required directories."""
    upload_dir = Path(temp_dir) / "test_upload"
    processed_dir = Path(temp_dir) / "test_processed"
    
    # Create service instance
    service = IngestionService(str(upload_dir), str(processed_dir))
    
    # Check directories were created
    assert upload_dir.exists()
    assert upload_dir.is_dir()
    assert processed_dir.exists()
    assert processed_dir.is_dir()