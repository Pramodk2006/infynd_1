"""Extractor factory for automatic source type detection and routing."""

import os
from typing import Optional

try:
    import filetype
except ImportError:
    filetype = None

from .base import ExtractorStrategy
from .pdf_extractor import PDFExtractor
from .html_extractor import HTMLExtractor
from .url_extractor import URLExtractor
from .text_extractor import TextExtractor
from ..utils.url_utils import is_valid_url


class ExtractorFactory:
    """Factory for creating appropriate extractors based on source type."""
    
    _extractors = {
        'pdf': PDFExtractor,
        'html': HTMLExtractor,
        'url': URLExtractor,
        'text': TextExtractor
    }
    
    @classmethod
    def get_extractor(cls, source: str) -> Optional[ExtractorStrategy]:
        """
        Get appropriate extractor for the given source.
        
        Args:
            source: Source to extract from (URL, file path, or text)
            
        Returns:
            Appropriate ExtractorStrategy instance or None
        """
        # Check if it's a URL
        if is_valid_url(source):
            return URLExtractor()
        
        # Check if it's a file
        if os.path.exists(source):
            # Try each file-based extractor
            for extractor_class in [PDFExtractor, HTMLExtractor, TextExtractor]:
                extractor = extractor_class()
                if extractor.can_handle(source):
                    return extractor
            
            # Try to detect by MIME type if filetype is available
            if filetype is not None:
                kind = filetype.guess(source)
                if kind is not None:
                    if kind.mime == 'application/pdf':
                        return PDFExtractor()
                    elif kind.mime in ['text/html', 'application/xhtml+xml']:
                        return HTMLExtractor()
                    elif kind.mime.startswith('text/'):
                        return TextExtractor()
            
            # Default to text for unknown file types
            return TextExtractor()
        
        # If not a URL or file, assume it's raw text
        # (though this is not typically used in current implementation)
        return None
    
    @classmethod
    def detect_source_type(cls, source: str) -> str:
        """
        Detect the type of source.
        
        Args:
            source: Source to check
            
        Returns:
            Source type: 'url', 'pdf', 'html', 'text', or 'unknown'
        """
        if is_valid_url(source):
            return 'url'
        
        if os.path.exists(source):
            if source.lower().endswith('.pdf'):
                return 'pdf'
            elif source.lower().endswith(('.html', '.htm')):
                return 'html'
            elif source.lower().endswith(('.txt', '.text', '.md', '.markdown')):
                return 'text'
            
            # Try MIME type detection
            if filetype is not None:
                kind = filetype.guess(source)
                if kind is not None:
                    if kind.mime == 'application/pdf':
                        return 'pdf'
                    elif kind.mime in ['text/html', 'application/xhtml+xml']:
                        return 'html'
                    elif kind.mime.startswith('text/'):
                        return 'text'
        
        return 'unknown'
