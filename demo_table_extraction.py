import asyncio
from pathlib import Path
import json
from typing import Dict, Any

from docling.document_converter import DocumentConverter
from rich.console import Console
from rich.table import Table as RichTable
from rich import print as rprint

from docuflow.table_extraction.service import TableExtractionService
from docuflow.table_extraction.ai_driven import DoclingTableExtractor
from docuflow.table_extraction.rule_based import RuleBasedTableExtractor
from docuflow.table_extraction.models.table import Table, TableDetectionMethod

console = Console()

def process_document(file_path: str) -> Dict[str, Any]:
    """Process document using Docling and return parsed content."""
    try:
        # Initialize converter
        converter = DocumentConverter()
        console.print(f"[yellow]Converting {file_path}...")
        
        # Get absolute path
        path = Path(file_path).absolute()
        console.print(f"[yellow]Full path: {path}")
        
        # Convert the document
        doc = converter.convert(str(path))
        
        # Convert to dict and log structure
        result = doc.to_dict()
        console.print("[green]Document converted successfully")
        console.print(f"Document structure: {list(result.keys())}")
        
        # Log page details
        if "pages" in result:
            for i, page in enumerate(result["pages"], 1):
                console.print(f"\nPage {i} elements:")
                if "layout" in page:
                    elements = page["layout"].get("elements", [])
                    element_types = set(e.get("type") for e in elements)
                    console.print(f"  Types: {element_types}")
                    tables = [e for e in elements if e.get("type") == "table"]
                    if tables:
                        console.print(f"  Found {len(tables)} tables")
        
        return result
        
    except Exception as e:
        console.print(f"[red]Error in document conversion: {str(e)}")
        import traceback
        console.print("[red]" + traceback.format_exc())
        raise

def display_table(table: Table):
    """Display a table using rich formatting."""
    # Create header
    console.print(f"\n[bold blue]Table {table.id}[/bold blue]")
    console.print(f"Page: {table.page_number}")
    console.print(f"Method: {table.detection_method.value}")
    console.print(f"Confidence: {table.confidence_score:.2f}")
    if table.caption:
        console.print(f"Caption: {table.caption}")
    console.print(f"Size: {table.num_rows} rows × {table.num_cols} columns")

    # Create rich table
    rich_table = RichTable(
        title=f"Content ({table.num_rows}×{table.num_cols})",
        show_header=True,
        header_style="bold magenta"
    )

    # Get headers and data rows
    headers = []
    data = [[None for _ in range(table.num_cols)] for _ in range(table.num_rows)]
    
    for cell in table.cells:
        data[cell.row][cell.col] = cell.text
        if cell.is_header:
            headers.append(cell.text)

    # If no explicit headers found, use first row
    if not headers:
        headers = data[0]
        data = data[1:]

    # Add columns
    for header in headers:
        rich_table.add_column(header or "")

    # Add rows
    for row in data:
        rich_table.add_row(*[str(cell or "") for cell in row])

    console.print(rich_table)

    # Show metadata
    if table.metadata:
        console.print("\n[bold]Metadata:[/bold]")
        console.print(json.dumps(table.metadata, indent=2))

def main():
    # Initialize services
    service = TableExtractionService()
    service.register_extractor(TableDetectionMethod.AI_DRIVEN, DoclingTableExtractor())
    service.register_extractor(TableDetectionMethod.RULE_BASED, RuleBasedTableExtractor())

    # Process each test file
    test_files_dir = Path("test_files")
    for file_path in test_files_dir.glob("*.pdf"):
        console.rule(f"[bold green]Processing {file_path.name}")
        
        try:
            # Process document
            parsed_content = process_document(str(file_path))
            
            # Extract tables
            tables = service.extract_tables(
                document_id=file_path.stem,
                parsed_content=parsed_content
            )
            
            # Display results
            console.print(f"\nFound {len(tables)} tables:")
            for table in tables:
                display_table(table)
                
        except Exception as e:
            console.print(f"[bold red]Error processing {file_path.name}:[/bold red] {str(e)}")

if __name__ == "__main__":
    main()