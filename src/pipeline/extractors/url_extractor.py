"""URL/website content extractor with crawling support."""

import time
from typing import Optional, Set, List
from urllib.parse import urljoin, urlparse
from collections import deque

try:
    import httpx
except ImportError:
    httpx = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .base import ExtractorStrategy
from ..models.document import Document, Source, Metadata, Content, StructuredContent
from ..utils.text_processing import clean_text, chunk_text
from ..utils.url_utils import (
    is_valid_url, is_same_domain, normalize_url, 
    should_skip_url, RobotsChecker, get_domain
)


class URLExtractor(ExtractorStrategy):
    """Extract content from URLs with optional crawling."""
    
    def __init__(self, user_agent: str = "DataFusionBot/1.0"):
        """
        Initialize URL extractor.
        
        Args:
            user_agent: User agent string for requests
        """
        self.user_agent = user_agent
        self.request_delay = 1.0  # Delay between requests in seconds
    
    def can_handle(self, source: str) -> bool:
        """Check if source is a valid URL."""
        return is_valid_url(source)
    
    def extract(self, source: str, company: str, **kwargs) -> Optional[Document]:
        """
        Extract content from URL.
        
        Args:
            source: URL to extract from
            company: Company name
            **kwargs: Additional parameters
                - crawl_mode: 'full' or 'summary' (default: 'summary')
                - max_pages: Maximum pages to crawl in full mode (default: 50)
                - timeout: Request timeout in seconds (default: 10)
                
        Returns:
            Extracted Document or None on error
        """
        if httpx is None:
            raise ImportError("httpx is not installed. Install with: pip install httpx")
        if BeautifulSoup is None:
            raise ImportError("BeautifulSoup4 is not installed. Install with: pip install beautifulsoup4 lxml")
        
        crawl_mode = kwargs.get('crawl_mode', 'summary')
        max_pages = kwargs.get('max_pages', 50)
        timeout = kwargs.get('timeout', 10)
        
        # Remove from kwargs to avoid duplicate argument errors
        kwargs_clean = {k: v for k, v in kwargs.items() if k not in ['crawl_mode', 'max_pages', 'timeout']}
        
        if crawl_mode == 'summary':
            # Extract from starting page and key summary pages
            return self._extract_summary(source, company, timeout, **kwargs_clean)
        else:
            # Full site crawl
            return self._extract_full(source, company, max_pages, timeout, **kwargs_clean)
    
    def _extract_summary(self, url: str, company: str, timeout: int, **kwargs) -> Optional[Document]:
        """
        Extract from main page and 1-2 key pages (about, products).
        
        Args:
            url: Starting URL
            company: Company name
            timeout: Request timeout
            **kwargs: Additional parameters
            
        Returns:
            Extracted Document or None
        """
        urls_to_fetch = [url]
        
        # Fetch main page first to find key pages
        main_content = self._fetch_url(url, timeout)
        if not main_content:
            return None
        
        soup = BeautifulSoup(main_content, 'lxml')
        
        # Find about/products pages
        key_pages = self._find_key_pages(soup, url)
        urls_to_fetch.extend(key_pages[:1])  # Add 1 key page for summary mode
        
        # Extract from all pages
        all_content = []
        all_structured = {
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'tables': [],
            'links': []
        }
        
        for page_url in urls_to_fetch:
            html = self._fetch_url(page_url, timeout)
            if html:
                structured = self._extract_from_html(html, page_url)
                if structured:
                    all_content.append(structured['raw_text'])
                    # Aggregate structured content
                    all_structured['headings'].extend(structured['structured'].headings)
                    all_structured['paragraphs'].extend(structured['structured'].paragraphs)
                    all_structured['lists'].extend(structured['structured'].lists)
                    all_structured['tables'].extend(structured['structured'].tables)
                    all_structured['links'].extend(structured['structured'].links)
            
            time.sleep(self.request_delay)
        
        if not all_content:
            return None
        
        # Combine all content
        raw_text = '\n\n'.join(all_content)
        
        # Create chunks
        chunk_size = kwargs.get('chunk_size', 512)
        chunks = chunk_text(raw_text, chunk_size=chunk_size)
        
        # Get metadata from main page
        title = soup.find('title')
        title_text = clean_text(title.get_text()) if title else get_domain(url)
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = clean_text(meta_desc['content']) if meta_desc and meta_desc.get('content') else None
        
        # Create Document
        document = Document(
            source=Source(
                type='url',
                uri=url,
                company=company
            ),
            metadata=Metadata(
                title=title_text,
                description=description,
                extra={'crawl_mode': 'summary', 'pages_fetched': len(urls_to_fetch)}
            ),
            content=Content(
                raw_text=raw_text,
                chunks=chunks,
                structured=StructuredContent(
                    headings=all_structured['headings'],
                    paragraphs=all_structured['paragraphs'],
                    lists=all_structured['lists'],
                    tables=all_structured['tables'],
                    links=all_structured['links'][:50]  # Limit links
                )
            )
        )
        
        return document
    
    def _extract_full(self, start_url: str, company: str, max_pages: int, timeout: int, **kwargs) -> Optional[Document]:
        """
        Crawl website and extract from all pages.
        
        Args:
            start_url: Starting URL
            company: Company name
            max_pages: Maximum pages to crawl
            timeout: Request timeout
            **kwargs: Additional parameters
            
        Returns:
            Extracted Document or None
        """
        visited: Set[str] = set()
        to_visit = deque([start_url])
        base_domain = get_domain(start_url)
        
        # Check robots.txt
        robots = RobotsChecker(start_url)
        
        all_content = []
        all_structured = {
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'tables': [],
            'links': []
        }
        
        main_title = None
        main_description = None
        
        while to_visit and len(visited) < max_pages:
            url = to_visit.popleft()
            
            # Skip if already visited
            if url in visited:
                continue
            
            # Check robots.txt
            if not robots.can_fetch(url, self.user_agent):
                continue
            
            visited.add(url)
            
            # Fetch page
            html = self._fetch_url(url, timeout)
            if not html:
                continue
            
            # Extract content
            structured = self._extract_from_html(html, url)
            if structured:
                all_content.append(structured['raw_text'])
                all_structured['headings'].extend(structured['structured'].headings)
                all_structured['paragraphs'].extend(structured['structured'].paragraphs)
                all_structured['lists'].extend(structured['structured'].lists)
                all_structured['tables'].extend(structured['structured'].tables)
                
                # Save main page metadata
                if url == start_url:
                    soup = BeautifulSoup(html, 'lxml')
                    title = soup.find('title')
                    main_title = clean_text(title.get_text()) if title else base_domain
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    main_description = clean_text(meta_desc['content']) if meta_desc and meta_desc.get('content') else None
                
                # Find new links
                soup = BeautifulSoup(html, 'lxml')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if should_skip_url(href):
                        continue
                    
                    abs_url = normalize_url(href, url)
                    
                    if is_same_domain(abs_url, start_url) and abs_url not in visited:
                        to_visit.append(abs_url)
            
            time.sleep(self.request_delay)
        
        if not all_content:
            return None
        
        # Combine all content
        raw_text = '\n\n'.join(all_content)
        
        # Create chunks
        chunk_size = kwargs.get('chunk_size', 512)
        chunks = chunk_text(raw_text, chunk_size=chunk_size)
        
        # Create Document
        document = Document(
            source=Source(
                type='url',
                uri=start_url,
                company=company
            ),
            metadata=Metadata(
                title=main_title or base_domain,
                description=main_description,
                extra={'crawl_mode': 'full', 'pages_fetched': len(visited)}
            ),
            content=Content(
                raw_text=raw_text,
                chunks=chunks,
                structured=StructuredContent(
                    headings=all_structured['headings'],
                    paragraphs=all_structured['paragraphs'],
                    lists=all_structured['lists'],
                    tables=all_structured['tables'],
                    links=all_structured['links'][:100]
                )
            )
        )
        
        return document
    
    def _fetch_url(self, url: str, timeout: int) -> Optional[str]:
        """
        Fetch URL content.
        
        Args:
            url: URL to fetch
            timeout: Request timeout
            
        Returns:
            HTML content or None
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers={'User-Agent': self.user_agent},
                    timeout=timeout,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' in content_type:
                        return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        
        return None
    
    def _extract_from_html(self, html: str, url: str) -> Optional[dict]:
        """Extract structured content from HTML."""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Extract headings
            headings = []
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                for heading in soup.find_all(tag):
                    text = clean_text(heading.get_text())
                    if text:
                        headings.append({'tag': tag, 'text': text})
            
            # Extract paragraphs
            paragraphs = []
            for p in soup.find_all('p'):
                text = clean_text(p.get_text())
                if text:
                    paragraphs.append(text)
            
            # Extract lists
            lists = []
            for list_tag in soup.find_all(['ul', 'ol']):
                items = []
                for li in list_tag.find_all('li', recursive=False):
                    text = clean_text(li.get_text())
                    if text:
                        items.append(text)
                if items:
                    lists.append({'type': list_tag.name, 'items': items})
            
            # Extract tables
            tables = []
            for table in soup.find_all('table'):
                headers = []
                rows = []
                
                header_row = table.find('thead')
                if header_row:
                    for th in header_row.find_all('th'):
                        headers.append(clean_text(th.get_text()))
                
                tbody = table.find('tbody') or table
                for tr in tbody.find_all('tr'):
                    row = []
                    for td in tr.find_all(['td', 'th']):
                        row.append(clean_text(td.get_text()))
                    if row:
                        rows.append(row)
                
                if rows:
                    tables.append({'headers': headers, 'rows': rows})
            
            # Build raw text
            raw_text_parts = []
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
            
            return {
                'raw_text': raw_text,
                'structured': StructuredContent(
                    headings=headings,
                    paragraphs=paragraphs,
                    lists=lists,
                    tables=tables,
                    links=[]
                )
            }
        except Exception as e:
            print(f"Error parsing HTML from {url}: {e}")
            return None
    
    def _find_key_pages(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find key pages like About, Products, Services.
        
        Args:
            soup: Parsed HTML
            base_url: Base URL
            
        Returns:
            List of key page URLs
        """
        key_words = ['about', 'product', 'service', 'company', 'who-we-are', 'what-we-do']
        key_pages = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            text = link.get_text().lower()
            
            for keyword in key_words:
                if keyword in href or keyword in text:
                    abs_url = normalize_url(link['href'], base_url)
                    if is_same_domain(abs_url, base_url) and abs_url not in key_pages:
                        key_pages.append(abs_url)
                        break
            
            if len(key_pages) >= 3:
                break
        
        return key_pages
