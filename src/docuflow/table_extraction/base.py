from abc import ABC, abstractmethod
from typing import List, Dict, Any

from .models.table import Table


class TableExtractor(ABC):
    """Base class for table extraction implementations."""

    @abstractmethod
    async def extract_tables(
        self,
        document_id: str,
        parsed_content: Dict[str, Any],
        **kwargs
    ) -> List[Table]:
        """
        Extract tables from parsed document content.

        Args:
            document_id: Unique identifier of the document
            parsed_content: Parsed document content from IBM Docling
            **kwargs: Additional extraction parameters

        Returns:
            List of extracted tables
        """
        pass

    @abstractmethod
    async def validate_table(self, table: Table) -> bool:
        """
        Validate extracted table structure and content.

        Args:
            table: Table to validate

        Returns:
            True if table is valid, False otherwise
        """
        pass