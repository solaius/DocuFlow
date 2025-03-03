# Table Extraction Module

The table extraction module provides robust capabilities for detecting and extracting tables from documents.

## Features

### Basic Table Structures
- Simple grid tables
- Tables with merged cells (rowspan/colspan)
- Tables with headers and footers

### Moderate Complexity
- Multi-level column headers
- Hierarchical/nested tables
- Mixed data type handling
- Empty/missing cell support
- Irregular column widths and row heights

### High Complexity (Coming Soon)
- Multi-line text cells
- Rotated/diagonal headers
- Tables with notes and footnotes
- Multi-page tables
- Split cells and jagged layouts

## Usage

### Basic Example
```python
from docuflow.table_extraction.service import TableExtractionService
from docuflow.table_extraction.models import TableDetectionMethod

# Initialize service
service = TableExtractionService()

# Register extractors
service.register_extractor(
    TableDetectionMethod.DOCLING_DRIVEN,
    DoclingTableExtractor()
)
service.register_extractor(
    TableDetectionMethod.RULE_BASED,
    RuleBasedTableExtractor()
)

# Extract tables
tables = await service.extract_tables(
    document_id="doc123",
    parsed_content=content
)
```

### Extraction Methods

#### AI-Driven Extraction
Uses IBM Docling's document analysis capabilities to:
- Detect table regions
- Analyze table structure
- Extract cell content and relationships

#### Rule-Based Extraction
Provides fallback capabilities using:
- Layout analysis
- Grid detection
- Text alignment patterns

## Configuration

### Confidence Thresholds
```python
extractor = DoclingTableExtractor(
    min_confidence_threshold=0.7
)
```

### Validation Rules
- Minimum table size (rows × columns)
- Cell content requirements
- Structure consistency checks

## Testing

See [test_files/tables/](../../test_files/tables/) for example tables and test cases:
- Basic table structures
- Moderate complexity tables
- High complexity tables (coming soon)

## Future Enhancements

1. Advanced Layout Analysis
   - Better handling of complex layouts
   - Improved merged cell detection

2. Content Understanding
   - Semantic analysis of cell content
   - Data type inference
   - Relationship detection

3. Performance Optimization
   - Parallel processing
   - GPU acceleration
   - Caching strategies