"""
Enhanced Data Extraction Module
Extracts comprehensive business information from raw text using Phi3.5 LLM
- Contact details (phone, email, address, VAT, company registration)
- People information (names, titles, emails)
- Certifications and compliance
- Services offered
- Logo and images
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime
from src.pipeline.extractors.llm_extractor import extract_all_business_info_llm


# ============================================================================
# CONTACT INFORMATION EXTRACTION
# ============================================================================

def extract_emails(text: str) -> List[str]:
    """Extract all email addresses from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    # Remove common noise emails
    noise = ['example@', 'test@', 'noreply@', 'no-reply@']
    return [e for e in set(emails) if not any(n in e.lower() for n in noise)][:5]


def extract_phones(text: str) -> List[str]:
    """Extract phone numbers (international and local formats)"""
    patterns = [
        r'\+\d{1,3}[\s-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}',  # International
        r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US format
        r'\d{4}[\s-]?\d{3}[\s-]?\d{3}',  # UK format
        r'\d{2}[\s-]?\d{4}[\s-]?\d{4}',  # Indian format
    ]
    
    phones = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    # Clean and deduplicate
    cleaned = [re.sub(r'\s+', ' ', p.strip()) for p in phones]
    return list(set(cleaned))[:5]


def extract_vat_number(text: str) -> Optional[str]:
    """Extract VAT registration number"""
    patterns = [
        r'\b(VAT|V\.A\.T\.?)\s*(?:No\.?|Number)?\s*:?\s*([A-Z]{2}\d{9,12})\b',
        r'\b(GB|IE|FR|DE)\s*\d{9,12}\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return None


def extract_company_registration(text: str) -> Optional[str]:
    """Extract company registration number"""
    patterns = [
        r'\b(?:Company\s*)?(?:Registration|Reg\.?)\s*(?:No\.?|Number)?\s*:?\s*(\d{8,10})\b',
        r'\b(?:Registered|Incorporated)\s*(?:in\s*England\s*(?:and\s*Wales)?\s*)?(?:No\.?|Number)?\s*:?\s*(\d{8,10})\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_address(text: str) -> Optional[str]:
    """Extract full address (best effort)"""
    # Look for common address patterns
    patterns = [
        r'(?:Address|Located at|Headquarters|HQ)[:\s]+([^\.]+?(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Way|Place|Square|Court|Ct)[^\.]+?(?:[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}|\d{5}(?:-\d{4})?))',
        r'\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln)[^\.]+?(?:[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}|\d{5})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            addr = match.group(1) if len(match.groups()) > 0 else match.group(0)
            return re.sub(r'\s+', ' ', addr.strip())[:200]
    
    return None


def extract_hours_of_operation(text: str) -> Optional[str]:
    """Extract business hours"""
    pattern = r'(?:Opening|Business|Office)?\s*Hours?\s*:?\s*((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[^\.]+?\d{1,2}(?:am|pm))'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()[:100]
    return None


# ============================================================================
# PEOPLE INFORMATION EXTRACTION
# ============================================================================

def extract_people(text: str) -> List[Dict[str, str]]:
    """Extract people names and titles"""
    people = []
    
    # Pattern: "Name, Title" or "Title: Name"
    title_patterns = [
        r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[,-]\s*(CEO|CTO|CFO|COO|Director|Manager|Head|Founder|President|VP|Vice President)',
        r'\b(CEO|CTO|CFO|COO|Director|Manager|Head|Founder|President|VP|Vice President)\s*[:-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
    ]
    
    for pattern in title_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if 'CEO' in match[1].upper() or 'Director' in match[1].lower():
                people.append({
                    'name': match[0].strip() if not match[0].isupper() else match[1].strip(),
                    'title': match[1].strip() if match[0].isupper() else match[0].strip(),
                    'email': '-',
                    'url': '-'
                })
    
    return people[:5]  # Limit to 5 people


# ============================================================================
# CERTIFICATIONS EXTRACTION
# ============================================================================

def extract_certifications(text: str) -> List[str]:
    """Extract certifications and compliance standards"""
    cert_patterns = [
        r'ISO\s*\d{5}(?:-\d)?',
        r'SOC\s*\d',
        r'GDPR\s*[Cc]ompliant',
        r'HIPAA\s*[Cc]ompliant',
        r'PCI\s*DSS',
        r'Cyber\s*Essentials(?:\s*Plus)?',
        r'CE\s*Mark',
        r'FDA\s*Approved',
        r'CREST\s*Accredited',
    ]
    
    certs = []
    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        certs.extend([m.strip() for m in matches])
    
    return list(set(certs))[:10]


# ============================================================================
# SERVICES EXTRACTION
# ============================================================================

def extract_services(text: str, company_name: str = "") -> List[Dict[str, str]]:
    """Extract services offered"""
    services = []
    
    # Look for service sections
    service_patterns = [
        r'(?:Our|We offer|We provide)\s+([^\.]+?(?:service|solution|product|platform|software|system)s?)',
        r'(?:Services|Solutions|Products)\s*:?\s*([^\.]+)',
    ]
    
    for pattern in service_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            service_text = match.strip()
            # Split on commas or "and"
            parts = re.split(r',|\sand\s', service_text)
            for part in parts:
                clean = part.strip()
                if len(clean) > 5 and len(clean) < 100:
                    services.append({
                        'service': clean,
                        'type': classify_service_type(clean)
                    })
    
    return services[:10]


def classify_service_type(service: str) -> str:
    """Classify service type"""
    service_lower = service.lower()
    
    if any(w in service_lower for w in ['software', 'app', 'platform', 'system', 'tool']):
        return 'Software'
    elif any(w in service_lower for w in ['consulting', 'advisory', 'strategy']):
        return 'Consulting'
    elif any(w in service_lower for w in ['support', 'maintenance', 'managed']):
        return 'Support'
    elif any(w in service_lower for w in ['training', 'education', 'workshop']):
        return 'Training'
    else:
        return 'Service'


# ============================================================================
# TAGS GENERATION
# ============================================================================

def generate_tags(text: str, industry: str = "", sector: str = "") -> List[str]:
    """Generate relevant tags from text"""
    tags = set()
    
    # Add industry/sector as tags
    if industry:
        tags.update(industry.lower().split())
    if sector:
        tags.update(sector.lower().split())
    
    # Extract keywords
    keywords = [
        'cloud', 'saas', 'ai', 'ml', 'automation', 'analytics', 'security',
        'mobile', 'web', 'api', 'platform', 'enterprise', 'smb', 'startup',
        'b2b', 'b2c', 'fintech', 'healthtech', 'edtech', 'hr', 'crm', 'erp'
    ]
    
    text_lower = text.lower()
    for keyword in keywords:
        if keyword in text_lower:
            tags.add(keyword)
    
    # Remove common words
    stopwords = {'and', 'the', 'for', 'with', 'services', 'solutions'}
    tags = {t for t in tags if t not in stopwords and len(t) > 2}
    
    return sorted(list(tags))[:10]


# ============================================================================
# ACRONYM EXTRACTION
# ============================================================================

def extract_acronym(company_name: str, text: str) -> Optional[str]:
    """Extract company acronym"""
    # First, check if company name itself is an acronym
    if company_name and company_name.isupper() and len(company_name) <= 5:
        return company_name
    
    # Look for acronym in parentheses after company name
    if company_name:
        pattern = rf'{re.escape(company_name)}\s*\(([A-Z]{{2,5}})\)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # Look for common acronym patterns
    pattern = r'\b([A-Z]{2,5})\b(?:\s+(?:is|provides|offers))'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    
    return None


# ============================================================================
# LOGO URL EXTRACTION
# ============================================================================

def extract_logo_url(source_data: dict, domain: str) -> Optional[str]:
    """Extract logo URL from source data"""
    # This would need HTML parsing - simplified version
    # In a real implementation, parse HTML and look for:
    # - <img class="logo" src="...">
    # - <link rel="icon" href="...">
    # - Open Graph image
    
    # For now, construct common logo URL patterns
    common_paths = [
        f'https://{domain}/logo.png',
        f'https://{domain}/assets/logo.png',
        f'https://{domain}/images/logo.png',
        f'https://{domain}/static/logo.png',
    ]
    
    # Return first one (in real app, we'd check if URL is accessible)
    return None  # Placeholder - needs HTML parsing


# ============================================================================
# MAIN EXTRACTION FUNCTION
# ============================================================================

def extract_all_data(company_folder: str, classification_result: dict = None) -> dict:
    """
    Extract all available data from company sources using Phi3.5 LLM.
    
    Args:
        company_folder: Path to company folder (e.g., 'data/outputs/kredily')
        classification_result: Classification output with sector/industry/sic
        
    Returns:
        Complete data extraction result using LLM-based extraction
    """
    output_path = Path(company_folder)
    sources_path = output_path / "sources"
    
    if not sources_path.exists():
        return create_empty_result()
    
    # Combine all text from all sources
    all_text = ""
    html_content = None
    metadata = {}
    domain = output_path.name
    
    for json_file in sources_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text
            if 'content' in data and 'raw_text' in data['content']:
                all_text += " " + data['content']['raw_text']
            
            # Extract HTML (for logo extraction)
            if not html_content and 'content' in data and 'html' in data['content']:
                html_content = data['content']['html']
            
            # Extract metadata
            if 'metadata' in data and not metadata:
                metadata = data['metadata']
            
            # Extract domain from source
            if 'source' in data and 'uri' in data['source']:
                uri = data['source']['uri']
                if 'http' in uri:
                    try:
                        # robust domain extraction
                        from urllib.parse import urlparse
                        parsed = urlparse(uri)
                        domain = parsed.netloc.replace('www.', '')
                    except:
                        domain = uri.split('/')[2].replace('www.', '')
        
        except Exception as e:
            continue
    
    # Extract company name
    company_name = metadata.get('title', '').split('-')[0].strip() if metadata.get('title') else domain
    
    # Get classification results
    final_pred = classification_result.get('final_prediction', {}) if classification_result else {}
    
    # Use Generated Summary for extraction if available (Chained LLM approach)
    # This ensures the details are extracted from the clean summary rather than raw text
    generated_summary = classification_result.get('summary', '') if classification_result else ''
    extraction_source = generated_summary if generated_summary and len(generated_summary) > 100 else all_text
    
    # Use LLM-based extraction for all fields
    result = extract_all_business_info_llm(
        text=extraction_source,
        html_content=html_content,
        domain=domain,
        company_name=company_name,
        short_description=metadata.get('description', '-') if metadata else '-',
        long_description=classification_result.get('summary', '-') if classification_result else '-',
        sector=final_pred.get('sector', '-'),
        industry=final_pred.get('industry', '-'),
        sub_industry=final_pred.get('sub_industry', '-'),
        sic_code=final_pred.get('sic_code', '-'),
        sic_text=final_pred.get('sic_description', '-')
    )
    
    # Add metadata
    result['extraction_timestamp'] = datetime.now().isoformat()
    result['text_length'] = len(all_text)
    result['classification'] = classification_result if classification_result else None
    
    return result


def create_empty_result() -> dict:
    """Create empty result with all fields set to '-'"""
    return {
        'domain': '-',
        'long_description': '-',
        'short_description': '-',
        'sic_code': '-',
        'sic_text': '-',
        'sub_industry': '-',
        'industry': '-',
        'sector': '-',
        'tags': [],
        'domain_status': '-',
        'company_registration_number': '-',
        'vat_number': '-',
        'company_name': '-',
        'acronym': '-',
        'logo_url': '-',
        'full_address': '-',
        'phone': '-',
        'sales_phone': '-',
        'fax': '-',
        'mobile': '-',
        'other_numbers': [],
        'email': '-',
        'all_emails': [],
        'hours_of_operation': '-',
        'hq_indicator': False,
        'people': [{'name': '-', 'title': '-', 'email': '-', 'url': '-'}],
        'certifications': ['-'],
        'services': [{'service': '-', 'type': '-'}],
        'text_preview': '-',
        'text_length': 0
    }
