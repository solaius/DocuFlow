import logging
from pathlib import Path
from docling.document_converter import DocumentConverter
from rich.console import Console
from rich.pretty import pprint

def inspect_object(obj, console, indent="", max_depth=3, current_depth=0):
    """Recursively inspect an object's attributes."""
    if current_depth >= max_depth:
        return
        
    for attr_name in dir(obj):
        if attr_name.startswith('_'):
            continue
            
        try:
            attr = getattr(obj, attr_name)
            if callable(attr):
                continue
                
            console.print(f"{indent}{attr_name}: {type(attr)}")
            
            # Recursively inspect lists and custom objects
            if isinstance(attr, list) and attr:
                console.print(f"{indent}  First item type: {type(attr[0])}")
                if not isinstance(attr[0], (str, int, float, bool)):
                    inspect_object(attr[0], console, indent + "    ", max_depth, current_depth + 1)
            elif hasattr(attr, '__dict__') and not isinstance(attr, (str, int, float, bool)):
                inspect_object(attr, console, indent + "  ", max_depth, current_depth + 1)
                
        except Exception as e:
            console.print(f"{indent}{attr_name}: [red]Error accessing: {str(e)}[/red]")

def inspect_table(table, console, indent=""):
    """Inspect a table object."""
    console.print(f"{indent}Table:")
    
    # Show caption if available
    if table.captions:
        caption = table.captions[0]
        if hasattr(caption, 'text'):
            console.print(f"{indent}  Caption: {caption.text}")
    
    # Show table data
    if table.data:
        console.print(f"{indent}  Size: {table.data.num_rows}×{table.data.num_cols}")
        console.print(f"{indent}  Grid:")
        for row in table.data.grid:
            cells = [cell.text for cell in row]
            console.print(f"{indent}    {cells}")
        
        # Show cell details
        console.print(f"{indent}  Cells:")
        for cell in table.data.table_cells:
            row = cell.start_row_offset_idx
            col = cell.start_col_offset_idx
            console.print(f"{indent}    - {cell.text} ({row}, {col})")
    
    # Show position if available
    if table.prov:
        prov = table.prov[0]
        console.print(f"{indent}  Position: Page {prov.page_no}, {prov.bbox}")

def inspect_document(doc, console):
    """Inspect a document's tables."""
    console.print("\nDocument Information:")
    console.print(f"Number of pages: {len(doc.pages)}")
    
    # Show tables
    if doc.tables:
        console.print(f"\nFound {len(doc.tables)} tables:")
        for i, table in enumerate(doc.tables, 1):
            console.print(f"\nTable {i}:")
            inspect_table(table, console, "  ")

def process_pdf(pdf_path, console):
    """Process a single PDF file."""
    pdf_path = Path(pdf_path).absolute()
    console.rule(f"[bold]Processing {pdf_path.name}")
    console.print(f"File exists: {pdf_path.exists()}")
    console.print(f"File size: {pdf_path.stat().st_size} bytes")
    
    try:
        # Initialize converter
        converter = DocumentConverter()
        
        # Convert document
        console.print("\nAttempting conversion...")
        result = converter.convert(str(pdf_path))
        console.print("[green]Conversion successful!")
        
        # Show document content
        inspect_document(result.document, console)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}")
        import traceback
        console.print(traceback.format_exc())

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("docling")
    logger.setLevel(logging.DEBUG)
    
    console = Console()
    
    # Process basic tables
    process_pdf("test_files/basic_tables.pdf", console)
    
    # Process moderate tables
    process_pdf("test_files/moderate_tables.pdf", console)

if __name__ == "__main__":
    main()