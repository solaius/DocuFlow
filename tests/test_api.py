import os

import pytest
from fastapi import status


def test_root_endpoint(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to DocuFlow API"}


def test_upload_pdf(test_client, sample_pdf):
    """Test uploading a PDF file."""
    # Prepare the file for upload
    with open(sample_pdf, "rb") as f:
        files = {"file": (os.path.basename(sample_pdf), f, "application/pdf")}
        response = test_client.post("/documents/upload", files=files)
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == os.path.basename(sample_pdf)
    assert data["file_type"] == "pdf"
    assert data["status"] == "pending"


def test_upload_docx(test_client, sample_docx):
    """Test uploading a DOCX file."""
    # Prepare the file for upload
    with open(sample_docx, "rb") as f:
        files = {"file": (os.path.basename(sample_docx), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = test_client.post("/documents/upload", files=files)
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == os.path.basename(sample_docx)
    assert data["file_type"] == "docx"
    assert data["status"] == "pending"


def test_get_nonexistent_document(test_client):
    """Test getting a document that doesn't exist."""
    # Test with valid UUID format
    response = test_client.get("/documents/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Test with invalid UUID format
    response = test_client.get("/documents/nonexistent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Test with empty ID
    response = test_client.get("/documents/")
    assert response.status_code == status.HTTP_404_NOT_FOUND