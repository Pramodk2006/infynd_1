"""
LLM-based Business Information Extractor using Phi3.5
Provides accurate extraction for contact info, people, certifications, and services
"""

import requests
import json
import re
from typing import Dict, List, Optional
from datetime import datetime

# Ollama API endpoint
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:7b"

PROXIES = {
    "http": None,
    "https": None
}


def call_ollama_with_json(prompt: str, text: str, model: str = DEFAULT_MODEL, max_retries: int = 2) -> Dict:
    """
    Call Ollama LLM and parse JSON response.
    
    Args:
        prompt: System prompt with extraction instructions
        text: Text to extract from
        model: Ollama model name
        max_retries: Number of retry attempts
        
    Returns:
        Parsed JSON dict
    """
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": f"{prompt}\n\nTEXT TO ANALYZE:\n{text[:8000]}\n\nJSON OUTPUT:",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent extraction
                        "num_predict": 2000
                    }
                },
                proxies=PROXIES,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                # Log raw response for debugging
                try:
                    with open("backend_debug.log", "a", encoding="utf-8") as f:
                        f.write(f"\n[{datetime.now().isoformat()}] RAW LLM RESPONSE:\n{generated_text}\n{'-'*80}\n")
                except:
                    pass
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                else:
                    # Try parsing the whole response
                    return json.loads(generated_text)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parse error (attempt {attempt + 1}): {e}"
            print(error_msg)
            try:
                with open("backend_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"\n[{datetime.now().isoformat()}] {error_msg}\n")
            except:
                pass
                
            if attempt < max_retries:
                continue
            else:
                return {}
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return {}
    
    return {}


def extract_contact_info_llm(text: str, company_name: str = "") -> Dict[str, any]:
    """
    Extract contact information using Phi3.5 LLM.
    
    Returns:
        Dict with emails, phones, address, VAT, company registration, etc.
    """
    prompt = f"""You are an expert at extracting contact information from company web content. Extract the following information and return ONLY a valid JSON object with these exact fields:

{{
    "email": "primary contact email or '-' if not found",
    "all_emails": ["list of all emails found, or ['-'] if none"],
    "phone": "primary phone number in original format or '-'",
    "sales_phone": "sales/customer phone if labeled as such, or '-'",
    "fax": "fax number if found, or '-'",
    "mobile": "mobile number if found, or '-'",
    "other_numbers": ["any additional phone numbers, or ['-'] if none"],
    "full_address": "complete physical address with postcode/zip or '-'",
    "hours_of_operation": "business hours if mentioned or '-'",
    "hq_indicator": true/false (true if text mentions headquarters/HQ/head office),
    "vat_number": "VAT number if found or '-'",
    "company_registration_number": "company registration/Companies House number or '-'"
}}

Rules:
- Keep phone numbers in their original format (don't reformat)
- For addresses, include street, city, and postcode/zip
- Return '-' for any field not found (not null or empty string)
- Extract ALL emails found (up to 5 most relevant)
- If multiple phone numbers exist, categorize them based on nearby labels (sales, fax, main, etc.)
- For company_registration_number, look for 8-digit UK company numbers or similar
- Return ONLY the JSON object, no additional text"""

    result = call_ollama_with_json(prompt, text, model=DEFAULT_MODEL)
    
    # Ensure all required fields exist with defaults
    defaults = {
        'email': '-',
        'all_emails': ['-'],
        'phone': '-',
        'sales_phone': '-',
        'fax': '-',
        'mobile': '-',
        'other_numbers': ['-'],
        'full_address': '-',
        'hours_of_operation': '-',
        'hq_indicator': False,
        'vat_number': '-',
        'company_registration_number': '-'
    }
    
    # Merge with defaults
    for key, default_value in defaults.items():
        if key not in result or not result[key]:
            result[key] = default_value
    
    return result


def extract_people_info_llm(text: str) -> List[Dict[str, str]]:
    """
    Extract people and their roles using Phi3.5 LLM.
    
    Returns:
        List of dicts with name, title, email, url
    """
    prompt = """You are an expert at extracting information about company team members from web content. Extract information about key people mentioned (executives, founders, directors, managers, etc.) and return ONLY a valid JSON object:

{
    "people": [
        {
            "name": "Full Name",
            "title": "Job Title/Role",
            "email": "person@company.com or '-'",
            "url": "profile URL or '-'"
        }
    ]
}

Rules:
- Extract up to 10 most relevant people
- Focus on leadership: CEO, CTO, CFO, Founders, Directors, Managers, Heads
- Include full names (first and last name)
- Match emails to people when they appear nearby
- Include LinkedIn or team page URLs if mentioned
- Return '-' for missing fields (not null or empty)
- Return empty array if no people found: {"people": []}
- Return ONLY the JSON object, no additional text"""

    result = call_ollama_with_json(prompt, text, model=DEFAULT_MODEL)
    
    people = result.get('people', [])
    
    # Ensure all fields exist
    for person in people:
        person.setdefault('name', '-')
        person.setdefault('title', '-')
        person.setdefault('email', '-')
        person.setdefault('url', '-')
    
    return people[:10] if people else []


def extract_certifications_llm(text: str) -> List[str]:
    """
    Extract certifications and compliance standards using Phi3.5 LLM.
    
    Returns:
        List of certification names
    """
    prompt = """You are an expert at identifying business certifications, compliance standards, and accreditations from company web content. Extract all mentioned certifications and return ONLY a valid JSON object:

{
    "certifications": ["ISO 9001", "ISO 27001", "GDPR Compliant", "SOC 2", "etc."]
}

Common certifications to look for:
- ISO standards (ISO 9001, ISO 27001, ISO 14001, etc.)
- Security: SOC 2, PCI DSS, Cyber Essentials
- Privacy: GDPR, CCPA, Privacy Shield
- Industry-specific: CE, FDA, GMP, HIPAA, FCA
- Quality: Six Sigma, Investors in People
- Environmental: B Corp, Carbon Neutral

Rules:
- Extract certification names as they appear
- Include version numbers if mentioned (e.g., "ISO 9001:2015")
- Return empty array if no certifications found: {"certifications": []}
- Return ONLY the JSON object, no additional text"""

    result = call_ollama_with_json(prompt, text, model=DEFAULT_MODEL)
    
    certs = result.get('certifications', [])
    return certs if certs else ['-']


def extract_services_llm(text: str) -> List[Dict[str, str]]:
    """
    Extract services and solutions using Phi3.5 LLM.
    
    Returns:
        List of dicts with service name and type
    """
    prompt = """You are an expert at identifying products and services offered by companies. Extract the main services/products and categorize them. Return ONLY a valid JSON object:

{
    "services": [
        {
            "service": "Service or Product Name",
            "type": "Product" or "Service" or "Solution"
        }
    ]
}

Rules:
- Extract up to 15 main services/products
- Categorize as "Product", "Service", or "Solution"
- Be specific (e.g., "Cloud Hosting" not just "Hosting")
- Prioritize services explicitly listed in service/product sections
- Return empty array if no services found: {"services": []}
- Return ONLY the JSON object, no additional text"""

    result = call_ollama_with_json(prompt, text, model=DEFAULT_MODEL)
    
    services = result.get('services', [])
    
    # Ensure all fields exist
    for service in services:
        service.setdefault('service', '-')
        service.setdefault('type', 'Service')
    
    return services[:15] if services else []


def extract_company_acronym_llm(company_name: str, text: str) -> str:
    """
    Extract company acronym using Phi3.5 LLM.
    
    Returns:
        Acronym or '-'
    """
    if not company_name or len(company_name) < 3:
        return '-'
    
    prompt = f"""Given the company name "{company_name}" and the following text, extract the company's official acronym or abbreviated name if one exists. Return ONLY a valid JSON object:

{{
    "acronym": "ABC" or "-" if none exists
}}

Rules:
- Return the OFFICIAL acronym used by the company (usually all caps)
- Common patterns: First letters of words (e.g., IBM, NASA)
- Return "-" if no acronym is found or commonly used
- Return ONLY the JSON object, no additional text"""

    result = call_ollama_with_json(prompt, text[:2000], model=DEFAULT_MODEL)
    
    acronym = result.get('acronym', '-')
    return acronym if acronym and acronym != '-' else '-'


def generate_tags_llm(text: str, sector: str = '', industry: str = '') -> List[str]:
    """
    Generate relevant business tags using Phi3.5 LLM.
    
    Returns:
        List of tags
    """
    prompt = f"""You are an expert at analyzing company web content and generating relevant descriptive tags. The company is in the {sector} sector and {industry} industry.

Extract and generate 5-10 relevant tags that describe the company's focus, technologies, target market, and key characteristics. Return ONLY a valid JSON object:

{{
    "tags": ["Tag1", "Tag2", "Tag3", "etc."]
}}

Rules:
- Generate 5-10 specific, relevant tags
- Include technology keywords (e.g., "AI", "Cloud", "SaaS")
- Include market focus (e.g., "B2B", "Enterprise", "SME")
- Include specialty areas (e.g., "Cybersecurity", "Analytics")
- Keep tags concise (1-3 words each)
- Return ONLY the JSON object, no additional text"""

    result = call_ollama_with_json(prompt, text[:3000], model=DEFAULT_MODEL)
    
    tags = result.get('tags', [])
    return tags[:10] if tags else ['-']


def extract_all_business_info_llm(
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
    Master function to extract all business information using Phi3.5 LLM, with confidence and explanation for each field.
    """
    print(f"🤖 Extracting business info using Phi3.5 LLM for {company_name}...")

    # Prompt for all fields with confidence and explanation
    prompt = f"""
You are an expert at extracting structured business information from company web content. 
The company name is "{company_name}" and the domain is "{domain}".
Known classification: Sector: {sector}, Industry: {industry}, Sub-Industry: {sub_industry}.

For each field below, extract:
- value: the best answer (or '-' if not found)
- confidence: a number from 0.0 (guess) to 1.0 (certain)
- explanation: a short natural-language justification for why you chose this value (max 2 sentences)

Return ONLY a valid JSON object with this structure:
{{
  "fields": {{
    "company_name": {{"value": "Official Company Name (extracted from text)", "confidence": 0.9, "explanation": "..."}},
    "acronym": {{"value": "ABC", "confidence": 0.9, "explanation": "..."}},
    "short_description": {{"value": "A single compelling sentence (elevator pitch) describing exactly what the company does. Generate this from the text.", "confidence": 0.9, "explanation": "Generated elevator pitch"}},
    "long_description": {{"value": "A detailed 2-3 sentence description of the company's business, products, and mission (generate from text)", "confidence": 0.8, "explanation": "..."}},
    "email": {{"value": "primary@email.com", "confidence": 0.9, "explanation": "..."}},
    "all_emails": {{"value": ["email1@test.com", "email2@test.com"], "confidence": 0.9, "explanation": "..."}},
    "phone": {{"value": "+1 234 567 890", "confidence": 0.9, "explanation": "..."}},
    "sales_phone": {{"value": "+1 234 567 890", "confidence": 0.9, "explanation": "..."}},
    "fax": {{"value": "+1 234 567 899", "confidence": 0.9, "explanation": "..."}},
    "mobile": {{"value": "+1 987 654 321", "confidence": 0.9, "explanation": "..."}},
    "other_numbers": {{"value": ["+1 234...", "+1 567..."], "confidence": 0.8, "explanation": "..."}},
    "full_address": {{"value": "123 Main St, City, Country", "confidence": 0.9, "explanation": "..."}},
    "hours_of_operation": {{"value": "Mon-Fri 9-5", "confidence": 0.8, "explanation": "..."}},
    "hq_indicator": {{"value": true, "confidence": 0.9, "explanation": "..."}},
    "company_registration_number": {{"value": "12345678", "confidence": 0.9, "explanation": "..."}},
    "vat_number": {{"value": "GB123456789", "confidence": 0.9, "explanation": "..."}},
    "domain_status": {{"value": "Active", "confidence": 0.9, "explanation": "Active/Parked/For Sale"}},
    "sector": {{"value": "{sector}", "confidence": 0.9, "explanation": "Pre-classified"}},
    "industry": {{"value": "{industry}", "confidence": 0.9, "explanation": "Pre-classified"}},
    "sub_industry": {{"value": "{sub_industry}", "confidence": 0.9, "explanation": "Pre-classified"}},
    "sic_code": {{"value": "{sic_code}", "confidence": 0.9, "explanation": "Pre-classified"}},
    "sic_text": {{"value": "{sic_text}", "confidence": 0.9, "explanation": "Pre-classified"}},
    "tags": {{"value": ["Tag1", "Tag2"], "confidence": 0.8, "explanation": "..."}},
    "certifications": {{"value": ["ISO 9001"], "confidence": 0.8, "explanation": "..."}},
    "people": {{"value": [{{"name": "John Doe", "title": "CEO", "email": "-", "url": "-"}}], "confidence": 0.8, "explanation": "..."}},
    "services": {{"value": [{{"service": "Cloud Hosting", "type": "Service"}}], "confidence": 0.8, "explanation": "..."}},
    "logo_url": {{"value": "-", "confidence": 0.0, "explanation": "Cannot extract images"}}
  }}
}}

Rules:
- If a field is not found, set value to '-' (or [] for arrays, false for boolean) and confidence to 0.0
- Explanations should mention evidence (e.g., "Found in About Us section", "No mention in text")
- Return ONLY the JSON object, no extra text
"""

    result = call_ollama_with_json(prompt, text, model=DEFAULT_MODEL)
    fields = result.get('fields', {})

    # Helper to safely get field data
    def get_data(field_name, default_value='-'):
        f = fields.get(field_name, {})
        return {
            'value': f.get('value', default_value),
            'confidence': f.get('confidence', 0.0),
            'explanation': f.get('explanation', 'Not found')
        }

    # Construct the final response matching frontend expectations
    # Note: The frontend expects these keys to be objects with {value, confidence, explanation}
    # thanks to our previous fix in EnhancedSummaryCard.jsx
    
    response = {
        'company_name': get_data('company_name', company_name),
        'acronym': get_data('acronym'),
        'generated_summary': {'value': long_description, 'confidence': 1.0, 'explanation': 'Generated by initial text summarization'},
        'short_description': get_data('short_description', short_description),
        'long_description': get_data('long_description', long_description),
        'email': get_data('email'),
        'all_emails': get_data('all_emails', []),
        'phone': get_data('phone'),
        'sales_phone': get_data('sales_phone'),
        'fax': get_data('fax'),
        'mobile': get_data('mobile'),
        'other_numbers': get_data('other_numbers', []),
        'full_address': get_data('full_address'),
        'hours_of_operation': get_data('hours_of_operation'),
        'hq_indicator': get_data('hq_indicator', False),
        'company_registration_number': get_data('company_registration_number'),
        'vat_number': get_data('vat_number'),
        'sector': get_data('sector', sector),
        'industry': get_data('industry', industry),
        'sub_industry': get_data('sub_industry', sub_industry),
        'sic_code': get_data('sic_code', sic_code),
        'sic_text': get_data('sic_text', sic_text),
        'tags': get_data('tags', []),
        'certifications': get_data('certifications', []),
        'people': get_data('people', []),
        'services': get_data('services', []),
        'logo_url': get_data('logo_url'),
        'domain_status': get_data('domain_status', 'Active'),
        
        # Metadata
        'domain': {'value': domain, 'confidence': 1.0, 'explanation': 'From source URL'},
        'extraction_timestamp': datetime.now().isoformat(),
        'text_length': len(text) if text else 0
    }

    return response
