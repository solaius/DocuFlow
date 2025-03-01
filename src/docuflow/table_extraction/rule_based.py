from typing import List, Dict, Any, Tuple, Optional
import logging
from uuid import uuid4

from .base import TableExtractor
from .models.table import Table, TableCell, TableDetectionMethod


class RuleBasedTableExtractor(TableExtractor):
    """Rule-based table extractor using layout analysis and heuristics."""

    def __init__(self, min_confidence_threshold: float = 0.6):
        self.logger = logging.getLogger(__name__)
        self.min_confidence_threshold = min_confidence_threshold

    async def extract_tables(
        self,
        document_id: str,
        parsed_content: Dict[str, Any],
        **kwargs
    ) -> List[Table]:
        """
        Extract tables using rule-based methods.

        Args:
            document_id: Unique identifier of the document
            parsed_content: Parsed document content from IBM Docling
            **kwargs: Additional extraction parameters

        Returns:
            List of extracted tables
        """
        tables = []
        try:
            # Process each page
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
        """Extract tables from a single page using rule-based methods."""
        tables = []
        
        # Find potential table regions using layout analysis
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
        Find potential table regions using rule-based layout analysis.
        
        This method looks for:
        1. Grid-like arrangements of text blocks
        2. Consistent horizontal/vertical alignments
        3. Regular spacing patterns
        4. Line segments that might indicate table borders
        """
        regions = []
        layout = page_content.get("layout", {})
        
        # Get all text blocks and their positions
        text_blocks = self._get_text_blocks(layout)
        if not text_blocks:
            return regions

        # Group blocks by vertical position (potential rows)
        rows = self._group_blocks_into_rows(text_blocks)
        
        # Analyze each group of rows for table-like characteristics
        current_region = []
        for row in rows:
            if self._is_potential_table_row(row):
                current_region.append(row)
            elif current_region:
                # End of potential table region
                if len(current_region) >= 2:  # Minimum 2 rows for a table
                    region = self._create_region_from_rows(current_region)
                    regions.append(region)
                current_region = []

        # Handle last region
        if current_region and len(current_region) >= 2:
            region = self._create_region_from_rows(current_region)
            regions.append(region)

        return regions

    def _get_text_blocks(self, layout: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and normalize text blocks from layout."""
        blocks = []
        for element in layout.get("elements", []):
            if element.get("type") == "text":
                # Skip if it looks like a caption
                text = element.get("text", "").strip().lower()
                if text.startswith("table ") and ":" in text:
                    continue
                    
                # Extract text and position information
                text_info = {
                    "text": element.get("text", ""),
                    "bbox": element.get("bbox", [0, 0, 0, 0]),
                    "font": element.get("font"),
                    "font_size": element.get("font_size")
                }
                blocks.append(text_info)
        return sorted(blocks, key=lambda x: (x["bbox"][1], x["bbox"][0]))

    def _group_blocks_into_rows(
        self,
        blocks: List[Dict[str, Any]],
        y_tolerance: float = 5.0
    ) -> List[List[Dict[str, Any]]]:
        """Group blocks into rows based on vertical position."""
        if not blocks:
            return []

        # Sort blocks by y-coordinate
        sorted_blocks = sorted(blocks, key=lambda b: b["bbox"][1])
        
        rows = []
        current_row = [sorted_blocks[0]]
        current_y = sorted_blocks[0]["bbox"][1]

        for block in sorted_blocks[1:]:
            block_y = block["bbox"][1]
            if abs(block_y - current_y) <= y_tolerance:
                current_row.append(block)
            else:
                rows.append(current_row)
                current_row = [block]
                current_y = block_y

        if current_row:
            rows.append(current_row)

        return rows

    def _is_potential_table_row(
        self,
        row: List[Dict[str, Any]],
        min_cells: int = 2,
        max_variance: float = 0.2
    ) -> bool:
        """
        Check if a row of blocks might be part of a table.
        
        Criteria:
        1. Minimum number of cells
        2. Regular horizontal spacing
        3. Similar text lengths
        4. Consistent formatting
        """
        if len(row) < min_cells:
            return False

        # Check horizontal spacing regularity
        spaces = []
        for i in range(len(row) - 1):
            space = row[i + 1]["bbox"][0] - row[i]["bbox"][2]
            spaces.append(space)

        if not spaces:
            return False

        # Calculate spacing variance
        avg_space = sum(spaces) / len(spaces)
        variance = sum((s - avg_space) ** 2 for s in spaces) / len(spaces)
        if variance / avg_space > max_variance:
            return False

        # Check formatting consistency
        fonts = set(block.get("font") for block in row)
        font_sizes = set(block.get("font_size") for block in row)
        
        # Allow some variation in formatting
        return len(fonts) <= 2 and len(font_sizes) <= 2

    def _create_region_from_rows(
        self,
        rows: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Create a table region from grouped rows."""
        # Calculate region boundaries
        min_x = min(block["bbox"][0] for row in rows for block in row)
        max_x = max(block["bbox"][2] for row in rows for block in row)
        min_y = min(block["bbox"][1] for row in rows for block in row)
        max_y = max(block["bbox"][3] for row in rows for block in row)

        return {
            "type": "table",
            "bbox": [min_x, min_y, max_x, max_y],
            "rows": rows,
            "confidence": self._calculate_region_confidence(rows)
        }

    def _calculate_region_confidence(
        self,
        rows: List[List[Dict[str, Any]]]
    ) -> float:
        """
        Calculate confidence score for a table region.
        
        Factors considered:
        1. Number of rows and columns
        2. Alignment consistency
        3. Formatting patterns
        4. Content patterns
        """
        if not rows:
            return 0.0

        factors = [
            self._calculate_structure_confidence(rows),
            self._calculate_alignment_confidence(rows),
            self._calculate_format_confidence(rows),
            self._calculate_content_confidence(rows)
        ]
        
        return sum(factors) / len(factors)

    def _calculate_structure_confidence(
        self,
        rows: List[List[Dict[str, Any]]]
    ) -> float:
        """Calculate confidence based on structural regularity."""
        if not rows:
            return 0.0

        # Check row length consistency
        row_lengths = [len(row) for row in rows]
        if not row_lengths:
            return 0.0

        avg_length = sum(row_lengths) / len(row_lengths)
        if avg_length < 2:  # Require at least 2 columns
            return 0.0

        # Calculate variance in row lengths
        variance = sum((l - avg_length) ** 2 for l in row_lengths) / len(row_lengths)
        
        # Higher confidence for consistent row lengths
        return max(0.0, 1.0 - (variance / avg_length))

    def _calculate_alignment_confidence(
        self,
        rows: List[List[Dict[str, Any]]]
    ) -> float:
        """Calculate confidence based on alignment consistency."""
        if not rows:
            return 0.0

        # Get column x-positions for each row
        col_positions = []
        for row in rows:
            positions = [block["bbox"][0] for block in row]
            col_positions.append(positions)

        # Calculate alignment consistency
        if not col_positions:
            return 0.0

        reference_pos = col_positions[0]
        alignment_scores = []

        for pos in col_positions[1:]:
            if len(pos) != len(reference_pos):
                alignment_scores.append(0.0)
                continue

            # Calculate position differences
            diffs = [abs(p - r) for p, r in zip(pos, reference_pos)]
            avg_diff = sum(diffs) / len(diffs)
            alignment_scores.append(max(0.0, 1.0 - (avg_diff / 50.0)))  # 50px tolerance

        return sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0

    def _calculate_format_confidence(
        self,
        rows: List[List[Dict[str, Any]]]
    ) -> float:
        """Calculate confidence based on formatting patterns."""
        if not rows:
            return 0.0

        # Analyze header formatting
        potential_header = rows[0]
        header_format = {
            "font": set(block.get("font") for block in potential_header),
            "font_size": set(block.get("font_size") for block in potential_header)
        }

        # Analyze body formatting
        body_format = {
            "font": set(block.get("font") for row in rows[1:] for block in row),
            "font_size": set(block.get("font_size") for row in rows[1:] for block in row)
        }

        # Higher confidence if header and body have distinct formatting
        format_diff_score = (
            (len(header_format["font"] - body_format["font"]) > 0) +
            (len(header_format["font_size"] - body_format["font_size"]) > 0)
        ) / 2.0

        # Higher confidence if body formatting is consistent
        body_consistency = (
            (len(body_format["font"]) <= 2) +
            (len(body_format["font_size"]) <= 2)
        ) / 2.0

        return (format_diff_score + body_consistency) / 2.0

    def _calculate_content_confidence(
        self,
        rows: List[List[Dict[str, Any]]]
    ) -> float:
        """Calculate confidence based on content patterns."""
        if not rows:
            return 0.0

        # Analyze content length patterns
        col_lengths = []
        for col_idx in range(len(rows[0])):
            col_content = []
            for row in rows:
                if col_idx < len(row):
                    col_content.append(len(row[col_idx].get("text", "")))
            if col_content:
                col_lengths.append(col_content)

        if not col_lengths:
            return 0.0

        # Calculate consistency within columns
        col_scores = []
        for lengths in col_lengths:
            if not lengths:
                continue
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            col_scores.append(max(0.0, 1.0 - (variance / (avg_length + 1))))

        return sum(col_scores) / len(col_scores) if col_scores else 0.0

    async def _process_table_region(
        self,
        document_id: str,
        page_num: int,
        region: Dict[str, Any],
        page_content: Dict[str, Any]
    ) -> Optional[Table]:
        """Process a table region into a structured Table object."""
        try:
            # Extract cells from rows
            cells, num_rows, num_cols = await self._extract_cells(region)
            
            if not cells:
                return None

            # Calculate confidence score
            confidence_score = region.get("confidence", 0.0)
            
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
                detection_method=TableDetectionMethod.RULE_BASED,
                confidence_score=confidence_score,
                bbox=region.get("bbox"),
                metadata={
                    "region_type": region.get("type"),
                    "processing_notes": "Extracted using rule-based analysis"
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
        """Extract cells from table region rows."""
        cells = []
        rows = region.get("rows", [])
        
        if not rows:
            return [], 0, 0

        num_rows = len(rows)
        num_cols = max(len(row) for row in rows)

        for row_idx, row in enumerate(rows):
            for col_idx, block in enumerate(row):
                cell = TableCell(
                    text=block.get("text", "").strip(),
                    row=row_idx,
                    col=col_idx,
                    is_header=row_idx == 0,  # Assume first row is header
                    confidence=0.8,  # Default confidence for rule-based extraction
                    metadata={
                        "font": block.get("font"),
                        "font_size": block.get("font_size"),
                        "bbox": block.get("bbox")
                    }
                )
                cells.append(cell)

        return cells, num_rows, num_cols

    def _extract_caption(
        self,
        region: Dict[str, Any],
        page_content: Dict[str, Any]
    ) -> Optional[str]:
        """Extract table caption if available."""
        bbox = region.get("bbox")
        if not bbox:
            return None

        # Look for caption-like text above or below the table
        for element in page_content.get("layout", {}).get("elements", []):
            if element.get("type") == "text":
                text = element.get("text", "").strip().lower()
                if text.startswith("table ") and len(text) < 200:
                    element_bbox = element.get("bbox")
                    if element_bbox and self._is_nearby(bbox, element_bbox):
                        return element.get("text")

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
            if table.num_rows < 2 or table.num_cols < 2:
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

            # Check for consistent column count and complete rows
            rows = {}
            for cell in table.cells:
                rows.setdefault(cell.row, []).append(cell)
            
            # Each row should have the expected number of columns
            if not all(len(row) == table.num_cols for row in rows.values()):
                return False

            # All rows from 0 to num_rows-1 should be present
            if set(rows.keys()) != set(range(table.num_rows)):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating table: {str(e)}")
            return False