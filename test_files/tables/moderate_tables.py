from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime

def create_multi_level_headers_table():
    """4. Multi-Level Column Headers Table"""
    data = [
        ['Product Category', 'Electronics', '', '', 'Clothing', '', ''],
        ['Subcategory', 'Laptops', 'Phones', 'Tablets', 'Shirts', 'Pants', 'Jackets'],
        ['Q1 Sales', '5000', '3000', '2000', '1500', '2000', '3500'],
        ['Q2 Sales', '5500', '3200', '2100', '1200', '1800', '2500'],
        ['Q3 Sales', '6000', '3500', '2300', '2000', '2200', '3000'],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        # Merge cells in first row
        ('SPAN', (1, 0), (3, 0)),  # Electronics
        ('SPAN', (4, 0), (6, 0)),  # Clothing
        # Header styles
        ('BACKGROUND', (0, 0), (-1, 1), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
        # Align numbers right
        ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
    ]))
    return table

def create_hierarchical_table():
    """5. Hierarchical/Nested Tables"""
    # Create sub-tables for departments
    dev_data = [
        ['Development Team'],
        ['Frontend', '3 devs'],
        ['Backend', '4 devs'],
        ['DevOps', '2 devs'],
    ]
    dev_table = Table(dev_data)
    dev_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('SPAN', (0, 0), (1, 0)),
    ]))
    
    sales_data = [
        ['Sales Team'],
        ['US Region', '5 reps'],
        ['EU Region', '4 reps'],
        ['APAC', '3 reps'],
    ]
    sales_table = Table(sales_data)
    sales_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('SPAN', (0, 0), (1, 0)),
    ]))
    
    # Main table containing sub-tables
    data = [
        ['Department', 'Structure'],
        ['Development', dev_table],
        ['Sales', sales_table],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]))
    return table

def create_mixed_data_table():
    """6. Table with Mixed Data Types"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    
    data = [
        ['Product', 'Price', 'Launch Date', 'Rating', 'Status'],
        ['Super Laptop', '$999.99', date_str, '★★★★☆', 'In Stock'],
        ['Ultra Phone', '$599.99', '2023-12-01', '★★★★★', 'Pre-order'],
        ['Mega Tablet', '$299.99', '2023-10-15', '★★★☆☆', 'Out of Stock'],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        # Price column right-aligned
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        # Center align dates and ratings
        ('ALIGN', (2, 0), (3, -1), 'CENTER'),
        # Color-code status
        ('TEXTCOLOR', (-1, 1), (-1, 1), colors.green),  # In Stock
        ('TEXTCOLOR', (-1, 2), (-1, 2), colors.blue),   # Pre-order
        ('TEXTCOLOR', (-1, 3), (-1, 3), colors.red),    # Out of Stock
    ]))
    return table

def create_empty_cells_table():
    """7. Table with Empty/Missing Cells"""
    data = [
        ['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        ['9:00', 'Meeting', '', 'Workshop', '', 'Review'],
        ['10:00', '', 'Training', '', 'Meeting', ''],
        ['11:00', 'Workshop', '', '', 'Training', 'Meeting'],
        ['12:00', 'Lunch', 'Lunch', 'Lunch', 'Lunch', 'Lunch'],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),  # Header row
        ('BACKGROUND', (0, 0), (0, -1), colors.blue),  # Time column
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        # Highlight lunch row
        ('BACKGROUND', (1, -1), (-1, -1), colors.lightgrey),
    ]))
    return table

def create_irregular_sizes_table():
    """8. Table with Irregular Column Widths & Row Heights"""
    data = [
        ['Subject', 'Monday Schedule', 'Room'],
        ['Mathematics\n(Double Period)', 'Morning Session\n9:00 - 10:30', '101'],
        ['History', 'Mid-Morning\n11:00 - 11:45', '202'],
        ['Science Lab\n(Triple Period)', 'Afternoon Session\n1:00 - 3:15\nLab Work & Theory', '301'],
    ]
    
    # Set custom column widths
    col_widths = [1.5*inch, 2.5*inch, 1.0*inch]
    table = Table(data, colWidths=col_widths)
    
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Add some row colors
        ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
        ('BACKGROUND', (0, 3), (-1, 3), colors.lightgrey),
    ]))
    return table

def create_moderate_tables_pdf(output_path="moderate_tables.pdf"):
    """Create PDF with all moderate complexity table types"""
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
    
    # 4. Multi-Level Headers Table
    story.append(Paragraph("4. Multi-Level Headers Table", title_style))
    story.append(Spacer(1, 12))
    story.append(create_multi_level_headers_table())
    story.append(Spacer(1, 30))
    
    # 5. Hierarchical/Nested Table
    story.append(Paragraph("5. Hierarchical/Nested Table", title_style))
    story.append(Spacer(1, 12))
    story.append(create_hierarchical_table())
    story.append(Spacer(1, 30))
    
    # 6. Mixed Data Types Table
    story.append(Paragraph("6. Mixed Data Types Table", title_style))
    story.append(Spacer(1, 12))
    story.append(create_mixed_data_table())
    story.append(Spacer(1, 30))
    
    # 7. Empty Cells Table
    story.append(Paragraph("7. Table with Empty Cells", title_style))
    story.append(Spacer(1, 12))
    story.append(create_empty_cells_table())
    story.append(Spacer(1, 30))
    
    # 8. Irregular Sizes Table
    story.append(Paragraph("8. Table with Irregular Sizes", title_style))
    story.append(Spacer(1, 12))
    story.append(create_irregular_sizes_table())
    
    # Build the document
    doc.build(story)

if __name__ == '__main__':
    create_moderate_tables_pdf("test_files/moderate_tables.pdf")