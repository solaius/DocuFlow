import pytest
from typing import Dict, Any

from docuflow.table_extraction.rule_based import RuleBasedTableExtractor
from docuflow.table_extraction.models.table import TableDetectionMethod


@pytest.fixture
def rule_based_extractor():
    """Create a RuleBasedTableExtractor instance."""
    return RuleBasedTableExtractor()


@pytest.fixture
def sample_layout_content() -> Dict[str, Any]:
    """Create sample layout content with grid-like text blocks."""
    return {
        "pages": [{
            "layout": {
                "elements": [
                    {
                        "type": "text",
                        "text": "Table 1: Sample Data",
                        "bbox": [50, 20, 200, 40],
                        "font": "Arial",
                        "font_size": 12
                    },
                    {
                        "type": "text",
                        "text": "Name",
                        "bbox": [50, 50, 150, 70],
                        "font": "Arial-Bold",
                        "font_size": 11
                    },
                    {
                        "type": "text",
                        "text": "Age",
                        "bbox": [200, 50, 250, 70],
                        "font": "Arial-Bold",
                        "font_size": 11
                    },
                    {
                        "type": "text",
                        "text": "City",
                        "bbox": [300, 50, 400, 70],
                        "font": "Arial-Bold",
                        "font_size": 11
                    },
                    {
                        "type": "text",
                        "text": "John Doe",
                        "bbox": [50, 80, 150, 100],
                        "font": "Arial",
                        "font_size": 10
                    },
                    {
                        "type": "text",
                        "text": "30",
                        "bbox": [200, 80, 250, 100],
                        "font": "Arial",
                        "font_size": 10
                    },
                    {
                        "type": "text",
                        "text": "New York",
                        "bbox": [300, 80, 400, 100],
                        "font": "Arial",
                        "font_size": 10
                    },
                    {
                        "type": "text",
                        "text": "Jane Smith",
                        "bbox": [50, 110, 150, 130],
                        "font": "Arial",
                        "font_size": 10
                    },
                    {
                        "type": "text",
                        "text": "25",
                        "bbox": [200, 110, 250, 130],
                        "font": "Arial",
                        "font_size": 10
                    },
                    {
                        "type": "text",
                        "text": "London",
                        "bbox": [300, 110, 400, 130],
                        "font": "Arial",
                        "font_size": 10
                    }
                ]
            }
        }]
    }


@pytest.fixture
def irregular_layout_content() -> Dict[str, Any]:
    """Create sample layout content with irregular text blocks."""
    return {
        "pages": [{
            "layout": {
                "elements": [
                    {
                        "type": "text",
                        "text": "Random Text 1",
                        "bbox": [50, 50, 150, 70],
                        "font": "Arial",
                        "font_size": 10
                    },
                    {
                        "type": "text",
                        "text": "Random Text 2",
                        "bbox": [200, 60, 300, 80],
                        "font": "Times",
                        "font_size": 12
                    },
                    {
                        "type": "text",
                        "text": "Random Text 3",
                        "bbox": [100, 90, 200, 110],
                        "font": "Helvetica",
                        "font_size": 11
                    }
                ]
            }
        }]
    }


@pytest.mark.asyncio
async def test_extract_regular_table(rule_based_extractor, sample_layout_content):
    """Test extraction of regular grid-like table structure."""
    tables = await rule_based_extractor.extract_tables("test-doc", sample_layout_content)
    
    assert len(tables) == 1
    table = tables[0]
    
    assert table.document_id == "test-doc"
    assert table.page_number == 1
    assert table.num_rows == 3  # Header + 2 data rows
    assert table.num_cols == 3  # Name, Age, City
    assert table.detection_method == TableDetectionMethod.RULE_BASED
    assert table.confidence_score >= 0.7
    
    # Verify cells
    assert len(table.cells) == 9  # 3x3 grid
    headers = [cell for cell in table.cells if cell.is_header]
    assert len(headers) == 3
    assert "Name" in [h.text for h in headers]
    assert "Age" in [h.text for h in headers]
    assert "City" in [h.text for h in headers]


@pytest.mark.asyncio
async def test_irregular_layout(rule_based_extractor, irregular_layout_content):
    """Test handling of irregular layout that shouldn't be detected as a table."""
    tables = await rule_based_extractor.extract_tables("test-doc", irregular_layout_content)
    assert len(tables) == 0


@pytest.mark.asyncio
async def test_confidence_calculation(rule_based_extractor, sample_layout_content):
    """Test confidence score calculation for rule-based extraction."""
    tables = await rule_based_extractor.extract_tables("test-doc", sample_layout_content)
    assert len(tables) == 1
    
    table = tables[0]
    
    # Check confidence factors
    assert table.confidence_score >= 0.7  # High confidence for regular grid
    
    # Get the blocks for confidence calculation
    blocks = rule_based_extractor._get_text_blocks(
        sample_layout_content["pages"][0]["layout"]
    )
    rows = rule_based_extractor._group_blocks_into_rows(blocks)
    
    # Verify confidence components
    structure_conf = rule_based_extractor._calculate_structure_confidence(rows)
    assert structure_conf > 0.8  # High structure confidence for regular grid
    
    alignment_conf = rule_based_extractor._calculate_alignment_confidence(rows)
    assert alignment_conf > 0.8  # High alignment confidence for regular grid
    
    format_conf = rule_based_extractor._calculate_format_confidence(rows)
    assert format_conf > 0.7  # Good format confidence (header vs data)


@pytest.mark.asyncio
async def test_caption_extraction(rule_based_extractor, sample_layout_content):
    """Test extraction of table caption."""
    tables = await rule_based_extractor.extract_tables("test-doc", sample_layout_content)
    assert len(tables) == 1
    
    table = tables[0]
    assert table.caption == "Table 1: Sample Data"


@pytest.mark.asyncio
async def test_validation(rule_based_extractor, sample_layout_content):
    """Test table validation logic."""
    tables = await rule_based_extractor.extract_tables("test-doc", sample_layout_content)
    assert len(tables) == 1
    
    table = tables[0]
    is_valid = await rule_based_extractor.validate_table(table)
    assert is_valid
    
    # Test invalid table (remove some cells)
    table.cells = table.cells[:-3]  # Remove last row
    is_valid = await rule_based_extractor.validate_table(table)
    assert not is_valid


@pytest.mark.asyncio
async def test_empty_document(rule_based_extractor):
    """Test handling of empty document."""
    empty_doc = {"pages": [{"layout": {"elements": []}}]}
    tables = await rule_based_extractor.extract_tables("test-doc", empty_doc)
    assert len(tables) == 0


@pytest.mark.asyncio
async def test_invalid_input(rule_based_extractor):
    """Test handling of invalid input."""
    invalid_doc = {"invalid": "structure"}
    tables = await rule_based_extractor.extract_tables("test-doc", invalid_doc)
    assert len(tables) == 0