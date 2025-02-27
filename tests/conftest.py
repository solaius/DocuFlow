import os
import shutil
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from docuflow.api.main import app
from docuflow.ingestion.service import IngestionService


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_upload_dir(temp_dir):
    """Create a temporary upload directory."""
    upload_dir = Path(temp_dir) / "uploads"
    upload_dir.mkdir(parents=True)
    yield str(upload_dir)


@pytest.fixture
def test_processed_dir(temp_dir):
    """Create a temporary processed directory."""
    processed_dir = Path(temp_dir) / "processed"
    processed_dir.mkdir(parents=True)
    yield str(processed_dir)


@pytest.fixture
def ingestion_service(test_upload_dir, test_processed_dir):
    """Create an IngestionService instance with test directories."""
    return IngestionService(test_upload_dir, test_processed_dir)


@pytest.fixture
def test_client():
    """Create a TestClient instance."""
    return TestClient(app)


@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(content)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def sample_docx():
    """Create a sample DOCX file for testing."""
    content = b"PK\x03\x04\x14\x00\x00\x00\x00\x00"  # Minimal DOCX signature
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(content)
        yield f.name
    os.unlink(f.name)