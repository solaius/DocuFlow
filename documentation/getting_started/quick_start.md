# Quick Start Guide

This guide will help you get started with DocuFlow quickly.

## Prerequisites

- Python 3.11 or later
- Poetry for dependency management
- CUDA-capable GPU (optional, for improved performance)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/solaius/DocuFlow.git
cd DocuFlow
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment:
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

## Basic Usage

1. Process a document:
```python
from docuflow.ingestion.service import IngestionService
from docuflow.parsing.service import DocumentParsingService

# Initialize services
ingestion = IngestionService()
parser = DocumentParsingService()

# Process a document
doc_id = await ingestion.upload("path/to/document.pdf")
result = await parser.process(doc_id)
```

2. Extract tables:
```python
from docuflow.table_extraction.service import TableExtractionService
from docuflow.table_extraction.models import TableDetectionMethod

# Initialize service
extractor = TableExtractionService()

# Extract tables
tables = await extractor.extract_tables(
    document_id=doc_id,
    parsed_content=result,
    preferred_method=TableDetectionMethod.AI_DRIVEN
)

# Process results
for table in tables:
    print(f"Table {table.id}:")
    print(f"Size: {table.num_rows}×{table.num_cols}")
    print("Content:")
    for row in table.data.grid:
        print([cell.text for cell in row])
```

## Next Steps

- Read the [Basic Usage Guide](basic_usage.md) for more detailed examples
- Check out the [Configuration Guide](configuration.md) for customization options
- See [Examples](../examples/basic.md) for more use cases