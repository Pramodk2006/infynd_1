"""Document storage management."""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..models.document import Document


class DocumentStore:
    """Manage storage of extracted documents."""
    
    def __init__(self, base_dir: str = "data/outputs"):
        """
        Initialize document store.
        
        Args:
            base_dir: Base directory for storing documents
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, document: Document) -> Path:
        """
        Save document to disk.
        
        Args:
            document: Document to save
            
        Returns:
            Path to saved file
        """
        # Create company directory
        company_name = self._sanitize_name(document.source.company)
        company_dir = self.base_dir / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sources subdirectory
        sources_dir = company_dir / "sources"
        sources_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_type = document.source.type
        doc_id = document.document_id[:8]  # First 8 chars of UUID
        filename = f"{timestamp}_{source_type}_{doc_id}.json"
        
        filepath = sources_dir / filename
        
        # Save document
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document.to_dict(), f, indent=2, ensure_ascii=False, default=str)
        
        # Update company metadata
        self._update_company_metadata(company_dir, document)
        
        # Update index
        self._update_index(company_dir, document, filepath)
        
        return filepath
    
    def load(self, filepath: str) -> Optional[Document]:
        """
        Load document from disk.
        
        Args:
            filepath: Path to document file
            
        Returns:
            Document or None if not found
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Document.from_dict(data)
        except Exception as e:
            print(f"Error loading document from {filepath}: {e}")
            return None
    
    def list_sources(self, company: str) -> List[Dict[str, Any]]:
        """
        List all sources for a company.
        
        Args:
            company: Company name
            
        Returns:
            List of source information dictionaries
        """
        company_name = self._sanitize_name(company)
        company_dir = self.base_dir / company_name
        index_file = company_dir / "index.json"
        
        if not index_file.exists():
            return []
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            return index.get('sources', [])
        except Exception as e:
            print(f"Error reading index: {e}")
            return []
    
    def get_company_metadata(self, company: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a company.
        
        Args:
            company: Company name
            
        Returns:
            Company metadata or None
        """
        company_name = self._sanitize_name(company)
        metadata_file = self.base_dir / company_name / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading metadata: {e}")
            return None
    
    def list_companies(self) -> List[str]:
        """
        List all companies in the store.
        
        Returns:
            List of company names
        """
        companies = []
        if self.base_dir.exists():
            for item in self.base_dir.iterdir():
                if item.is_dir():
                    companies.append(item.name)
        return sorted(companies)
    
    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize company name for use as directory name.
        
        Args:
            name: Company name
            
        Returns:
            Sanitized name
        """
        # Replace spaces and special characters
        sanitized = name.lower().replace(' ', '-')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '-_')
        return sanitized
    
    def _update_company_metadata(self, company_dir: Path, document: Document):
        """Update company metadata file."""
        metadata_file = company_dir / "metadata.json"
        
        metadata = {
            'company': document.source.company,
            'last_updated': datetime.now().isoformat(),
        }
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                metadata['created'] = existing.get('created', metadata['last_updated'])
                metadata['total_sources'] = existing.get('total_sources', 0) + 1
            except Exception:
                metadata['created'] = metadata['last_updated']
                metadata['total_sources'] = 1
        else:
            metadata['created'] = metadata['last_updated']
            metadata['total_sources'] = 1
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _update_index(self, company_dir: Path, document: Document, filepath: Path):
        """Update company source index."""
        index_file = company_dir / "index.json"
        
        source_entry = {
            'document_id': document.document_id,
            'type': document.source.type,
            'uri': document.source.uri,
            'extracted_at': document.source.extracted_at.isoformat(),
            'title': document.metadata.title,
            'filepath': str(filepath.relative_to(self.base_dir))
        }
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            except Exception:
                index = {'sources': []}
        else:
            index = {'sources': []}
        
        index['sources'].append(source_entry)
        index['last_updated'] = datetime.now().isoformat()
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
