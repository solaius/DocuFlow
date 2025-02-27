from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Union

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import (PdfPipelineOptions, TableFormerMode,
                                              TableStructureOptions)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument, TableItem

from docuflow.models.document import Document, DocumentStatus


class DocumentParsingService:
    def __init__(self):
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
            
            # Enable OCR for scanned documents
            do_ocr=True,
            
            # Generate page images for visualization
            generate_page_images=True,
            generate_picture_images=True,
            
            # Set reasonable timeout
            document_timeout=300  # 5 minutes
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
            # Convert table to pandas DataFrame
            df = table.export_to_dataframe()
            
            # Get table metadata
            table_data = {
                "page": page_no,
                "content": table.export_to_markdown(),
                "num_rows": len(df),
                "num_cols": len(df.columns),
                "headers": df.columns.tolist(),
                "bbox": None
            }
            
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
        
        # Process each page
        for page_no, page in docling_doc.pages.items():
            # Check for tables
            if docling_doc.tables:
                metadata["has_tables"] = True
                for table in docling_doc.tables:
                    if any(prov.page_no == page_no for prov in table.prov):
                        table_data = self._extract_table_data(table, page_no)
                        metadata["tables"].append(table_data)
            
            # Check for images
            if docling_doc.pictures:
                metadata["has_images"] = True
                for picture in docling_doc.pictures:
                    if any(prov.page_no == page_no for prov in picture.prov):
                        picture_data = self._extract_picture_data(picture, page_no)
                        metadata["images"].append(picture_data)
            
            # Check for code and formulas
            for text_item in docling_doc.texts:
                if text_item.label == "code":
                    metadata["has_code"] = True
                elif text_item.label == "formula":
                    metadata["has_formulas"] = True
                    
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
                document.status = DocumentStatus.PROCESSED
                
            elif result.status == ConversionStatus.PARTIAL_SUCCESS:
                # Handle partial success - some content was extracted
                document.status = DocumentStatus.PROCESSED
                document.content = result.document.export_to_markdown()
                document.metadata = self._process_docling_document(result.document)
                document.error = f"Partial success: {'; '.join(str(e) for e in result.errors)}"
                
            else:
                # Handle complete failure
                document.status = DocumentStatus.FAILED
                document.error = f"Docling conversion failed: {'; '.join(str(e) for e in result.errors)}"
                
        except Exception as e:
            document.status = DocumentStatus.FAILED
            document.error = f"Document parsing failed: {str(e)}"
            
        return document