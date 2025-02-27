import os
import pytest
from pathlib import Path

from docuflow.models.document import Document, DocumentStatus, DocumentType
from docuflow.parsing.service import DocumentParsingService


@pytest.fixture
def sample_pdf():
    # Create a temporary test PDF file
    test_dir = Path("/workspace/DocuFlow/tests/test_files")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = test_dir / "test.pdf"
    # Create a simple PDF for testing
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "Test Document")
    c.drawString(100, 700, "This is a test PDF file.")
    c.save()
    
    yield pdf_path
    
    # Cleanup
    if pdf_path.exists():
        os.remove(pdf_path)
    if test_dir.exists():
        test_dir.rmdir()


@pytest.mark.asyncio
async def test_document_parsing(sample_pdf):
    # Create a test document
    doc = Document(
        filename="test.pdf",
        file_type=DocumentType.PDF,
        file_path=str(sample_pdf)
    )
    
    # Initialize parsing service
    parsing_service = DocumentParsingService()
    
    # Parse document
    result = await parsing_service.parse_document(doc, sample_pdf)
    
    # Check results
    print(f"Error: {result.error}")
    assert result.status == DocumentStatus.PROCESSED
    assert result.content is not None
    assert "Test Document" in result.content
    assert result.metadata["num_pages"] == 1
    assert not result.metadata["has_tables"]  # Our test PDF has no tables
    assert not result.metadata["has_images"]  # Our test PDF has no images
    assert not result.metadata["has_code"]  # Our test PDF has no code blocks