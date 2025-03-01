from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

def create_simple_grid_table():
    """1. Simple Grid Table"""
    data = [
        ['Header 1', 'Header 2', 'Header 3'],
        ['Row 1, Col 1', 'Row 1, Col 2', 'Row 1, Col 3'],
        ['Row 2, Col 1', 'Row 2, Col 2', 'Row 2, Col 3'],
        ['Row 3, Col 1', 'Row 3, Col 2', 'Row 3, Col 3']
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return table

def create_merged_cells_table():
    """2. Merged Cells Table"""
    data = [
        ['Merged Header Spanning Three Columns', '', ''],
        ['Column 1', 'Column 2', 'Column 3'],
        ['Row 1', 'Merged Cells', ''],
        ['Row 2', '1', '2'],
        ['Spanning\nTwo Rows', '3', '4'],
        ['', '5', '6']
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Merge cells in first row
        ('SPAN', (0, 0), (2, 0)),
        # Merge cells in third row
        ('SPAN', (1, 2), (2, 2)),
        # Merge cells in last two rows
        ('SPAN', (0, 4), (0, 5)),
        # Headers
        ('BACKGROUND', (0, 0), (-1, 1), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
        # Cell alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return table

def create_header_footer_table():
    """3. Table with Headers and Footers"""
    data = [
        ['Department', 'Q1 Sales', 'Q2 Sales', 'Q3 Sales', 'Q4 Sales'],
        ['Electronics', '10,000', '12,000', '15,000', '18,000'],
        ['Clothing', '8,000', '9,000', '11,000', '14,000'],
        ['Books', '5,000', '5,500', '6,000', '7,500'],
        ['TOTAL', '23,000', '26,500', '32,000', '39,500']
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        # Footer style
        ('BACKGROUND', (0, -1), (-1, -1), colors.grey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Align numbers right
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ]))
    return table

def create_basic_tables_pdf(output_path="basic_tables.pdf"):
    """Create PDF with all basic table types"""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    
    # Create story
    story = []
    
    # 1. Simple Grid Table
    story.append(Paragraph("1. Simple Grid Table", title_style))
    story.append(Spacer(1, 12))
    story.append(create_simple_grid_table())
    story.append(Spacer(1, 30))
    
    # 2. Merged Cells Table
    story.append(Paragraph("2. Merged Cells Table", title_style))
    story.append(Spacer(1, 12))
    story.append(create_merged_cells_table())
    story.append(Spacer(1, 30))
    
    # 3. Headers and Footers Table
    story.append(Paragraph("3. Table with Headers and Footers", title_style))
    story.append(Spacer(1, 12))
    story.append(create_header_footer_table())
    
    # Build the document
    doc.build(story)

if __name__ == '__main__':
    create_basic_tables_pdf("test_files/basic_tables.pdf")