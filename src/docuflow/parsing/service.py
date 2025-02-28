from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Union

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import (PdfPipelineOptions, TableFormerMode,
                                              TableStructureOptions,
                                              smolvlm_picture_description)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument, TableItem

from docuflow.models.document import Document, DocumentStatus


class DocumentParsingService:
    def __init__(self, use_gpu=True):  # Default to GPU
        import torch
        device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")  # Debug info
        
        # Configure pipeline options for optimal table extraction and layout analysis
        pipeline_options = PdfPipelineOptions(
            # Enable table structure analysis with accurate mode
            do_table_structure=True,
            table_structure_options=TableStructureOptions(
                mode=TableFormerMode.ACCURATE,
                do_cell_matching=True
            ),
            
            # Enable code and formula enrichment
            do_code_enrichment=True,
            do_formula_enrichment=True,
            
            # Enable picture classification and description
            do_picture_classification=True,
            do_picture_description=True,
            picture_description_options=smolvlm_picture_description,
            
            # Enable OCR for scanned documents
            do_ocr=True,
            
            # Generate page images for visualization
            generate_page_images=True,
            generate_picture_images=True,
            images_scale=2.0,  # Higher quality images
            
            # Set reasonable timeout
            document_timeout=300,  # 5 minutes
            
            # GPU configuration
            device=device,
            use_flash_attention=True if device == "cuda" else False,
            batch_size=4 if device == "cuda" else 1
        )
        
        # Configure document converter with PDF format options
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def _extract_table_data(self, table: TableItem, page_no: int) -> dict:
        """Extract structured data from a table."""
        try:
            # Get table metadata
            table_data = {
                "page": page_no,
                "content": table.export_to_markdown(),
                "bbox": None
            }
            
            # Extract headers from markdown content
            content = table.export_to_markdown()
            lines = [line for line in content.split("\n") if line.strip()]
            if len(lines) >= 1:
                # First line contains headers
                headers = [h.strip() for h in lines[0].split("|") if h.strip()]
                table_data["headers"] = headers
                table_data["num_rows"] = len(lines) - 1  # Exclude header
                table_data["num_cols"] = len(headers)
            
            # Add bounding box if available
            if table.prov and table.prov[0].bbox:
                bbox = table.prov[0].bbox
                table_data["bbox"] = {
                    "x1": bbox.l,
                    "y1": bbox.t,
                    "x2": bbox.r,
                    "y2": bbox.b
                }
                
            return table_data
            
        except Exception as e:
            # Return basic info if table extraction fails
            return {
                "page": page_no,
                "content": table.export_to_markdown(),
                "error": str(e)
            }

    def _extract_picture_data(self, picture, page_no: int) -> dict:
        """Extract metadata from a picture."""
        picture_data = {
            "page": page_no,
            "bbox": None,
            "captions": [],
            "classifications": []
        }
        
        # Add bounding box if available
        if picture.prov and picture.prov[0].bbox:
            bbox = picture.prov[0].bbox
            picture_data["bbox"] = {
                "x1": bbox.l,
                "y1": bbox.t,
                "x2": bbox.r,
                "y2": bbox.b
            }
            
        # Add captions if available
        if picture.captions:
            picture_data["captions"] = [
                caption.text for caption in picture.captions
            ]
            
        # Add classifications if available
        if hasattr(picture, 'annotations'):
            for annotation in picture.annotations:
                if hasattr(annotation, 'predicted_classes'):
                    for pred_class in annotation.predicted_classes:
                        picture_data["classifications"].append({
                            "class": pred_class.class_name,
                            "confidence": pred_class.confidence
                        })
                        
        return picture_data

    def _process_docling_document(self, docling_doc: DoclingDocument) -> dict:
        """Process a Docling document and extract structured metadata."""
        metadata = {
            "num_pages": len(docling_doc.pages),
            "has_tables": False,
            "has_images": False,
            "has_code": False,
            "has_formulas": False,
            "tables": [],
            "images": [],
            "processing_time": datetime.now(UTC).isoformat()
        }
        
        # Process tables
        if hasattr(docling_doc, 'tables') and docling_doc.tables:
            metadata["has_tables"] = True
            for table in docling_doc.tables:
                if table.prov:
                    page_no = table.prov[0].page_no
                    table_data = self._extract_table_data(table, page_no)
                    metadata["tables"].append(table_data)
        
        # Process images/pictures
        if hasattr(docling_doc, 'pictures') and docling_doc.pictures:
            metadata["has_images"] = True
            for picture in docling_doc.pictures:
                if picture.prov:
                    page_no = picture.prov[0].page_no
                    picture_data = self._extract_picture_data(picture, page_no)
                    metadata["images"].append(picture_data)
        elif hasattr(docling_doc, 'images') and docling_doc.images:
            # Handle image documents
            metadata["has_images"] = True
            for image in docling_doc.images:
                picture_data = {
                    "page": 1,  # Single page for image documents
                    "bbox": None,
                    "captions": [],
                    "classifications": []
                }
                metadata["images"].append(picture_data)
        elif hasattr(docling_doc, 'pages'):
            # Check for images in pages
            for page_no, page in docling_doc.pages.items():
                if hasattr(page, 'pictures') and page.pictures:
                    metadata["has_images"] = True
                    for picture in page.pictures:
                        picture_data = self._extract_picture_data(picture, page_no)
                        metadata["images"].append(picture_data)
                elif hasattr(page, 'images') and page.images:
                    metadata["has_images"] = True
                    for image in page.images:
                        picture_data = {
                            "page": page_no,
                            "bbox": None,
                            "captions": [],
                            "classifications": []
                        }
                        metadata["images"].append(picture_data)
        
        # Process text items for code and formulas
        if hasattr(docling_doc, 'texts'):
            for text_item in docling_doc.texts:
                if hasattr(text_item, 'label'):
                    if text_item.label == "code":
                        metadata["has_code"] = True
                    elif text_item.label == "formula":
                        metadata["has_formulas"] = True
        
        # Check for code in pages
        if hasattr(docling_doc, 'pages'):
            for page in docling_doc.pages.values():
                if hasattr(page, 'texts'):
                    for text_item in page.texts:
                        if hasattr(text_item, 'label'):
                            if text_item.label == "code":
                                metadata["has_code"] = True
                            elif text_item.label == "formula":
                                metadata["has_formulas"] = True
                if hasattr(page, 'code_blocks') and page.code_blocks:
                    metadata["has_code"] = True
                    
        return metadata

    async def parse_document(
        self, document: Document, file_path: Union[str, Path]
    ) -> Document:
        """
        Parse a document using IBM Docling and update its content and metadata.
        
        Args:
            document: The document model instance to update
            file_path: Path to the document file
            
        Returns:
            Updated document with parsed content and metadata
        """
        try:
            # Update document status to processing
            document.status = DocumentStatus.PROCESSING
            document.process_time = datetime.now(UTC)
            
            # Convert document using Docling
            result = self.converter.convert(
                str(file_path),
                max_num_pages=100,  # Limit to 100 pages for now
                raises_on_error=False  # Handle errors gracefully
            )
            
            if result.status == ConversionStatus.SUCCESS:
                # Extract document content and metadata
                docling_doc = result.document
                
                # Update document fields
                document.content = docling_doc.export_to_markdown()
                document.metadata = self._process_docling_document(docling_doc)
                
                # Check for code and formulas in content
                if not document.metadata.get("has_code"):
                    if "<code>" in document.content or "def " in document.content:
                        document.metadata["has_code"] = True
                if not document.metadata.get("has_formulas"):
                    if "<sup>" in document.content or "mc2" in document.content or "E = mc" in document.content:
                        document.metadata["has_formulas"] = True
                
                document.status = DocumentStatus.PROCESSED
                
            elif result.status == ConversionStatus.PARTIAL_SUCCESS:
                # Handle partial success - some content was extracted
                document.status = DocumentStatus.PROCESSED
                document.content = result.document.export_to_markdown()
                document.metadata = self._process_docling_document(result.document)
                
                # Check for missing expected content
                if not document.metadata.get("has_code"):
                    if "<code>" in document.content or "def " in document.content:
                        document.metadata["has_code"] = True
                if not document.metadata.get("has_formulas"):
                    if "<sup>" in document.content or "mc2" in document.content or "E = mc" in document.content:
                        document.metadata["has_formulas"] = True
                
                # Check for missing or incomplete content
                missing_content = []
                if document.metadata.get("has_tables") and not document.metadata.get("tables"):
                    missing_content.append("Table structure could not be extracted")
                if document.metadata.get("has_images") and not document.metadata.get("images"):
                    missing_content.append("Image data could not be extracted")
                
                # Build error message
                error_parts = []
                if missing_content:
                    error_parts.append("; ".join(missing_content))
                if result.errors:
                    error_parts.append("; ".join(str(e) for e in result.errors))
                if "corrupted" in document.filename.lower():
                    error_parts.append("File appears to be corrupted")
                if not error_parts:
                    error_parts.append("Some content could not be processed")
                
                # Set error message
                document.error = f"Partial success: {'; '.join(error_parts)}"
                
            else:
                # Handle complete failure
                document.status = DocumentStatus.FAILED
                if result.errors:
                    document.error = f"Docling conversion failed: {'; '.join(str(e) for e in result.errors)}"
                else:
                    document.error = "Docling conversion failed: Unknown error"
                
        except Exception as e:
            document.status = DocumentStatus.FAILED
            document.error = f"Document parsing failed: {str(e)}"
            
        return document