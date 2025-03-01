from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_sample_pdf():
    # Ensure test_files directory exists
    from pathlib import Path
    Path("test_files").mkdir(exist_ok=True)
    
    # Create PDF with better compatibility settings
    doc = SimpleDocTemplate(
        "test_files/sample_tables.pdf",
        pagesize=letter,
        invariant=True,  # Ensure consistent output
        compress=False   # Avoid compression issues
    )
    
    # Create story for the document
    story = []
    styles = getSampleStyleSheet()
    
    # Add a simple table
    story.append(Paragraph("Table 1: Simple Data Table", styles['Heading1']))
    data = [
        ['Name', 'Age', 'City'],
        ['John Doe', '30', 'New York'],
        ['Jane Smith', '25', 'London'],
        ['Bob Johnson', '35', 'Paris']
    ]
    table = Table(data)
    table.setStyle(TableStyle([
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
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Add a complex table with merged cells
    story.append(Paragraph("Table 2: Sales Report (with merged cells)", styles['Heading1']))
    data = [
        ['Region', 'Q1', 'Q2', 'Q3', 'Q4', 'Total'],
        ['North', '100', '120', '130', '140', '490'],
        ['South', '110', '130', '140', '150', '530'],
        ['East', '120', '140', '150', '160', '570'],
        ['West', '130', '150', '160', '170', '610'],
        ['Total', '460', '540', '580', '620', '2200']
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.grey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Add a table with irregular structure
    story.append(Paragraph("Table 3: Product Catalog", styles['Heading1']))
    data = [
        ['Category', 'Product', 'Price', 'Stock'],
        ['Electronics', 'Laptop', '$999', '50'],
        ['', 'Smartphone', '$599', '100'],
        ['', 'Tablet', '$399', '75'],
        ['Clothing', 'T-Shirt', '$29', '200'],
        ['', 'Jeans', '$59', '150'],
        ['Books', 'Python Guide', '$49', '80'],
        ['', 'ML Handbook', '$79', '60']
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
    ]))
    story.append(table)
    
    # Build the document
    doc.build(story)

if __name__ == '__main__':
    create_sample_pdf()