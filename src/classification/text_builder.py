"""
Company text builder.

Extracts and combines text from all company documents to create a representative
description for classification.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import re
import requests
import os


def build_company_text(company_folder: str, use_ollama_summary: bool = True, max_input_chars: int = 10000) -> str:
    """
    Build a comprehensive text representation of a company from all its documents.
    
    NEW APPROACH:
    - Extract up to 10,000 characters of raw company text
    - Use Ollama LLM to intelligently summarize into business-focused description
    - Falls back to rule-based extraction if Ollama fails
    
    Combines:
    - metadata.title and description (weighted 3x)
    - Structured headings h1, h2, h3 (weighted 2x)
    - First paragraphs
    - Extended raw_text (up to 10000 chars)
    - Lists and table content
    - Prioritizes /about, /products, /solutions URLs
    
    Args:
        company_folder: Path to company folder (e.g., data/outputs/company_name)
        use_ollama_summary: Use Ollama to generate intelligent summary (default: True)
        max_input_chars: Maximum characters to extract before summarization (default: 10000)
        
    Returns:
        Combined text string (lowercase, cleaned)
    """
    company_path = Path(company_folder)
    sources_path = company_path / "sources"
    
    if not sources_path.exists():
        return ""
    
    # Separate high-priority and regular documents
    priority_docs = []
    regular_docs = []
    
    # Iterate over all source JSON files
    for json_file in sources_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                doc = json.load(f)
            
            # Check if this is a high-priority URL
            source_uri = doc.get("source", {}).get("uri", "")
            if _is_priority_source(source_uri):
                priority_docs.append(doc)
            else:
                regular_docs.append(doc)
            
        except (json.JSONDecodeError, KeyError, IOError) as e:
            # Skip malformed or inaccessible files
            continue
    
    all_text_parts = []
    
    # Process priority docs first with higher weight
    for doc in priority_docs:
        text_parts = _extract_text_from_document(doc, weight_multiplier=2.0)
        all_text_parts.extend(text_parts)
    
    # Process regular docs
    for doc in regular_docs:
        text_parts = _extract_text_from_document(doc, weight_multiplier=1.0)
        all_text_parts.extend(text_parts)
    
    # Combine all parts
    combined_text = " ".join(all_text_parts)
    
    # Clean and normalize
    cleaned_text = _clean_text(combined_text)
    
    # Limit to max_input_chars for Ollama summarization
    if len(cleaned_text) > max_input_chars:
        cleaned_text = cleaned_text[:max_input_chars]
    
    # Use Ollama to create intelligent summary
    if use_ollama_summary and len(cleaned_text) > 500:
        summary = _summarize_with_ollama(cleaned_text, company_folder)
        if summary:
            return summary
    
    # Fallback: Extract business-relevant content manually
    cleaned_text = _extract_business_relevant_content(cleaned_text)
    
    # Final limit for embeddings
    MAX_CHARS = 3000
    if len(cleaned_text) > MAX_CHARS:
        cleaned_text = cleaned_text[:MAX_CHARS]
    
    return cleaned_text


def _extract_business_relevant_content(text: str, max_length: int = 5000) -> str:
    """
    Extract only business-relevant sentences from text.
    
    Prioritizes sentences containing:
    - Products/services keywords
    - Industry/sector keywords
    - Technology keywords
    - Business model keywords
    
    Filters out:
    - Contact information
    - Navigation text
    - Generic marketing phrases
    """
    # If text is already short enough, just return it
    if len(text) < max_length:
        return text
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
    
    # If we don't have many sentences, return as is
    if len(sentences) < 10:
        return text[:max_length]
    
    # Business-relevant keywords (high priority)
    business_keywords = [
        # Core business
        'software', 'platform', 'solution', 'service', 'product', 'system',
        'technology', 'tool', 'application', 'app', 'saas', 'cloud',
        
        # Industry/sector
        'industry', 'enterprise', 'business', 'company', 'organization',
        'market', 'sector', 'customer', 'client',
        
        # Specific domains
        'hr', 'human resources', 'payroll', 'crm', 'erp', 'analytics',
        'data', 'ai', 'artificial intelligence', 'machine learning',
        'automation', 'management', 'tracking', 'monitoring',
        'workspace', 'office', 'coworking', 'flexible',
        
        # Business model
        'provide', 'deliver', 'offer', 'enable', 'power', 'help',
        'specialize', 'focus', 'develop', 'build', 'create',
        
        # Value proposition
        'mission', 'vision', 'goal', 'objective', 'purpose',
        'innovative', 'leading', 'pioneer', 'transform',
    ]
    
    # Noise keywords (to filter out)
    noise_keywords = [
        'cookie', 'privacy policy', 'terms and conditions',
    ]
    
    # Score and filter sentences
    scored_sentences = []
    for sentence in sentences:
        # Skip if too short
        if len(sentence) < 20:
            continue
        
        # Skip if contains noise
        has_noise = any(noise in sentence.lower() for noise in noise_keywords)
        if has_noise:
            continue
        
        # Score based on business keywords
        score = sum(1 for keyword in business_keywords if keyword in sentence.lower())
        
        # Include sentence if it has at least one business keyword OR if it's long and descriptive
        if score > 0 or len(sentence) > 50:
            scored_sentences.append((score, sentence))
    
    # If we filtered out too much, return original
    if len(scored_sentences) < 5:
        return text[:max_length]
    
    # Sort by score (descending) and take top sentences
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    top_sentences = [s[1] for s in scored_sentences[:40]]  # Top 40 sentences
    
    # Join and truncate
    result = '. '.join(top_sentences)
    if len(result) > max_length:
        result = result[:max_length]
    
    return result if result else text[:max_length]


def _is_priority_source(uri: str) -> bool:
    """
    Check if a source URI contains high-value keywords.
    Priority URLs: /about, /products, /solutions, /industries, /company, /services
    """
    if not uri:
        return False
    
    uri_lower = uri.lower()
    priority_keywords = [
        '/about', '/products', '/solutions', '/industries', 
        '/company', '/services', '/platform', '/technology',
        '/what-we-do', '/overview'
    ]
    
    return any(keyword in uri_lower for keyword in priority_keywords)


def _extract_text_from_document(doc: Dict[str, Any], weight_multiplier: float = 1.0) -> List[str]:
    """
    Extract relevant text parts from a single document JSON.
    
    Priority (with weighting):
    1. metadata.title (3x weight)
    2. metadata.description (3x weight)
    3. Structured headings h1, h2, h3 (2x weight)
    4. First 5 paragraphs
    5. Extended raw_text (up to 5000 chars)
    6. List items (more comprehensive)
    7. Table cells (more comprehensive)
    
    Args:
        doc: Document JSON
        weight_multiplier: Additional multiplier for priority sources
    """
    parts = []
    
    # 1. Title (weighted 3x)
    metadata = doc.get("metadata", {})
    title = metadata.get("title", "")
    if title:
        # Repeat 3 times for weighting
        repeat_count = int(3 * weight_multiplier)
        parts.extend([title] * repeat_count)
    
    # 2. Description (weighted 3x)
    description = metadata.get("description", "")
    if description:
        repeat_count = int(3 * weight_multiplier)
        parts.extend([description] * repeat_count)
    
    content = doc.get("content", {})
    structured = content.get("structured", {}) if content else {}
    
    # 3. Headings (h1, h2, h3) - weighted 2x
    headings = structured.get("headings", []) if structured else []
    for heading in headings:
        if heading.get("tag") in ["h1", "h2", "h3"]:
            text = heading.get("text", "")
            if text:
                # Repeat 2 times for weighting
                repeat_count = int(2 * weight_multiplier)
                parts.extend([text] * repeat_count)
    
    # 4. First 5 paragraphs (increased from 3)
    paragraphs = structured.get("paragraphs", []) if structured else []
    for para in paragraphs[:5]:
        if para:
            parts.append(para)
    
    # 5. Extended raw_text (5000 chars instead of 2000)
    raw_text = content.get("raw_text", "") if content else ""
    if raw_text:
        if not structured:
            # Use more text if no structured content
            parts.append(raw_text[:5000])
        elif len(parts) < 10:
            # Use more if we have limited structured data
            parts.append(raw_text[:3000])
        else:
            # Still include some raw text
            parts.append(raw_text[:1500])
    
    # 6. Lists (more comprehensive)
    lists = structured.get("lists", []) if structured else []
    for lst in lists[:5]:  # Increased from 2 to 5 lists
        items = lst.get("items", [])
        for item in items[:10]:  # Increased from 5 to 10 items per list
            if item:
                parts.append(item)
    
    # 7. Tables (more comprehensive)
    tables = structured.get("tables", []) if structured else []
    for table in tables[:3]:  # Increased from 1 to 3 tables
        # Headers
        headers = table.get("headers", [])
        parts.extend(headers)
        
        # More rows
        rows = table.get("rows", [])
        for row in rows[:5]:  # Increased from 3 to 5 rows
            if isinstance(row, list):
                parts.extend([str(cell) for cell in row if cell])
    
    return parts


def _clean_text(text: str) -> str:
    """
    Clean and normalize text - IMPROVED VERSION.
    
    - Remove noise: navigation, footers, contact forms, cookie notices
    - Remove repetitive phrases (occurs more than 3 times)
    - Keep only business-relevant content
    - Lowercase and normalize whitespace
    """
    # Lowercase
    text = text.lower()
    
    # Remove common noise patterns (expanded)
    noise_patterns = [
        r'cookie\s+policy',
        r'privacy\s+policy',
        r'terms\s+(and\s+)?conditions',
        r'all\s+rights\s+reserved',
        r'copyright\s+©?\s*\d{4}',
        r'click\s+here',
        r'read\s+more',
        r'learn\s+more',
        r'subscribe\s+to\s+(our\s+)?newsletter',
        r'sign\s+up',
        r'log\s+in',
        r'register\s+(now|here)',
        r'get\s+started',
        r'contact\s+us',
        r'follow\s+us',
        r'facebook|twitter|linkedin|instagram',
        r'powered\s+by',
        r'skip\s+to\s+(content|navigation)',
        r'email\s+address',
        r'your\s+email',
        r'we\s+use\s+cookies',
        r'accept\s+cookies',
        r'this\s+website\s+uses',
        r'menu|navigation|nav|breadcrumb',
        r'home\s*>\s*about',
        r'©\s*\d{4}',
        r'send\s+email',
        r'support@\w+\.\w+',
        r'onboarding@\w+\.\w+',
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    
    # Remove URLs
    text = re.sub(r'https?://[^\s]+', ' ', text)
    text = re.sub(r'www\.[^\s]+', ' ', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', ' ', text)
    
    # Remove repetitive phrases (appears more than 3 times)
    text = _remove_repetitive_phrases(text)
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def _remove_repetitive_phrases(text: str, max_occurrences: int = 2) -> str:
    """
    Remove phrases that appear more than max_occurrences times.
    This helps remove navigation menus and repeated headers.
    """
    # Split into sentences/phrases (by periods, newlines)
    phrases = re.split(r'[.!?\n]+', text)
    phrases = [p.strip() for p in phrases if len(p.strip()) > 10]  # Min 10 chars
    
    # Count occurrences
    phrase_counts = {}
    for phrase in phrases:
        phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
    
    # Remove phrases that appear too often
    filtered_phrases = []
    seen_count = {}
    for phrase in phrases:
        count = seen_count.get(phrase, 0)
        if count < max_occurrences:
            filtered_phrases.append(phrase)
            seen_count[phrase] = count + 1
    
    return ' '.join(filtered_phrases)


def get_company_name_from_path(company_folder: str) -> str:
    """Extract company name from folder path."""
    return Path(company_folder).name


def _summarize_with_ollama(text: str, company_folder: str, model: str = "qwen2.5:7b") -> str:
    """
    Use Ollama LLM to intelligently summarize company information.
    
    Available models (fastest to most accurate):
    - llama3.2:1b (fastest, ~1GB) - Good for simple summaries
    - llama3.2:3b (balanced, ~2GB) - Fast and accurate
    - llama2:latest (~4GB) - More detailed
    - gemma3:4b (~3.3GB) - Google's best small model, very detailed
    - qwen2.5:7b (~4.7GB) - **BEST** for structured extraction and following instructions
    - mistral:latest (~4GB) - Good at following instructions
    
    Args:
        text: Raw company text (up to 10,000 chars)
        company_folder: Path to company folder
        model: Ollama model to use (default: qwen2.5:7b)
        
    Returns:
        Intelligent summary focusing on business essentials, or None if failed
    """
    company_name = get_company_name_from_path(company_folder)
    
    # Set proxy bypass for localhost
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    
    prompt = f"""You are a business analyst expert. Analyze this company information and create a concise summary focused ONLY on business essentials.

Company: {company_name}

Raw Information:
{text}

INSTRUCTIONS:
Create a human-readable business summary with clear bullet points. Use the following exact structure:

**Core Business:**
[One clear sentence on what they do]

**Key Offerings:**
* [Product/Service 1]
* [Product/Service 2]
* [Product/Service 3]

**Target Audience:**
* [Who they serve]

**Industry & Sector:**
[Industry focus]

**Value Proposition:**
[Why they matter]

IMPORTANT:
- Use bullet points (*) for lists
- Keep it clean, professional, and easy to read
- Maximum 500 words
- Remove all noise (contact info, navigation, cookies)
- Output MUST include the headers above

Summary:"""

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,  # Lower temperature for factual output
                    'num_predict': 800,  # Increased from 600
                }
            },
            proxies={'http': None, 'https': None},
            timeout=120  # Increased from 60 for larger models
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('response', '').strip()
            
            if summary and len(summary) > 100:
                print(f"✅ Ollama ({model}) summary generated ({len(summary)} chars)")
                return summary.lower()
        
    except Exception as e:
        print(f"⚠️ Ollama summarization failed: {e}")
    
    return None
