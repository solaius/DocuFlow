from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def create_simple_pdf():
    # Create PDF
    doc = SimpleDocTemplate(
        "test_files/simple_table.pdf",
        pagesize=letter,
        invariant=True,
        compress=False
    )
    
    # Create a simple table
    data = [
        ['Name', 'Age'],
        ['John', '30'],
        ['Jane', '25']
    ]
    
    # Create table with basic style
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    # Build the document
    doc.build([table])

if __name__ == '__main__':
    create_simple_pdf()