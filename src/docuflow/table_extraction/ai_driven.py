from typing import List, Dict, Any, Tuple, Optional
import logging
from uuid import uuid4

from .base import TableExtractor
from .models.table import Table, TableCell, TableDetectionMethod


class DoclingTableExtractor(TableExtractor):
    """AI-driven table extractor using IBM Docling's output."""

    def __init__(self, min_confidence_threshold: float = 0.7):
        self.logger = logging.getLogger(__name__)
        self.min_confidence_threshold = min_confidence_threshold

    async def extract_tables(
        self,
        document_id: str,
        parsed_content: Dict[str, Any],
        **kwargs
    ) -> List[Table]:
        """
        Extract tables from Docling's parsed content.

        Args:
            document_id: Unique identifier of the document
            parsed_content: Parsed document content from IBM Docling
            **kwargs: Additional extraction parameters

        Returns:
            List of extracted tables
        """
        tables = []
        try:
            # Extract tables from each page
            for page_num, page_content in enumerate(parsed_content.get("pages", []), 1):
                page_tables = await self._extract_page_tables(
                    document_id, page_num, page_content
                )
                tables.extend(page_tables)
        except Exception as e:
            self.logger.error(f"Error extracting tables: {str(e)}")
            raise

        return tables

    async def _extract_page_tables(
        self,
        document_id: str,
        page_num: int,
        page_content: Dict[str, Any]
    ) -> List[Table]:
        """Extract tables from a single page."""
        tables = []
        
        # Get table regions from Docling's layout analysis
        table_regions = self._find_table_regions(page_content)
        
        for region in table_regions:
            try:
                table = await self._process_table_region(
                    document_id, page_num, region, page_content
                )
                if table:
                    tables.append(table)
            except Exception as e:
                self.logger.warning(
                    f"Failed to process table in page {page_num}: {str(e)}"
                )

        return tables

    def _find_table_regions(self, page_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find table regions in Docling's page content.
        
        Docling typically marks tables with specific layout types or
        structural indicators in its output.
        """
        table_regions = []
        
        # Look for table indicators in layout analysis
        layout = page_content.get("layout", {})
        
        # Check for explicit table markers
        for element in layout.get("elements", []):
            if element.get("type") == "table":
                table_regions.append(element)
            # Also check for implicit tables (grid-like structures)
            elif self._is_implicit_table(element):
                table_regions.append(element)

        return table_regions

    def _is_implicit_table(self, element: Dict[str, Any]) -> bool:
        """
        Detect if an element represents an implicit table structure.
        
        This checks for grid-like arrangements of text blocks that
        might represent tables even if not explicitly marked as such.
        """
        # Check for grid-like alignment of text blocks
        if element.get("type") != "text":
            return False

        # Look for consistent column alignment
        blocks = element.get("blocks", [])
        if len(blocks) < 2:  # Need at least 2 rows for a table
            return False

        # Check for aligned columns
        col_positions = self._get_column_positions(blocks)
        return len(col_positions) > 1 and self._has_consistent_alignment(blocks, col_positions)

    def _get_column_positions(self, blocks: List[Dict[str, Any]]) -> List[float]:
        """Get unique x-positions that might represent columns."""
        positions = set()
        for block in blocks:
            for text in block.get("text", []):
                positions.add(text.get("x", 0))
        return sorted(positions)

    def _has_consistent_alignment(
        self,
        blocks: List[Dict[str, Any]],
        col_positions: List[float]
    ) -> bool:
        """Check if text blocks show consistent column alignment."""
        alignment_count = 0
        for block in blocks:
            block_positions = [text.get("x", 0) for text in block.get("text", [])]
            if any(abs(pos - col_pos) < 5 for pos in block_positions 
                  for col_pos in col_positions):
                alignment_count += 1
        
        return alignment_count / len(blocks) > 0.7  # 70% alignment threshold

    async def _process_table_region(
        self,
        document_id: str,
        page_num: int,
        region: Dict[str, Any],
        page_content: Dict[str, Any]
    ) -> Optional[Table]:
        """Process a table region into a structured Table object."""
        try:
            # Extract cells and determine table structure
            cells, num_rows, num_cols = await self._extract_cells(region)
            
            if not cells:
                return None

            # Calculate confidence score
            confidence_score = self._calculate_confidence(cells, region)
            
            if confidence_score < self.min_confidence_threshold:
                self.logger.debug(
                    f"Table confidence {confidence_score} below threshold "
                    f"{self.min_confidence_threshold}"
                )
                return None

            # Create table object
            table = Table(
                id=f"table-{document_id}-{page_num}-{uuid4().hex[:8]}",
                document_id=document_id,
                page_number=page_num,
                cells=cells,
                num_rows=num_rows,
                num_cols=num_cols,
                caption=self._extract_caption(region, page_content),
                detection_method=TableDetectionMethod.AI_DRIVEN,
                confidence_score=confidence_score,
                bbox=region.get("bbox"),
                metadata={
                    "region_type": region.get("type"),
                    "processing_notes": "Extracted using Docling AI"
                }
            )

            return table

        except Exception as e:
            self.logger.error(f"Error processing table region: {str(e)}")
            return None

    async def _extract_cells(
        self,
        region: Dict[str, Any]
    ) -> Tuple[List[TableCell], int, int]:
        """
        Extract cells from a table region.
        
        Returns:
            Tuple containing:
            - List of TableCell objects
            - Number of rows
            - Number of columns
        """
        cells = []
        max_row = 0
        max_col = 0

        # Process cells based on region type
        if region.get("type") == "table":
            # Handle explicit table structure
            for cell_data in region.get("cells", []):
                cell = self._process_cell(cell_data)
                if cell:
                    cells.append(cell)
                    max_row = max(max_row, cell.row + cell.rowspan)
                    max_col = max(max_col, cell.col + cell.colspan)
        else:
            # Handle implicit table structure
            cells, max_row, max_col = await self._process_implicit_table(region)

        return cells, max_row, max_col

    def _process_cell(self, cell_data: Dict[str, Any]) -> Optional[TableCell]:
        """Process a single cell from explicit table data."""
        try:
            return TableCell(
                text=cell_data.get("text", "").strip(),
                row=cell_data.get("row", 0),
                col=cell_data.get("col", 0),
                rowspan=cell_data.get("rowspan", 1),
                colspan=cell_data.get("colspan", 1),
                is_header=cell_data.get("is_header", False),
                confidence=cell_data.get("confidence", 1.0),
                metadata={
                    "font": cell_data.get("font"),
                    "font_size": cell_data.get("font_size"),
                    "style": cell_data.get("style", {})
                }
            )
        except Exception as e:
            self.logger.warning(f"Failed to process cell: {str(e)}")
            return None

    async def _process_implicit_table(
        self,
        region: Dict[str, Any]
    ) -> Tuple[List[TableCell], int, int]:
        """Process an implicit table structure from aligned text blocks."""
        cells = []
        row_positions = self._get_row_positions(region)
        col_positions = self._get_column_positions(region.get("blocks", []))
        
        for block in region.get("blocks", []):
            for text in block.get("text", []):
                row = self._get_position_index(text.get("y", 0), row_positions)
                col = self._get_position_index(text.get("x", 0), col_positions)
                
                cell = TableCell(
                    text=text.get("content", "").strip(),
                    row=row,
                    col=col,
                    is_header=row == 0,  # Assume first row is header
                    confidence=0.8,  # Lower confidence for implicit tables
                    metadata={
                        "font": text.get("font"),
                        "font_size": text.get("font_size")
                    }
                )
                cells.append(cell)

        return cells, len(row_positions), len(col_positions)

    def _get_row_positions(self, region: Dict[str, Any]) -> List[float]:
        """Get unique y-positions that might represent rows."""
        positions = set()
        for block in region.get("blocks", []):
            for text in block.get("text", []):
                positions.add(text.get("y", 0))
        return sorted(positions)

    def _get_position_index(self, position: float, positions: List[float]) -> int:
        """Get the index of the closest position in a list of positions."""
        for i, pos in enumerate(positions):
            if abs(position - pos) < 5:  # 5-pixel threshold
                return i
        return len(positions) - 1

    def _extract_caption(
        self,
        region: Dict[str, Any],
        page_content: Dict[str, Any]
    ) -> Optional[str]:
        """Extract table caption if available."""
        # Check for explicit caption
        caption = region.get("caption")
        if caption:
            return caption

        # Look for nearby text that might be a caption
        bbox = region.get("bbox")
        if not bbox:
            return None

        # Look for text blocks just above or below the table
        for block in page_content.get("layout", {}).get("elements", []):
            if block.get("type") == "text":
                text = block.get("text", "").strip().lower()
                if text.startswith("table ") and len(text) < 200:
                    block_bbox = block.get("bbox")
                    if block_bbox and self._is_nearby(bbox, block_bbox):
                        return block.get("text")

        return None

    def _is_nearby(
        self,
        table_bbox: List[float],
        text_bbox: List[float],
        threshold: float = 50
    ) -> bool:
        """Check if a text block is near the table."""
        return (abs(table_bbox[1] - text_bbox[3]) < threshold or  # Text above table
                abs(table_bbox[3] - text_bbox[1]) < threshold)    # Text below table

    def _calculate_confidence(
        self,
        cells: List[TableCell],
        region: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score for the table extraction."""
        if not cells:
            return 0.0

        factors = [
            self._calculate_structure_confidence(cells),
            self._calculate_content_confidence(cells),
            self._calculate_layout_confidence(region)
        ]
        
        return sum(factors) / len(factors)

    def _calculate_structure_confidence(self, cells: List[TableCell]) -> float:
        """Calculate confidence based on table structure."""
        # Check for consistent row/column structure
        rows = set(cell.row for cell in cells)
        cols = set(cell.col for cell in cells)
        
        # Perfect grid should have cells in every position
        expected_cells = len(rows) * len(cols)
        actual_cells = len(cells)
        
        return min(1.0, actual_cells / expected_cells)

    def _calculate_content_confidence(self, cells: List[TableCell]) -> float:
        """Calculate confidence based on cell content."""
        # Average of individual cell confidences
        return sum(cell.confidence for cell in cells) / len(cells)

    def _calculate_layout_confidence(self, region: Dict[str, Any]) -> float:
        """Calculate confidence based on layout analysis."""
        # Higher confidence for explicit tables
        if region.get("type") == "table":
            return 1.0
        
        # For implicit tables, check alignment quality
        blocks = region.get("blocks", [])
        col_positions = self._get_column_positions(blocks)
        if not col_positions:
            return 0.5
        
        alignment_score = sum(1 for block in blocks 
                            if self._has_consistent_alignment([block], col_positions))
        return min(1.0, alignment_score / len(blocks))

    async def validate_table(self, table: Table) -> bool:
        """
        Validate extracted table structure and content.

        Args:
            table: Table to validate

        Returns:
            True if table is valid, False otherwise
        """
        if not table.cells:
            return False

        try:
            # Check basic structure
            if table.num_rows < 1 or table.num_cols < 2:
                return False

            # Verify cell positions
            for cell in table.cells:
                if (cell.row < 0 or cell.row >= table.num_rows or
                    cell.col < 0 or cell.col >= table.num_cols):
                    return False

            # Check for minimum content
            non_empty_cells = sum(1 for cell in table.cells if cell.text.strip())
            if non_empty_cells / len(table.cells) < 0.5:  # Require 50% non-empty cells
                return False

            # Verify no overlapping cells
            if not self._verify_no_cell_overlap(table):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating table: {str(e)}")
            return False

    def _verify_no_cell_overlap(self, table: Table) -> bool:
        """Verify that no cells overlap in the table grid."""
        grid = [[False] * table.num_cols for _ in range(table.num_rows)]
        
        for cell in table.cells:
            for r in range(cell.row, cell.row + cell.rowspan):
                for c in range(cell.col, cell.col + cell.colspan):
                    if grid[r][c]:  # Cell position already occupied
                        return False
                    grid[r][c] = True
                    
        return True