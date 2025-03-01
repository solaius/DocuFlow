from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4

from .base import TableExtractor
from .models.table import Table, TableDetectionMethod


class TableExtractionService:
    """Service for coordinating table extraction from documents."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._extractors: Dict[TableDetectionMethod, TableExtractor] = {}

    def register_extractor(self, method: TableDetectionMethod, extractor: TableExtractor):
        """Register a table extractor implementation."""
        self._extractors[method] = extractor
        self.logger.info(f"Registered table extractor for method: {method}")

    async def extract_tables(
        self,
        document_id: str,
        parsed_content: Dict[str, Any],
        preferred_method: Optional[TableDetectionMethod] = None,
        **kwargs
    ) -> List[Table]:
        """
        Extract tables from a parsed document using available extractors.

        Args:
            document_id: Unique identifier of the document
            parsed_content: Parsed document content from IBM Docling
            preferred_method: Preferred extraction method to use
            **kwargs: Additional extraction parameters

        Returns:
            List of extracted tables

        Raises:
            ValueError: If no suitable extractor is available
        """
        if not self._extractors:
            raise ValueError("No table extractors registered")

        # Use preferred method if specified and available
        if preferred_method and preferred_method in self._extractors:
            extractor = self._extractors[preferred_method]
            tables = await extractor.extract_tables(
                document_id, parsed_content, **kwargs
            )
            return await self._validate_tables(tables, extractor)

        # Try AI-driven first, then rule-based, and merge results
        tables = []
        ai_tables = []
        rule_based_tables = []

        # Try AI-driven extraction first
        if TableDetectionMethod.AI_DRIVEN in self._extractors:
            try:
                extractor = self._extractors[TableDetectionMethod.AI_DRIVEN]
                ai_tables = await extractor.extract_tables(
                    document_id, parsed_content, **kwargs
                )
                ai_tables = await self._validate_tables(ai_tables, extractor)
            except Exception as e:
                self.logger.error(f"Error during AI-driven extraction: {str(e)}")
                # AI extraction failed, continue to rule-based

        # If AI extraction failed or found no tables, try rule-based
        if (not ai_tables) and TableDetectionMethod.RULE_BASED in self._extractors:
            try:
                extractor = self._extractors[TableDetectionMethod.RULE_BASED]
                rule_based_tables = await extractor.extract_tables(
                    document_id, parsed_content, **kwargs
                )
                rule_based_tables = await self._validate_tables(rule_based_tables, extractor)
            except Exception as e:
                self.logger.error(f"Error during rule-based extraction: {str(e)}")

        # Merge results, preferring AI-driven results when there's overlap
        try:
            tables = await self._merge_table_results(ai_tables, rule_based_tables)
        except Exception as e:
            self.logger.error(f"Error merging table results: {str(e)}")
            # On merge error, return whatever results we have
            tables = ai_tables + rule_based_tables

        return tables

    async def _merge_table_results(
        self,
        ai_tables: List[Table],
        rule_based_tables: List[Table]
    ) -> List[Table]:
        """
        Merge results from both extractors, handling overlaps.
        
        Strategy:
        1. Keep all AI tables with high confidence
        2. Add rule-based tables that don't overlap with AI tables
        3. For overlapping regions, keep the one with higher confidence
        """
        if not rule_based_tables:
            return ai_tables
        if not ai_tables:
            return rule_based_tables

        merged_tables = []
        used_regions = set()

        # Add all high-confidence AI tables
        for table in ai_tables:
            if table.confidence_score >= 0.8:
                merged_tables.append(table)
                if table.bbox:
                    used_regions.add(self._bbox_to_key(table.bbox))

        # Process remaining tables
        remaining_ai = [t for t in ai_tables if t.confidence_score < 0.8]
        all_remaining = remaining_ai + rule_based_tables

        # Sort by confidence score
        all_remaining.sort(key=lambda t: t.confidence_score, reverse=True)

        for table in all_remaining:
            if not table.bbox:
                merged_tables.append(table)
                continue

            bbox_key = self._bbox_to_key(table.bbox)
            if bbox_key not in used_regions and not self._has_overlap(table, merged_tables):
                merged_tables.append(table)
                used_regions.add(bbox_key)

        return merged_tables

    def _bbox_to_key(self, bbox: List[float]) -> str:
        """Convert bbox to string key for comparison."""
        return f"{int(bbox[0])},{int(bbox[1])},{int(bbox[2])},{int(bbox[3])}"

    def _has_overlap(self, table: Table, existing_tables: List[Table]) -> bool:
        """Check if table overlaps with any existing tables."""
        if not table.bbox:
            return False

        for existing in existing_tables:
            if not existing.bbox:
                continue

            # Check for overlap
            if (table.bbox[0] < existing.bbox[2] and
                table.bbox[2] > existing.bbox[0] and
                table.bbox[1] < existing.bbox[3] and
                table.bbox[3] > existing.bbox[1]):
                return True

        return False

    async def _validate_tables(
        self, tables: List[Table], extractor: TableExtractor
    ) -> List[Table]:
        """Validate extracted tables and filter out invalid ones."""
        validated_tables = []
        for table in tables:
            try:
                if await extractor.validate_table(table):
                    validated_tables.append(table)
                else:
                    self.logger.warning(
                        f"Table validation failed for table {table.id} "
                        f"in document {table.document_id}"
                    )
            except Exception as e:
                self.logger.error(
                    f"Error validating table {table.id}: {str(e)}"
                )

        return validated_tables