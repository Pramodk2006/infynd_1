"""
Data models for the extraction pipeline.

These models define the structure for extracted documents,
designed to be vector-DB ready with proper chunking and metadata.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict


class Source(BaseModel):
    """Source information for a document."""
    
    type: str = Field(..., description="Source type: pdf, url, html, text")
    uri: str = Field(..., description="Original source path or URL")
    company: str = Field(..., description="Company name")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    
    model_config = ConfigDict(frozen=False)


class Metadata(BaseModel):
    """Document metadata."""
    
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    date: Optional[datetime] = Field(None, description="Document date")
    page_count: Optional[int] = Field(None, description="Number of pages")
    language: Optional[str] = Field(None, description="Document language")
    description: Optional[str] = Field(None, description="Meta description")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    model_config = ConfigDict(frozen=False)


class ContentChunk(BaseModel):
    """A chunk of content for vector database ingestion."""
    
    chunk_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique chunk ID")
    text: str = Field(..., description="Chunk text content")
    start_index: int = Field(..., description="Start position in raw_text")
    end_index: int = Field(..., description="End position in raw_text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk-level metadata (section, page, etc.)")
    
    model_config = ConfigDict(frozen=False)


class StructuredContent(BaseModel):
    """Structured HTML content extraction."""
    
    headings: List[Dict[str, str]] = Field(default_factory=list, description="Headings with tags")
    paragraphs: List[str] = Field(default_factory=list, description="Paragraph texts")
    lists: List[Dict[str, Any]] = Field(default_factory=list, description="Lists with items")
    tables: List[Dict[str, Any]] = Field(default_factory=list, description="Tables with headers/rows")
    links: List[Dict[str, str]] = Field(default_factory=list, description="Extracted links")
    
    model_config = ConfigDict(frozen=False)


class Content(BaseModel):
    """Document content with raw text and chunks."""
    
    raw_text: str = Field(..., description="Full extracted text")
    chunks: List[ContentChunk] = Field(default_factory=list, description="Pre-chunked content")
    structured: Optional[StructuredContent] = Field(None, description="Structured content (for HTML)")
    
    model_config = ConfigDict(frozen=False)


class Document(BaseModel):
    """Main document model for extracted content."""
    
    document_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique document ID")
    source: Source = Field(..., description="Source information")
    metadata: Metadata = Field(default_factory=Metadata, description="Document metadata")
    content: Content = Field(..., description="Document content")
    
    model_config = ConfigDict(frozen=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create Document from dictionary."""
        return cls.model_validate(data)
