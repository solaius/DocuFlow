import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

from docuflow.models.document import Document, DocumentStatus, DocumentType
from docuflow.parsing.service import DocumentParsingService


@pytest.fixture(scope="session")
def test_files_dir():
    """Create and manage test files directory."""
    test_dir = Path("/workspace/DocuFlow/tests/test_files")
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def sample_image(test_files_dir):
    """Create a test image with some text and shapes."""
    image_path = test_files_dir / "test_image.png"
    
    # Create a simple image with text and shapes
    img = Image.new('RGB', (800, 600), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Add some shapes
    draw.rectangle([100, 100, 300, 200], outline='black', width=2)
    draw.ellipse([400, 100, 600, 200], outline='blue', width=2)
    draw.line([100, 300, 700, 300], fill='red', width=3)
    
    # Add text
    draw.text((50, 50), "Test Image Content", fill='black', size=24)
    draw.text((50, 400), "Sample Text", fill='blue', size=18)
    
    # Save with high quality
    img.save(image_path, quality=95, optimize=True)
    
    yield image_path
    
    if image_path.exists():
        os.remove(image_path)


@pytest.fixture
def complex_pdf(test_files_dir, sample_image):
    """Create a complex PDF with tables, images, and formatted text."""
    pdf_path = test_files_dir / "complex_test.pdf"
    
    # Create PDF with multiple elements
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Prepare styles
    styles = getSampleStyleSheet()
    
    # Build content
    story = []
    
    # Add title
    story.append(Paragraph("Complex Test Document", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Add some text with formatting
    story.append(Paragraph("This is a test document with various elements:", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Add a code block
    code_text = '''def example_function():
    print("This is a code block")
    return True'''
    story.append(Paragraph("Code Example:", styles['Heading2']))
    story.append(Paragraph(f"<code>{code_text}</code>", styles['Code']))
    story.append(Spacer(1, 12))
    
    # Add a table
    table_data = [
        ['Header 1', 'Header 2', 'Header 3'],
        ['Row 1', '123', 'abc'],
        ['Row 2', '456', 'def'],
        ['Row 3', '789', 'ghi']
    ]
    table = Table(table_data)
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    story.append(Paragraph("Sample Table:", styles['Heading2']))
    story.append(table)
    story.append(Spacer(1, 12))
    
    # Add an image
    img = RLImage(str(sample_image), width=4*inch, height=3*inch)
    story.append(Paragraph("Sample Image:", styles['Heading2']))
    story.append(img)
    story.append(Spacer(1, 12))
    
    # Add another image to ensure multiple images are handled
    img2 = RLImage(str(sample_image), width=3*inch, height=2*inch)
    story.append(Paragraph("Another Image:", styles['Heading2']))
    story.append(img2)
    story.append(Spacer(1, 12))
    
    # Add a formula
    story.append(Paragraph("Sample Formula:", styles['Heading2']))
    story.append(Paragraph("E = mc<sup>2</sup>", styles['Normal']))
    story.append(Paragraph("Another formula: x<sup>2</sup> + y<sup>2</sup> = r<sup>2</sup>", styles['Normal']))
    
    # Build the PDF
    doc.build(story)
    
    yield pdf_path
    
    if pdf_path.exists():
        os.remove(pdf_path)


@pytest.fixture
def parsing_service():
    """Create a DocumentParsingService instance."""
    return DocumentParsingService()


@pytest.mark.asyncio
async def test_simple_text_parsing(test_files_dir):
    """Test parsing a simple PDF with just text."""
    # Create a simple PDF
    pdf_path = test_files_dir / "simple_test.pdf"
    c = SimpleDocTemplate(str(pdf_path))
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("Simple Test Document", styles['Title']))
    story.append(Paragraph("This is a test PDF file.", styles['Normal']))
    c.build(story)
    
    # Create document and parse
    doc = Document(
        filename="simple_test.pdf",
        file_type=DocumentType.PDF,
        file_path=str(pdf_path)
    )
    
    parsing_service = DocumentParsingService()
    result = await parsing_service.parse_document(doc, pdf_path)
    
    # Verify results
    assert result.status == DocumentStatus.PROCESSED
    assert result.content is not None
    assert "Simple Test Document" in result.content
    assert result.metadata["num_pages"] == 1
    assert not result.metadata["has_tables"]
    assert not result.metadata["has_images"]
    assert not result.metadata["has_code"]
    assert not result.metadata["has_formulas"]
    assert isinstance(result.metadata["processing_time"], str)
    
    # Cleanup
    os.remove(pdf_path)


@pytest.mark.asyncio
async def test_complex_document_parsing(complex_pdf, parsing_service):
    """Test parsing a complex PDF with tables, images, and code."""
    # Create document
    doc = Document(
        filename="complex_test.pdf",
        file_type=DocumentType.PDF,
        file_path=str(complex_pdf)
    )
    
    # Parse document
    result = await parsing_service.parse_document(doc, complex_pdf)
    
    # Verify basic results
    assert result.status == DocumentStatus.PROCESSED
    assert result.content is not None
    assert result.error is None
    
    # Check metadata
    assert result.metadata["num_pages"] >= 1
    assert result.metadata["has_tables"]
    assert result.metadata["has_images"]
    assert result.metadata["has_code"]
    assert result.metadata["has_formulas"]
    
    # Check table extraction
    assert "tables" in result.metadata
    tables = result.metadata["tables"]
    assert len(tables) > 0
    table = tables[0]
    assert "headers" in table
    assert "Header 1" in table["headers"]
    assert "num_rows" in table
    assert table["num_rows"] >= 4  # Header + 3 data rows
    assert "bbox" in table
    
    # Check image extraction
    assert "images" in result.metadata
    images = result.metadata["images"]
    assert len(images) > 0
    image = images[0]
    assert "page" in image
    assert "bbox" in image
    
    # Check processing time
    assert "processing_time" in result.metadata
    processing_time = datetime.fromisoformat(result.metadata["processing_time"])
    assert isinstance(processing_time, datetime)
    assert processing_time.tzinfo == UTC


@pytest.mark.asyncio
async def test_image_document_parsing(sample_image, parsing_service):
    """Test parsing an image document."""
    # Create document
    doc = Document(
        filename="test_image.png",
        file_type=DocumentType.IMAGE,
        file_path=str(sample_image)
    )
    
    # Parse document
    result = await parsing_service.parse_document(doc, sample_image)
    
    # Verify results
    assert result.status == DocumentStatus.PROCESSED
    assert result.content is not None
    assert result.metadata["num_pages"] == 1
    assert not result.metadata["has_tables"]
    assert result.metadata["has_images"]
    assert not result.metadata["has_code"]
    
    # Check image metadata
    assert "images" in result.metadata
    images = result.metadata["images"]
    assert len(images) == 1
    image = images[0]
    assert "page" in image
    assert "bbox" in image
    assert "captions" in image


@pytest.mark.asyncio
async def test_error_handling(test_files_dir, parsing_service):
    """Test error handling with invalid files."""
    # Create an invalid PDF file
    invalid_pdf = test_files_dir / "invalid.pdf"
    with open(invalid_pdf, "w") as f:
        f.write("This is not a valid PDF file")
    
    # Create document
    doc = Document(
        filename="invalid.pdf",
        file_type=DocumentType.PDF,
        file_path=str(invalid_pdf)
    )
    
    # Parse document
    result = await parsing_service.parse_document(doc, invalid_pdf)
    
    # Verify error handling
    assert result.status == DocumentStatus.FAILED
    assert result.error is not None
    assert "failed" in result.error.lower()
    
    # Cleanup
    os.remove(invalid_pdf)


@pytest.mark.asyncio
async def test_partial_success_handling(complex_pdf, parsing_service):
    """Test handling of partial success cases."""
    # Create a corrupted PDF by truncating it
    corrupted_pdf = complex_pdf.parent / "corrupted.pdf"
    shutil.copy(complex_pdf, corrupted_pdf)
    with open(corrupted_pdf, "r+b") as f:
        # Get file size
        f.seek(0, 2)  # Seek to end
        size = f.tell()
        # Truncate to half size
        f.truncate(size // 2)
    
    # Create document
    doc = Document(
        filename="corrupted.pdf",
        file_type=DocumentType.PDF,
        file_path=str(corrupted_pdf)
    )
    
    # Parse document
    result = await parsing_service.parse_document(doc, corrupted_pdf)
    
    # Verify partial success handling
    assert result.status in [DocumentStatus.PROCESSED, DocumentStatus.FAILED]
    if result.status == DocumentStatus.PROCESSED:
        assert result.content is not None
        assert result.metadata is not None
        assert result.error is not None  # Should have warning about partial success
    else:
        assert result.error is not None
    
    # Cleanup
    os.remove(corrupted_pdf)