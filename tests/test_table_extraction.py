import pytest
from unittest.mock import Mock, AsyncMock

from docuflow.table_extraction import (
    TableExtractionService,
    TableExtractor,
    Table,
    TableCell,
    TableDetectionMethod,
)


class MockTableExtractor(TableExtractor):
    """Mock implementation of TableExtractor for testing."""
    
    def __init__(self, tables_to_return=None, validation_result=True):
        self.tables_to_return = tables_to_return or []
        self.validation_result = validation_result
        self.extract_tables_called = False
        self.validate_table_called = False

    async def extract_tables(self, document_id, parsed_content, **kwargs):
        self.extract_tables_called = True
        return self.tables_to_return

    async def validate_table(self, table):
        self.validate_table_called = True
        return self.validation_result


@pytest.fixture
def sample_table():
    """Create a sample table for testing."""
    return Table(
        id="test-table-1",
        document_id="test-doc-1",
        page_number=1,
        cells=[
            TableCell(text="Header 1", row=0, col=0, is_header=True),
            TableCell(text="Header 2", row=0, col=1, is_header=True),
            TableCell(text="Data 1", row=1, col=0),
            TableCell(text="Data 2", row=1, col=1),
        ],
        num_rows=2,
        num_cols=2,
        detection_method=TableDetectionMethod.DOCLING_DRIVEN,
        confidence_score=0.95,
    )


@pytest.fixture
def table_service():
    """Create a TableExtractionService instance."""
    return TableExtractionService()


@pytest.mark.asyncio
async def test_register_extractor(table_service):
    """Test registering an extractor."""
    mock_extractor = MockTableExtractor()
    table_service.register_extractor(TableDetectionMethod.DOCLING_DRIVEN, mock_extractor)
    assert TableDetectionMethod.DOCLING_DRIVEN in table_service._extractors


@pytest.mark.asyncio
async def test_extract_tables_docling_driven(table_service, sample_table):
    """Test table extraction using Docling-driven method."""
    mock_extractor = MockTableExtractor(tables_to_return=[sample_table])
    table_service.register_extractor(TableDetectionMethod.DOCLING_DRIVEN, mock_extractor)

    tables = await table_service.extract_tables(
        "test-doc-1",
        {"content": "test content"},
        preferred_method=TableDetectionMethod.DOCLING_DRIVEN
    )

    assert len(tables) == 1
    assert tables[0].id == sample_table.id
    assert mock_extractor.extract_tables_called
    assert mock_extractor.validate_table_called


@pytest.mark.asyncio
async def test_extract_tables_fallback(table_service, sample_table):
    """Test fallback to rule-based extraction when AI fails."""
    # AI extractor that raises an exception
    ai_extractor = MockTableExtractor()
    ai_extractor.extract_tables = AsyncMock(side_effect=Exception("AI failed"))

    # Rule-based extractor that works
    rule_extractor = MockTableExtractor(tables_to_return=[sample_table])

    table_service.register_extractor(TableDetectionMethod.DOCLING_DRIVEN, ai_extractor)
    table_service.register_extractor(TableDetectionMethod.RULE_BASED, rule_extractor)

    tables = await table_service.extract_tables("test-doc-1", {"content": "test content"})

    assert len(tables) == 1
    assert tables[0].id == sample_table.id
    assert rule_extractor.extract_tables_called


@pytest.mark.asyncio
async def test_validate_tables(table_service, sample_table):
    """Test table validation filtering."""
    # Create extractor that fails validation
    mock_extractor = MockTableExtractor(
        tables_to_return=[sample_table],
        validation_result=False
    )
    table_service.register_extractor(TableDetectionMethod.DOCLING_DRIVEN, mock_extractor)

    tables = await table_service.extract_tables(
        "test-doc-1",
        {"content": "test content"},
        preferred_method=TableDetectionMethod.DOCLING_DRIVEN
    )

    assert len(tables) == 0  # All tables should be filtered out due to validation failure


@pytest.mark.asyncio
async def test_table_to_markdown(sample_table):
    """Test converting table to markdown format."""
    markdown = sample_table.to_markdown()
    expected = (
        "| Header 1 | Header 2 |\n"
        "|---|---|\n"
        "| Data 1 | Data 2 |"
    )
    assert markdown.strip() == expected.strip()


@pytest.mark.asyncio
async def test_table_to_dict_format(sample_table):
    """Test converting table to 2D list format."""
    grid = sample_table.to_dict_format()
    expected = [
        ["Header 1", "Header 2"],
        ["Data 1", "Data 2"]
    ]
    assert grid == expected