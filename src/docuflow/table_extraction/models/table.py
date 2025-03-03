from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TableDetectionMethod(Enum):
    DOCLING_DRIVEN = "docling_driven"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"


class TableCell(BaseModel):
    text: str = Field(description="Raw text content of the cell")
    row: int = Field(description="Row index (0-based)")
    col: int = Field(description="Column index (0-based)")
    rowspan: int = Field(default=1, description="Number of rows this cell spans")
    colspan: int = Field(default=1, description="Number of columns this cell spans")
    is_header: bool = Field(default=False, description="Whether this cell is a header")
    confidence: float = Field(
        default=1.0, 
        description="Confidence score of the extraction (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the cell (e.g., formatting, data type)"
    )


class Table(BaseModel):
    id: str = Field(description="Unique identifier for the table")
    document_id: str = Field(description="ID of the document containing this table")
    page_number: int = Field(description="Page number where the table appears")
    cells: List[TableCell] = Field(description="List of cells in the table")
    num_rows: int = Field(description="Total number of rows")
    num_cols: int = Field(description="Total number of columns")
    caption: Optional[str] = Field(
        default=None, 
        description="Table caption or title if available"
    )
    detection_method: TableDetectionMethod = Field(
        description="Method used to detect and extract the table"
    )
    confidence_score: float = Field(
        description="Overall confidence score for the table extraction",
        ge=0.0,
        le=1.0
    )
    bbox: Optional[List[float]] = Field(
        default=None,
        description="Bounding box coordinates [x1, y1, x2, y2] normalized to page dimensions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the table"
    )

    def to_dict_format(self) -> List[List[str]]:
        """Convert the table to a 2D list format."""
        # Initialize empty grid
        grid = [['' for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        
        # Fill in cells
        for cell in self.cells:
            grid[cell.row][cell.col] = cell.text
            
        return grid

    def to_markdown(self) -> str:
        """Convert the table to markdown format."""
        if not self.cells:
            return ""

        # Get the grid representation
        grid = self.to_dict_format()
        
        # Find header row if any
        header_row = next(
            (cell.row for cell in self.cells if cell.is_header),
            0  # Default to first row if no explicit headers
        )

        # Convert to markdown
        md_lines = []
        
        # Add caption if exists
        if self.caption:
            md_lines.append(f"**{self.caption}**\n")

        # Process rows
        for i, row in enumerate(grid):
            md_lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
            
            # Add separator after header
            if i == header_row:
                md_lines.append("|" + "|".join("---" for _ in row) + "|")

        return "\n".join(md_lines)