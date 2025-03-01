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

        # Try AI-driven first, fall back to rule-based
        tables = []
        try:
            if TableDetectionMethod.AI_DRIVEN in self._extractors:
                extractor = self._extractors[TableDetectionMethod.AI_DRIVEN]
                tables = await extractor.extract_tables(
                    document_id, parsed_content, **kwargs
                )
                tables = await self._validate_tables(tables, extractor)

            # If AI method failed or found no tables, try rule-based
            if not tables and TableDetectionMethod.RULE_BASED in self._extractors:
                extractor = self._extractors[TableDetectionMethod.RULE_BASED]
                tables = await extractor.extract_tables(
                    document_id, parsed_content, **kwargs
                )
                tables = await self._validate_tables(tables, extractor)

        except Exception as e:
            self.logger.error(f"Error during table extraction: {str(e)}")
            # Fall back to rule-based if AI method fails
            if TableDetectionMethod.RULE_BASED in self._extractors:
                extractor = self._extractors[TableDetectionMethod.RULE_BASED]
                tables = await extractor.extract_tables(
                    document_id, parsed_content, **kwargs
                )
                tables = await self._validate_tables(tables, extractor)

        return tables

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