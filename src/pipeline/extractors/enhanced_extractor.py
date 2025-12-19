"""
Enhanced Business Information Extractor
Extracts comprehensive company details from raw text
"""

import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
import json


def extract_contact_info(text: str) -> Dict[str, any]:
    """
    Extract all contact information from text using regex patterns.
    
    Returns:
        Dict with emails, phones, VAT, company registration, etc.
    """
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = list(set(re.findall(email_pattern, text)))
    
    # Phone patterns (international and UK)
    phone_patterns = [
        r'\+\d{1,3}[\s\-\.]?\d{1,4}[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,4}',  # International
        r'\(\d{3,5}\)[\s\-]?\d{3,4}[\s\-]?\d{3,4}',  # (020) 1234 5678
        r'\d{3,5}[\s\-]\d{3,4}[\s\-]\d{3,4}',  # 020 1234 5678
        r'\d{10,}',  # 10+ digit numbers
    ]
    
    phones = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        phones.extend(matches)
    
    # Clean and deduplicate phones
    phones = [p.strip() for p in phones if len(p.replace(' ', '').replace('-', '').replace('.', '')) >= 10]
    phones = list(set(phones))[:5]  # Limit to 5 unique numbers
    
    # VAT number (UK, EU formats)
    vat_pattern = r'\b(?:VAT|V\.A\.T\.?|VAT\s*No\.?|VAT\s*Number)[:\s]*([A-Z]{2}\s?\d{9,12}|\d{9,12})\b'
    vat_matches = re.findall(vat_pattern, text, re.IGNORECASE)
    vat_number = vat_matches[0] if vat_matches else None
    
    # Company Registration Number (UK format)
    company_reg_patterns = [
        r'\b(?:Company\s*No\.?|Registration\s*No\.?|Reg\.?\s*No\.?|Registered\s*Number)[:\s]*(\d{8})\b',
        r'\b(?:Companies\s*House)[:\s]*(\d{8})\b',
    ]
    
    company_reg = None
    for pattern in company_reg_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            company_reg = matches[0]
            break
    
    # Address pattern (simplified - looks for postal codes)
    uk_postcode_pattern = r'\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b'
    us_zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
    
    address_contexts = []
    
    # Find UK postcodes with context
    for match in re.finditer(uk_postcode_pattern, text):
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 20)
        context = text[start:end].strip()
        address_contexts.append(context)
    
    # Find US ZIP codes with context
    for match in re.finditer(us_zip_pattern, text):
        # Check if it's near words like "address", "located", "street"
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 20)
        context = text[start:end]
        if re.search(r'address|street|located|office|headquarters|hq', context, re.IGNORECASE):
            address_contexts.append(text[start:end].strip())
    
    full_address = address_contexts[0] if address_contexts else None
    
    # Hours of operation
    hours_pattern = r'(?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)[\s\-]*(?:to|-)[\s\-]*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*:?\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?\s*[-–]\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?'
    hours_matches = re.findall(hours_pattern, text, re.IGNORECASE)
    hours_of_operation = hours_matches[0] if hours_matches else None
    
    # HQ indicator
    hq_indicator = bool(re.search(r'\b(?:headquarters|head\s*office|HQ|main\s*office)\b', text, re.IGNORECASE))
    
    # Categorize phones
    main_phone = phones[0] if phones else None
    sales_phone = None
    fax = None
    other_numbers = []
    
    # Look for labeled phones
    for phone in phones:
        # Find context around phone
        phone_escaped = re.escape(phone)
        pattern = r'(.{0,30})' + phone_escaped + r'(.{0,30})'
        context_match = re.search(pattern, text, re.IGNORECASE)
        
        if context_match:
            context = context_match.group(1) + context_match.group(2)
            context_lower = context.lower()
            
            if 'sales' in context_lower or 'sell' in context_lower:
                sales_phone = phone
            elif 'fax' in context_lower:
                fax = phone
            elif phone != main_phone and phone != sales_phone and phone != fax:
                other_numbers.append(phone)
    
    return {
        'email': emails[0] if emails else '-',
        'all_emails': emails if emails else ['-'],
        'phone': main_phone or '-',
        'sales_phone': sales_phone or '-',
        'fax': fax or '-',
        'mobile': '-',  # Hard to distinguish without more context
        'other_numbers': other_numbers if other_numbers else ['-'],
        'full_address': full_address or '-',
        'hours_of_operation': hours_of_operation or '-',
        'hq_indicator': hq_indicator,
        'vat_number': vat_number or '-',
        'company_registration_number': company_reg or '-'
    }


