"""URL utilities for validation and parsing."""

import re
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from typing import Optional


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def get_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain name or None
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs are from the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if same domain
    """
    return get_domain(url1) == get_domain(url2)


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """
    Normalize URL by removing fragments and making it absolute.
    
    Args:
        url: URL to normalize
        base_url: Base URL for relative URLs
        
    Returns:
        Normalized URL
    """
    # Remove fragment
    url = url.split('#')[0]
    
    # Make absolute if base_url provided
    if base_url:
        url = urljoin(base_url, url)
    
    # Remove trailing slash
    if url.endswith('/'):
        url = url[:-1]
    
    return url


def should_skip_url(url: str) -> bool:
    """
    Check if URL should be skipped (mailto, tel, javascript, etc.).
    
    Args:
        url: URL to check
        
    Returns:
        True if should skip
    """
    skip_schemes = ['mailto:', 'tel:', 'javascript:', 'data:', 'ftp:']
    url_lower = url.lower()
    
    for scheme in skip_schemes:
        if url_lower.startswith(scheme):
            return True
    
    # Skip common file extensions that aren't content
    skip_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', 
                      '.css', '.js', '.xml', '.json', '.zip', '.exe']
    for ext in skip_extensions:
        if url_lower.endswith(ext):
            return True
    
    return False


class RobotsChecker:
    """Check robots.txt compliance."""
    
    def __init__(self, base_url: str):
        """
        Initialize robots.txt checker.
        
        Args:
            base_url: Base URL of the site
        """
        self.base_url = base_url
        self.parser = RobotFileParser()
        robots_url = urljoin(base_url, '/robots.txt')
        self.parser.set_url(robots_url)
        
        try:
            self.parser.read()
            self.enabled = True
        except Exception:
            self.enabled = False
    
    def can_fetch(self, url: str, user_agent: str = '*') -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent string
            
        Returns:
            True if allowed to fetch
        """
        if not self.enabled:
            return True  # If can't read robots.txt, assume allowed
        
        try:
            return self.parser.can_fetch(user_agent, url)
        except Exception:
            return True
