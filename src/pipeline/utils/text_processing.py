"""Text processing utilities."""

import re
from typing import List
from ..models.document import ContentChunk


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[ContentChunk]:
    """
    Split text into overlapping chunks for vector DB ingestion.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List of ContentChunk objects
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at sentence boundary if not at end
        if end < len(text):
            # Look for sentence endings
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:  # Only break if we're past halfway
                end = break_point + 1
        
        chunk_text_content = text[start:end].strip()
        
        if chunk_text_content:  # Only add non-empty chunks
            chunk = ContentChunk(
                text=chunk_text_content,
                start_index=start,
                end_index=end,
                metadata={"length": len(chunk_text_content)}
            )
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else end
    
    return chunks


def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from text.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Input text
        
    Returns:
        Text without URLs
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_pattern, '', text)