def extract_people_info(text: str) -> List[Dict[str, str]]:
    """
    Extract people names and titles using pattern matching.
    Simplified version without spaCy dependency.
    """
    people = []
    
    # Common title patterns
    title_patterns = [
        r'\b(CEO|CTO|CFO|COO|CMO|CIO|Director|Manager|Head\s+of|VP|President|Founder|Co-Founder|Partner|Chairman|Managing\s+Director)\b',
    ]
    
    # Name pattern (capitalized words, 2-3 parts)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    
    # Find titles with nearby names
    for title_pattern in title_patterns:
        for title_match in re.finditer(title_pattern, text, re.IGNORECASE):
            title = title_match.group(0)
            
            # Look for name near title (within 50 chars before or after)
            start = max(0, title_match.start() - 50)
            end = min(len(text), title_match.end() + 50)
            context = text[start:end]
            
            # Find names in context
            name_matches = re.findall(name_pattern, context)
            
            for name in name_matches:
                # Skip common false positives
                if name.lower() not in ['the team', 'our team', 'business computer', 'meet the']:
                    # Try to find email for this person
                    person_email = extract_email_for_person(text, name)
                    
                    people.append({
                        'name': name,
                        'title': title,
                        'email': person_email or '-',
                        'url': '-'
                    })
    
    # Deduplicate by name
    seen_names = set()
    unique_people = []
    for person in people:
        if person['name'] not in seen_names:
            seen_names.add(person['name'])
            unique_people.append(person)
    
    return unique_people[:10]  # Limit to 10 people


def extract_email_for_person(text: str, name: str) -> Optional[str]:
    """Find email associated with a person's name"""
    # Look for email within 100 chars of name
    name_escaped = re.escape(name)
    pattern = name_escaped + r'.{0,100}?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Try reverse (email before name)
    pattern = r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}).{0,100}?' + name_escaped
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None


def extract_certifications(text: str) -> List[str]:
    """Extract certifications and compliance badges from text"""
    cert_patterns = {
        r'ISO\s*\d{5}': 'ISO',
        r'ISO/IEC\s*\d{5}': 'ISO/IEC',
        r'SOC\s*\d\s*Type\s*[I|II|1|2]': 'SOC',
        r'GDPR\s*[Cc]ompliant': 'GDPR Compliant',
        r'HIPAA\s*[Cc]ompliant': 'HIPAA Compliant',
        r'PCI\s*DSS': 'PCI DSS',
        r'Cyber\s*Essentials(?:\s*Plus)?': 'Cyber Essentials',
        r'BS\s*\d{4,5}': 'British Standard',
        r'NIST': 'NIST',
        r'FedRAMP': 'FedRAMP',
        r'CSA\s*STAR': 'CSA STAR',
        r'CREST': 'CREST',
    }
    
    certifications = []
    
    for pattern, cert_name in cert_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Use the actual match for ISO numbers, standard name for others
            if 'ISO' in cert_name or 'SOC' in cert_name or 'BS' in cert_name:
                certifications.extend([m.strip() for m in matches])
            else:
                certifications.append(cert_name)
    
    return list(set(certifications)) if certifications else ['-']


def extract_services(text: str) -> List[Dict[str, str]]:
    """
    Extract services offered by the company.
    Uses section headers and keyword matching.
    """
    services = []
    
    # Common service section headers
    section_patterns = [
        r'(?:Our\s+)?Services?:?\s*\n(.{0,500})',
        r'What\s+We\s+(?:Do|Offer):?\s*\n(.{0,500})',
        r'Solutions?:?\s*\n(.{0,500})',
        r'Products?:?\s*\n(.{0,500})',
    ]
    
    # Extract sections
    service_texts = []
    for pattern in section_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        service_texts.extend(matches)
    
    # Common service keywords with types
    service_keywords = {
        'consulting': 'Consulting',
        'support': 'Support',
        'training': 'Training',
        'implementation': 'Implementation',
        'managed services': 'Managed Services',
        'cloud': 'Software',
        'software': 'Software',
        'development': 'Software',
        'security': 'Security',
        'compliance': 'Compliance',
        'payroll': 'Software',
        'hr': 'Software',
        'crm': 'Software',
        'analytics': 'Software',
    }
    
    # Extract services from sections
    for service_text in service_texts:
        for keyword, service_type in service_keywords.items():
            if re.search(r'\b' + keyword + r'\b', service_text, re.IGNORECASE):
                service_name = keyword.title()
                services.append({
                    'service': service_name,
                    'type': service_type
                })
    
    # Deduplicate
    seen = set()
    unique_services = []
    for service in services:
        key = (service['service'], service['type'])
        if key not in seen:
            seen.add(key)
            unique_services.append(service)
    
    return unique_services[:10] if unique_services else [{'service': '-', 'type': '-'}]


def generate_tags(text: str, sector: str, industry: str) -> List[str]:
    """Generate relevant tags from text and classification"""
    tags = set()
    
    # Add sector and industry as base tags
    if sector and sector != '-':
        tags.add(sector.lower().replace(' & ', '-').replace(' ', '-'))
    
    if industry and industry != '-':
        for word in industry.lower().split():
            if len(word) > 3 and word not in ['the', 'and', 'services']:
                tags.add(word)
    
    # Technology keywords
    tech_keywords = [
        'cloud', 'saas', 'ai', 'ml', 'analytics', 'automation',
        'mobile', 'web', 'api', 'platform', 'software', 'data',
        'security', 'compliance', 'gdpr', 'iso', 'cybersecurity'
    ]
    
    for keyword in tech_keywords:
        if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
            tags.add(keyword)
    
    # Business model keywords
    if re.search(r'\bfree\b.*\bforever\b|\bfreemium\b', text, re.IGNORECASE):
        tags.add('free')
    
    if re.search(r'\benterprise\b', text, re.IGNORECASE):
        tags.add('enterprise')
    
    if re.search(r'\bsmb\b|\bsmall\s+business\b', text, re.IGNORECASE):
        tags.add('smb')
    
    # Geographic keywords
    geo_keywords = ['uk', 'usa', 'india', 'europe', 'global', 'international']
    for geo in geo_keywords:
        if re.search(r'\b' + geo + r'\b', text, re.IGNORECASE):
            tags.add(geo)
    
    return sorted(list(tags))[:10]  # Limit to 10 tags


