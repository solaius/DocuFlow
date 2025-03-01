import pathlib
from docuflow.models.document import Document, DocumentType
from docuflow.parsing.service import DocumentParsingService
import asyncio
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table

def create_test_image(image_path):
    """Create a test image with text and shapes."""
    img = Image.new('RGB', (800, 600), color='white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Add some shapes
    draw.rectangle([100, 100, 300, 200], outline='black', width=2)
    draw.ellipse([400, 100, 600, 200], outline='blue', width=2)
    draw.line([100, 300, 700, 300], fill='red', width=3)
    
    # Add text
    draw.text((50, 50), "Test Image Content", fill='black')
    draw.text((50, 400), "Sample Text", fill='blue')
    
    # Save with high quality
    img.save(image_path, quality=95, optimize=True)
    return image_path

def create_test_pdf(pdf_path, image_path):
    """Create a test PDF with various elements."""
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    story.append(Paragraph("Test Document", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Add text
    story.append(Paragraph("This is a test document with various elements:", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Add code block
    code_text = '''def example_function():
    print("This is a code block")
    return True'''
    story.append(Paragraph("Code Example:", styles['Heading2']))
    story.append(Paragraph(f"<code>{code_text}</code>", styles['Code']))
    story.append(Spacer(1, 12))
    
    # Add table
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
    
    # Add image
    img = RLImage(str(image_path), width=4*inch, height=3*inch)
    story.append(Paragraph("Sample Image:", styles['Heading2']))
    story.append(img)
    story.append(Spacer(1, 12))
    
    # Add formula
    story.append(Paragraph("Sample Formula:", styles['Heading2']))
    story.append(Paragraph("E = mc<sup>2</sup>", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return pdf_path

async def main():
    # Create test directory
    test_dir = pathlib.Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create test files
    image_path = test_dir / "test_image.png"
    pdf_path = test_dir / "Alstom - Wikipedia.pdf"

    # Generate test files
    create_test_image(image_path)
    #create_test_pdf(pdf_path, image_path)
    
    # Create document object
    doc = Document(
        filename="Alstom - Wikipedia.pdf",
        file_type=DocumentType.PDF,
        file_path=str(pdf_path)
    )
    
    # Create parsing service and parse document
    service = DocumentParsingService()
    result = await service.parse_document(doc, pdf_path)
    
    # Print results
    print("\nDocument Status:", result.status)
    print("\nExtracted Content:")
    print(result.content)
    print("\nMetadata:")
    for key, value in result.metadata.items():
        print(f"{key}:")
        if isinstance(value, list):
            for item in value:
                print(f"  - {item}")
        else:
            print(f"  {value}")
    
    if result.error:
        print("\nErrors:")
        print(result.error)

if __name__ == "__main__":
    asyncio.run(main())