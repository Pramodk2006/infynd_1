"""
Base extractor strategy interface.

All extractors must implement this abstract base class.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models.document import Document


class ExtractorStrategy(ABC):
    """Abstract base class for all extractors."""
    
    @abstractmethod
    def extract(self, source: str, company: str, **kwargs) -> Optional[Document]:
        """
        Extract content from a source.
        
        Args:
            source: Source to extract from (URL, file path, or text)
            company: Company name for the document
            **kwargs: Additional extraction parameters
            
        Returns:
            Extracted Document or None if extraction failed
        """
        pass
    
    @abstractmethod
    def can_handle(self, source: str) -> bool:
        """
        Check if this extractor can handle the given source.
        
        Args:
            source: Source to check
            
        Returns:
            True if this extractor can handle the source
        """
        pass
