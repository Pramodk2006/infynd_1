"""HTML file content extractor using BeautifulSoup4."""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from bs4 import BeautifulSoup, Tag
except ImportError:
    BeautifulSoup = None
    Tag = None

from .base import ExtractorStrategy
from ..models.document import Document, Source, Metadata, Content, StructuredContent
from ..utils.text_processing import clean_text, chunk_text


class HTMLExtractor(ExtractorStrategy):
    """Extract content from HTML files."""
    
    def can_handle(self, source: str) -> bool:
        """Check if source is an HTML file."""
        if not os.path.exists(source):
            return False
        return source.lower().endswith(('.html', '.htm'))
    
    def extract(self, source: str, company: str, **kwargs) -> Optional[Document]:
        """
        Extract structured content from HTML file.
        
        Args:
            source: Path to HTML file
            company: Company name
            **kwargs: Additional parameters
            
        Returns:
            Extracted Document or None on error
        """
        if BeautifulSoup is None:
            raise ImportError("BeautifulSoup4 is not installed. Install with: pip install beautifulsoup4 lxml")
        
        try:
            # Read HTML file
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = clean_text(title_tag.get_text())
            
            # Extract meta description
            description = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = clean_text(meta_desc['content'])
            
            # Extract headings
            headings = self._extract_headings(soup)
            
            # Extract paragraphs
            paragraphs = self._extract_paragraphs(soup)
            
            # Extract lists
            lists = self._extract_lists(soup)
            
            # Extract tables
            tables = self._extract_tables(soup)
            
            # Extract links
            links = self._extract_links(soup, source)
            
            # Build raw text
            raw_text_parts = []
            if title:
                raw_text_parts.append(title)
            if description:
                raw_text_parts.append(description)
            
            for heading in headings:
                raw_text_parts.append(heading['text'])
            
            raw_text_parts.extend(paragraphs)
            
            for lst in lists:
                raw_text_parts.extend(lst['items'])
            
            for table in tables:
                for row in table['rows']:
                    raw_text_parts.extend(row)
            
            raw_text = '\n\n'.join(raw_text_parts)
            raw_text = clean_text(raw_text)
            
            if not raw_text:
                return None
            
            # Create chunks
            chunk_size = kwargs.get('chunk_size', 512)
            chunks = chunk_text(raw_text, chunk_size=chunk_size)
            
            # Create Document
            document = Document(
                source=Source(
                    type='html',
                    uri=str(Path(source).absolute()),
                    company=company
                ),
                metadata=Metadata(
                    title=title or Path(source).stem,
                    description=description
                ),
                content=Content(
                    raw_text=raw_text,
                    chunks=chunks,
                    structured=StructuredContent(
                        headings=headings,
                        paragraphs=paragraphs,
                        lists=lists,
                        tables=tables,
                        links=links
                    )
                )
            )
            
            return document
            
        except Exception as e:
            print(f"Error extracting HTML {source}: {e}")
            return None
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all headings (h1-h6)."""
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(tag):
                text = clean_text(heading.get_text())
                if text:
                    headings.append({'tag': tag, 'text': text})
        return headings
    
    def _extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract all paragraph texts."""
        paragraphs = []
        for p in soup.find_all('p'):
            text = clean_text(p.get_text())
            if text:
                paragraphs.append(text)
        return paragraphs
    
    def _extract_lists(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all lists (ul, ol)."""
        lists = []
        for list_tag in soup.find_all(['ul', 'ol']):
            items = []
            for li in list_tag.find_all('li', recursive=False):
                text = clean_text(li.get_text())
                if text:
                    items.append(text)
            if items:
                lists.append({
                    'type': list_tag.name,
                    'items': items
                })
        return lists
    
    def _extract_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all tables."""
        tables = []
        for table in soup.find_all('table'):
            headers = []
            rows = []
            
            # Extract headers
            header_row = table.find('thead')
            if header_row:
                for th in header_row.find_all('th'):
                    headers.append(clean_text(th.get_text()))
            
            # Extract rows
            tbody = table.find('tbody') or table
            for tr in tbody.find_all('tr'):
                row = []
                for td in tr.find_all(['td', 'th']):
                    row.append(clean_text(td.get_text()))
                if row:
                    rows.append(row)
            
            if rows:
                tables.append({
                    'headers': headers,
                    'rows': rows
                })
        
        return tables
    
    def _extract_links(self, soup: BeautifulSoup, base_path: str) -> List[Dict[str, str]]:
        """Extract all links."""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = clean_text(a.get_text())
            if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                links.append({
                    'text': text,
                    'href': href
                })
        return links[:100]  # Limit to first 100 links
