"""
LLM-based re-ranking using local Ollama.

Taxonomy-constrained classification: LLM only chooses from top-k candidates,
preventing hallucination while leveraging semantic understanding.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from .models import ClassificationResult


OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama2:latest"  # 7B model - good balance of speed and accuracy


def check_ollama_available() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        # Bypass proxy for localhost
        session = requests.Session()
        session.trust_env = False
        response = session.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_available_models() -> List[str]:
    """Get list of available Ollama models."""
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except Exception:
        return []


def llm_rerank_sector(
    company_text: str,
    top_candidates: List[Dict],
    company_name: str = "the company",
    model: str = DEFAULT_MODEL
) -> Optional[str]:
    """
    Use LLM to re-rank and select the best sector from top candidates.
    
    Args:
        company_text: Company description (first 1500 chars)
        top_candidates: List of dicts with 'label' and 'score' from deterministic classifier
        company_name: Name of company for context
        model: Ollama model to use
        
    Returns:
        Selected sector label or None if LLM fails
    """
    if not check_ollama_available():
        return None
    
    # Build candidate list for prompt
    candidate_list = "\n".join([f"- {c['label']}" for c in top_candidates[:5]])
    
    prompt = f"""You are a business classification expert. Given a company description and a list of possible sectors, choose exactly ONE sector that best matches.

Company: {company_name}

Description:
{company_text[:1500]}

Possible sectors (choose ONLY from this list):
{candidate_list}

Instructions:
- Choose exactly one sector from the list above
- If none fit well, respond with "Unknown"
- Respond with ONLY the sector name, nothing else
- Do NOT invent new sectors

Your answer (sector name only):"""

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistency
                    "num_predict": 50     # Short response
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()
            
            # Validate answer is in candidates
            candidate_labels = [c['label'] for c in top_candidates[:5]]
            if answer in candidate_labels:
                return answer
            elif answer.lower() == "unknown":
                return "Unknown"
            else:
                # LLM gave invalid answer, return None (use deterministic)
                return None
        
        return None
        
    except Exception as e:
        print(f"⚠️  LLM re-ranking failed: {e}")
        return None


def llm_rerank_industry(
    company_text: str,
    top_candidates: List[Dict],
    sector: str,
    company_name: str = "the company",
    model: str = DEFAULT_MODEL
) -> Optional[str]:
    """
    Use LLM to re-rank and select the best industry from top candidates.
    
    Args:
        company_text: Company description
        top_candidates: List of dicts with 'label' and 'score'
        sector: The chosen sector for context
        company_name: Name of company
        model: Ollama model to use
        
    Returns:
        Selected industry label or None
    """
    if not check_ollama_available():
        return None
    
    candidate_list = "\n".join([f"- {c['label']}" for c in top_candidates[:7]])
    
    prompt = f"""You are a business classification expert. Given a company in the {sector} sector, choose the best industry.

Company: {company_name}
Sector: {sector}

Description:
{company_text[:1500]}

Possible industries in {sector} (choose ONLY from this list):
{candidate_list}

Instructions:
- Choose exactly one industry from the list above
- If none fit well, respond with "Unknown"
- Respond with ONLY the industry name, nothing else
- Do NOT invent new industries

Your answer (industry name only):"""

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 50
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()
            
            candidate_labels = [c['label'] for c in top_candidates[:7]]
            if answer in candidate_labels:
                return answer
            elif answer.lower() == "unknown":
                return "Unknown"
            else:
                return None
        
        return None
        
    except Exception:
        return None


def llm_extract_attributes(
    company_text: str,
    company_name: str = "the company",
    model: str = DEFAULT_MODEL
) -> Dict[str, str]:
    """
    Extract additional attributes using LLM.
    
    Extracts:
    - headquarters_country: Country where company is based
    - customer_type: B2B, B2C, or B2B2C
    - products_summary: Brief summary of main products/services (1 sentence)
    
    Returns:
        Dict with extracted attributes
    """
    if not check_ollama_available():
        return {}
    
    prompt = f"""Extract information about this company. Respond ONLY in valid JSON format.

Company: {company_name}

Description:
{company_text[:2000]}

Extract the following (respond with "unknown" if not clear):
1. headquarters_country: Country where company is headquartered
2. customer_type: B2B (business customers), B2C (consumers), or B2B2C (both)
3. products_summary: One sentence describing main products/services

Respond in this exact JSON format:
{{
  "headquarters_country": "...",
  "customer_type": "...",
  "products_summary": "..."
}}

Your JSON response:"""

    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(
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
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()
            
            # Try to parse JSON
            try:
                # Extract JSON from response (might have extra text)
                start = answer.find('{')
                end = answer.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = answer[start:end]
                    attributes = json.loads(json_str)
                    return attributes
            except json.JSONDecodeError:
                pass
        
        return {}
        
    except Exception:
        return {}
