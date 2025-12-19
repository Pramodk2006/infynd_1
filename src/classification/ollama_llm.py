"""
Ollama LLM for classification using local models.
"""

import requests
import json
import re
from typing import List, Dict, Optional

# Ollama API endpoint
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:7b"

# Proxy bypass
PROXIES = {
    "http": None,
    "https": None
}


def check_ollama_available() -> bool:
    """Check if Ollama is running."""
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            proxies=PROXIES,
            timeout=3
        )
        return response.status_code == 200
    except Exception:
        return False


def get_available_models() -> List[str]:
    """Get list of available models."""
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            proxies=PROXIES,
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        return []
    except Exception:
        return []


def classify_with_llm(
    company_text: str,
    candidates: List[Dict],
    company_name: str = "the company",
    model: str = DEFAULT_MODEL
) -> Optional[Dict]:
    """
    Use Ollama LLM to select best classification from candidates.
    
    Args:
        company_text: Company description text
        candidates: List of candidate classifications from embeddings
        company_name: Name of the company
        model: Ollama model to use
        
    Returns:
        Dict with selected classification or None
    """
    if not candidates:
        return None
    
    # Build prompt
    options_text = []
    for i, c in enumerate(candidates[:5], 1):  # Top 5 candidates (reduced from 10)
        options_text.append(
            f"{i}. {c['sub_industry']} (Industry: {c['industry']}, Sector: {c['sector']}) - Score: {c['similarity']:.3f}"
        )
    
    prompt = f"""You are an expert business analyst. Classify this company by selecting the BEST option from the list below.

Company: {company_name}

Description:
{company_text[:2000]}

OPTIONS (choose the number of the best match):
{chr(10).join(options_text)}

INSTRUCTIONS:
- Read the company description carefully
- Choose the option number (1-{len(options_text)}) that best matches
- Respond with ONLY a JSON object in this format:
{{"choice": <number>, "confidence": <0.0-1.0>, "reasoning": "<brief explanation>"}}

Your JSON response:"""

    try:
        print(f"   Sending request to Ollama {model}...")
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 200
                }
            },
            proxies=PROXIES,
            timeout=120  # Increased to 120 seconds
        )
        
        if response.status_code != 200:
            return None
        
        result = response.json()
        answer = result.get('response', '').strip()
        
        # Parse JSON from response
        json_match = re.search(r'\{[^{}]*\}', answer)
        if json_match:
            data = json.loads(json_match.group())
            
            choice_num = int(data.get('choice', 1))
            
            # Validate choice
            if 1 <= choice_num <= len(candidates[:10]):
                selected = candidates[choice_num - 1]
                return {
                    'sector': selected['sector'],
                    'industry': selected['industry'],
                    'sub_industry': selected['sub_industry'],
                    'confidence': float(data.get('confidence', 0.8)),
                    'reasoning': data.get('reasoning', ''),
                    'method': 'llm'
                }
        
        # Fallback to top candidate
        return {
            'sector': candidates[0]['sector'],
            'industry': candidates[0]['industry'],
            'sub_industry': candidates[0]['sub_industry'],
            'confidence': 0.7,
            'reasoning': 'LLM response invalid, using top embedding match',
            'method': 'embedding_fallback'
        }
        
    except Exception as e:
        print(f"LLM classification error: {e}")
        return None


def extract_attributes_with_llm(
    company_text: str,
    company_name: str = "the company",
    model: str = DEFAULT_MODEL
) -> Dict[str, str]:
    """
    Extract additional company attributes using LLM.
    
    Extracts:
    - headquarters_country
    - customer_type (B2B, B2C, B2B2C)
    - products_summary
    
    Returns:
        Dict with extracted attributes
    """
    prompt = f"""Extract information about this company. Respond in valid JSON format only.

Company: {company_name}

Description:
{company_text[:2000]}

Extract:
1. headquarters_country: Country where company is headquartered (or "unknown")
2. customer_type: B2B, B2C, or B2B2C (or "unknown")
3. products_summary: One sentence describing main products/services (or "unknown")

Respond with this exact JSON format:
{{"headquarters_country": "...", "customer_type": "...", "products_summary": "..."}}

Your JSON response:"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 150
                }
            },
            proxies=PROXIES,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()
            
            # Extract JSON
            json_match = re.search(r'\{[^{}]*\}', answer)
            if json_match:
                return json.loads(json_match.group())
        
        return {}
        
    except Exception:
        return {}
