"""PDF content extractor using PyMuPDF."""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from .base import ExtractorStrategy
from ..models.document import Document, Source, Metadata, Content, StructuredContent
from ..utils.text_processing import clean_text, chunk_text


class PDFExtractor(ExtractorStrategy):
    """Extract content from PDF files using PyMuPDF."""
    
    def can_handle(self, source: str) -> bool:
        """Check if source is a PDF file."""
        if not os.path.exists(source):
            return False
        return source.lower().endswith('.pdf')
    
    def extract(self, source: str, company: str, **kwargs) -> Optional[Document]:
        """
        Extract text and metadata from PDF file.
        
        Args:
            source: Path to PDF file
            company: Company name
            **kwargs: Additional parameters (chunk_size, etc.)
            
        Returns:
            Extracted Document or None on error
        """
        if fitz is None:
            raise ImportError("PyMuPDF is not installed. Install with: pip install PyMuPDF")
        
        try:
            # Open PDF
            pdf_doc = fitz.open(source)
            
            # Extract metadata
            pdf_metadata = pdf_doc.metadata
            metadata = Metadata(
                title=pdf_metadata.get('title') or Path(source).stem,
                author=pdf_metadata.get('author'),
                page_count=len(pdf_doc),
                extra={
                    'creator': pdf_metadata.get('creator'),
                    'producer': pdf_metadata.get('producer'),
                    'format': pdf_metadata.get('format', 'PDF'),
                }
            )
            
            # Try to extract creation date
            if pdf_metadata.get('creationDate'):
                try:
                    # PyMuPDF date format: D:YYYYMMDDHHmmSS
                    date_str = pdf_metadata['creationDate']
                    if date_str.startswith('D:'):
                        date_str = date_str[2:16]  # Extract YYYYMMDDHHmmSS
                        metadata.date = datetime.strptime(date_str, '%Y%m%d%H%M%S')
                except Exception:
                    pass
            
            # Extract text from all pages
            full_text = []
            for page_num, page in enumerate(pdf_doc):
                page_text = page.get_text()
                if page_text.strip():
                    full_text.append(page_text)
            
            pdf_doc.close()
            
            # Combine and clean text
            raw_text = '\n\n'.join(full_text)
            raw_text = clean_text(raw_text)
            
            if not raw_text:
                return None
            
            # Create chunks
            chunk_size = kwargs.get('chunk_size', 512)
            chunks = chunk_text(raw_text, chunk_size=chunk_size)
            
            # Create Document
            document = Document(
                source=Source(
                    type='pdf',
                    uri=str(Path(source).absolute()),
                    company=company
                ),
                metadata=metadata,
                content=Content(
                    raw_text=raw_text,
                    chunks=chunks
                )
            )
            
            return document
            
        except Exception as e:
            print(f"Error extracting PDF {source}: {e}")
            return None