def extract_company_acronym(company_name: str, text: str) -> str:
    """Extract company acronym from name or find it in text"""
    if not company_name or company_name == '-':
        return '-'
    
    # Try to find acronym in text (e.g., "BCS" near "Business Computer Solutions")
    name_words = company_name.split()
    if len(name_words) >= 2:
        acronym = ''.join([word[0].upper() for word in name_words if len(word) > 2])
        
        # Check if acronym appears in text
        if re.search(r'\b' + acronym + r'\b', text):
            return acronym
    
    return '-'


def extract_logo_url_from_html(html_content: str, domain: str) -> str:
    """Extract logo URL from HTML content"""
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Common logo selectors
        logo = (
            soup.find('img', class_=re.compile(r'logo', re.I)) or
            soup.find('img', id=re.compile(r'logo', re.I)) or
            soup.find('img', alt=re.compile(r'logo', re.I)) or
            soup.find('img', {'data-testid': 'logo'}) or
            soup.select_one('header img') or
            soup.select_one('.header img') or
            soup.select_one('.navbar img')
        )
        
        if logo and logo.get('src'):
            logo_src = logo['src']
            
            # Convert relative URLs to absolute
            if logo_src.startswith('//'):
                return 'https:' + logo_src
            elif logo_src.startswith('/'):
                return f"https://{domain}{logo_src}"
            elif logo_src.startswith('http'):
                return logo_src
            else:
                return f"https://{domain}/{logo_src}"
        
    except ImportError:
        # BeautifulSoup not available
        pass
    except Exception as e:
        print(f"Error extracting logo: {e}")
    
    return '-'


def extract_all_business_info(
    text: str,
    html_content: str = None,
    domain: str = None,
    company_name: str = None,
    short_description: str = None,
    long_description: str = None,
    sector: str = None,
    industry: str = None,
    sub_industry: str = None,
    sic_code: str = None,
    sic_text: str = None
) -> Dict:
    """
    Master function to extract all business information.
    
    Args:
        text: Raw text content
        html_content: Optional HTML for logo extraction
        domain: Company domain
        company_name: Company name
        short_description: Short description
        long_description: Long description (from Qwen)
        sector: Classification sector
        industry: Classification industry
        sub_industry: Classification sub-industry
        sic_code: SIC code
        sic_text: SIC description
        
    Returns:
        Complete business information dict
    """
    # Extract contact info
    contact = extract_contact_info(text)
    
    # Extract people
    people = extract_people_info(text)
    
    # Extract certifications
    certifications = extract_certifications(text)
    
    # Extract services
    services = extract_services(text)
    
    # Generate tags
    tags = generate_tags(text, sector or '', industry or '')
    
    # Extract acronym
    acronym = extract_company_acronym(company_name or '', text)
    
    # Extract logo (if HTML available)
    logo_url = '-'
    if html_content and domain:
        logo_url = extract_logo_url_from_html(html_content, domain)
    
    # Determine domain status (active if we got data)
    domain_status = 'active' if text else 'inactive'
    
    return {
        # Mandatory classification fields
        'domain': domain or '-',
        'long_description': long_description or '-',
        'short_description': short_description or '-',
        'sic_code': sic_code or '-',
        'sic_text': sic_text or '-',
        'sub_industry': sub_industry or '-',
        'industry': industry or '-',
        'sector': sector or '-',
        'tags': tags if tags else ['-'],
        
        # Company identity
        'company_name': company_name or '-',
        'domain_status': domain_status,
        'acronym': acronym,
        'logo_url': logo_url,
        'company_registration_number': contact['company_registration_number'],
        'vat_number': contact['vat_number'],
        
        # Contact information
        'full_address': contact['full_address'],
        'phone': contact['phone'],
        'sales_phone': contact['sales_phone'],
        'fax': contact['fax'],
        'mobile': contact['mobile'],
        'other_numbers': contact['other_numbers'],
        'email': contact['email'],
        'all_emails': contact['all_emails'],
        'hours_of_operation': contact['hours_of_operation'],
        'hq_indicator': contact['hq_indicator'],
        
        # People
        'people': people if people else [{'name': '-', 'title': '-', 'email': '-', 'url': '-'}],
        
        # Certifications
        'certifications': certifications,
        
        # Services
        'services': services,
        
        # Raw text
        'text': text[:5000] if text else '-'  # Limit for display
    }
