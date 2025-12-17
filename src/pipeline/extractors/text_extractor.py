"""Plain text content extractor."""

import os
from pathlib import Path
from typing import Optional

from .base import ExtractorStrategy
from ..models.document import Document, Source, Metadata, Content
from ..utils.text_processing import clean_text, chunk_text


class TextExtractor(ExtractorStrategy):
    """Extract content from plain text files."""
    
    def can_handle(self, source: str) -> bool:
        """Check if source is a text file."""
        if not os.path.exists(source):
            return False
        return source.lower().endswith(('.txt', '.text', '.md', '.markdown'))
    
    def extract(self, source: str, company: str, **kwargs) -> Optional[Document]:
        """
        Extract content from text file.
        
        Args:
            source: Path to text file
            company: Company name
            **kwargs: Additional parameters
            
        Returns:
            Extracted Document or None on error
        """
        try:
            # Read text file
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            
            # Clean text
            raw_text = clean_text(raw_text)
            
            if not raw_text:
                return None
            
            # Create chunks
            chunk_size = kwargs.get('chunk_size', 512)
            chunks = chunk_text(raw_text, chunk_size=chunk_size)
            
            # Create Document
            document = Document(
                source=Source(
                    type='text',
                    uri=str(Path(source).absolute()),
                    company=company
                ),
                metadata=Metadata(
                    title=Path(source).stem
                ),
                content=Content(
                    raw_text=raw_text,
                    chunks=chunks
                )
            )
            
            return document
            
        except Exception as e:
            print(f"Error extracting text file {source}: {e}")
            return None
