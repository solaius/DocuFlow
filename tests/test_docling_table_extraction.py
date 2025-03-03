import pytest
from typing import Dict, Any

from docuflow.table_extraction.docling_driven import DoclingTableExtractor
from docuflow.table_extraction.models.table import TableDetectionMethod


@pytest.fixture
def docling_extractor():
    """Create a DoclingTableExtractor instance."""
    return DoclingTableExtractor()


@pytest.fixture
def sample_docling_output() -> Dict[str, Any]:
    """Create sample Docling output with an explicit table."""
    return {
        "pages": [{
            "layout": {
                "elements": [{
                    "type": "table",
                    "bbox": [50, 50, 500, 300],
                    "cells": [
                        {
                            "text": "Header 1",
                            "row": 0,
                            "col": 0,
                            "is_header": True,
                            "confidence": 0.95,
                            "font": "Arial",
                            "font_size": 12
                        },
                        {
                            "text": "Header 2",
                            "row": 0,
                            "col": 1,
                            "is_header": True,
                            "confidence": 0.95,
                            "font": "Arial",
                            "font_size": 12
                        },
                        {
                            "text": "Data 1",
                            "row": 1,
                            "col": 0,
                            "is_header": False,
                            "confidence": 0.9,
                            "font": "Arial",
                            "font_size": 10
                        },
                        {
                            "text": "Data 2",
                            "row": 1,
                            "col": 1,
                            "is_header": False,
                            "confidence": 0.9,
                            "font": "Arial",
                            "font_size": 10
                        }
                    ],
                    "caption": "Sample Table"
                }]
            }
        }]
    }


@pytest.fixture
def sample_implicit_table_output() -> Dict[str, Any]:
    """Create sample Docling output with an implicit table structure."""
    return {
        "pages": [{
            "layout": {
                "elements": [{
                    "type": "text",
                    "bbox": [50, 50, 500, 300],
                    "blocks": [
                        {
                            "text": [
                                {"content": "Column 1", "x": 50, "y": 50, "font": "Arial", "font_size": 12},
                                {"content": "Column 2", "x": 200, "y": 50, "font": "Arial", "font_size": 12}
                            ]
                        },
                        {
                            "text": [
                                {"content": "Value 1", "x": 50, "y": 100, "font": "Arial", "font_size": 10},
                                {"content": "Value 2", "x": 200, "y": 100, "font": "Arial", "font_size": 10}
                            ]
                        }
                    ]
                }]
            }
        }]
    }


@pytest.mark.asyncio
async def test_extract_explicit_table(docling_extractor, sample_docling_output):
    """Test extraction of explicitly marked tables."""
    tables = await docling_extractor.extract_tables("test-doc", sample_docling_output)
    
    assert len(tables) == 1
    table = tables[0]
    
    assert table.document_id == "test-doc"
    assert table.page_number == 1
    assert table.num_rows == 2
    assert table.num_cols == 2
    assert table.caption == "Sample Table"
    assert table.detection_method == TableDetectionMethod.DOCLING_DRIVEN
    assert table.confidence_score >= 0.9
    
    # Verify cells
    assert len(table.cells) == 4
    headers = [cell for cell in table.cells if cell.is_header]
    assert len(headers) == 2
    assert headers[0].text == "Header 1"
    assert headers[1].text == "Header 2"


@pytest.mark.asyncio
async def test_extract_implicit_table(docling_extractor, sample_implicit_table_output):
    """Test extraction of implicit table structures."""
    tables = await docling_extractor.extract_tables("test-doc", sample_implicit_table_output)
    
    assert len(tables) == 1
    table = tables[0]
    
    assert table.document_id == "test-doc"
    assert table.page_number == 1
    assert table.num_rows == 2
    assert table.num_cols == 2
    assert table.detection_method == TableDetectionMethod.DOCLING_DRIVEN
    
    # Verify cells
    assert len(table.cells) == 4
    first_row = [cell for cell in table.cells if cell.row == 0]
    assert len(first_row) == 2
    assert "Column 1" in [cell.text for cell in first_row]
    assert "Column 2" in [cell.text for cell in first_row]


@pytest.mark.asyncio
async def test_table_validation(docling_extractor, sample_docling_output):
    """Test table validation logic."""
    tables = await docling_extractor.extract_tables("test-doc", sample_docling_output)
    assert len(tables) == 1
    
    table = tables[0]
    is_valid = await docling_extractor.validate_table(table)
    assert is_valid

    # Test invalid table (overlapping cells)
    table.cells[0].colspan = 2  # Make first header span both columns
    is_valid = await docling_extractor.validate_table(table)
    assert not is_valid


@pytest.mark.asyncio
async def test_confidence_calculation(docling_extractor, sample_docling_output, sample_implicit_table_output):
    """Test confidence score calculation."""
    tables = await docling_extractor.extract_tables("test-doc", sample_docling_output)
    assert len(tables) == 1
    
    table = tables[0]
    assert table.confidence_score > 0.8  # High confidence for explicit table
    
    # Test with implicit table (should have lower confidence)
    tables = await docling_extractor.extract_tables("test-doc", sample_implicit_table_output)
    assert len(tables) == 1
    assert tables[0].confidence_score < table.confidence_score


@pytest.mark.asyncio
async def test_empty_document(docling_extractor):
    """Test handling of documents with no tables."""
    empty_doc = {"pages": [{"layout": {"elements": []}}]}
    tables = await docling_extractor.extract_tables("test-doc", empty_doc)
    assert len(tables) == 0


@pytest.mark.asyncio
async def test_invalid_input(docling_extractor):
    """Test handling of invalid input."""
    invalid_doc = {"invalid": "structure"}
    tables = await docling_extractor.extract_tables("test-doc", invalid_doc)
    assert len(tables) == 0


@pytest.mark.asyncio
async def test_merged_cells(docling_extractor):
    """Test handling of merged cells."""
    doc_with_merged_cells = {
        "pages": [{
            "layout": {
                "elements": [{
                    "type": "table",
                    "bbox": [50, 50, 500, 300],
                    "cells": [
                        {
                            "text": "Merged Header",
                            "row": 0,
                            "col": 0,
                            "rowspan": 1,
                            "colspan": 2,
                            "is_header": True,
                            "confidence": 0.95
                        },
                        {
                            "text": "Data 1",
                            "row": 1,
                            "col": 0,
                            "is_header": False,
                            "confidence": 0.9
                        },
                        {
                            "text": "Data 2",
                            "row": 1,
                            "col": 1,
                            "is_header": False,
                            "confidence": 0.9
                        }
                    ]
                }]
            }
        }]
    }
    
    tables = await docling_extractor.extract_tables("test-doc", doc_with_merged_cells)
    assert len(tables) == 1
    table = tables[0]
    
    # Verify merged cell
    merged_header = next(cell for cell in table.cells if cell.colspan > 1)
    assert merged_header.text == "Merged Header"
    assert merged_header.colspan == 2