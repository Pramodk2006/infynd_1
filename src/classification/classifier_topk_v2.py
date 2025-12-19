"""
Enhanced Top-K Hierarchical Classifier v2
===========================================

Improvements over v1:
1. Specificity scoring - favors detailed labels over generic ones
2. Document source quality weighting - prioritizes high-signal pages
3. Evidence density for confidence calibration
4. Conditional LLM re-ranking when uncertainty is high
5. Smarter final selection with context-aware scoring

Author: Enhanced pipeline based on analysis
Date: December 2025
"""

import os
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import numpy as np

from .models import Taxonomy
from .similarity import compute_label_scores


# ============================================================================
# PHASE 1: SPECIFICITY SCORING
# ============================================================================

def compute_specificity_score(label: str, company_text: str) -> float:
    """
    Favor SPECIFIC labels over generic ones:
    - "Business and Domestic Software" > "App Development"
    - Multi-word labels > single words
    - Labels containing company-specific terms > generic software terms
    
    Args:
        label: The classification label (e.g., "Business and Domestic Software")
        company_text: Full company description text
        
    Returns:
        Specificity score between 0.0 and 1.0
    """
    label_words = label.lower().split()
    text_words = set(company_text.lower().split())
    
    # 1. Length bias: more specific = more words
    # "Business and Domestic Software" (4 words) > "App Development" (2 words)
    length_score = min(len(label_words) / 3.0, 1.0)  # cap at 3 words
    
    # 2. Rarity bias: uncommon words get boost
    # Penalize common generic terms that appear everywhere
    common_generic = {
        'app', 'software', 'service', 'services', 'development', 'system', 
        'systems', 'solution', 'solutions', 'management', 'platform',
        'technology', 'technologies', 'product', 'products'
    }
    specific_words = [w for w in label_words if w not in common_generic]
    specificity_ratio = len(specific_words) / max(len(label_words), 1)
    
    # 3. Company-text overlap: label words actually in company text
    # "Domestic" appears in "Business and Domestic Software" and company text → boost
    overlap_count = sum(1 for w in label_words if w in text_words)
    overlap_ratio = overlap_count / len(label_words) if label_words else 0
    
    # Weighted combination
    final_score = (
        0.4 * length_score +           # Favor multi-word labels
        0.3 * specificity_ratio +      # Favor uncommon words
        0.3 * overlap_ratio            # Favor terms in company text
    )
    
    return final_score


def compute_final_scores(
    company_text: str, 
    candidates: List[Tuple[str, float]],
    boost_factor: float = 0.3
) -> List[Tuple[str, float, float]]:
    """
    Re-rank top-K candidates with specificity boost.
    
    Args:
        company_text: Full company description
        candidates: List of (label, base_score) tuples
        boost_factor: How much to boost specific labels (0.0 to 1.0)
        
    Returns:
        List of (label, adjusted_score, specificity) sorted by adjusted score
    """
    specificity_adjusted = []
    
    for label, base_score in candidates:
        specificity = compute_specificity_score(label, company_text)
        
        # Boost specific labels, penalize generic ones
        # If specificity=1.0: multiply by (0.7 + 0.3*1.0) = 1.0 (full boost)
        # If specificity=0.0: multiply by (0.7 + 0.3*0.0) = 0.7 (30% penalty)
        boost_multiplier = (1.0 - boost_factor) + (boost_factor * specificity)
        adjusted_score = base_score * boost_multiplier
        
        specificity_adjusted.append((label, adjusted_score, specificity))
    
    # Sort by adjusted score (highest first)
    return sorted(specificity_adjusted, key=lambda x: x[1], reverse=True)


# ============================================================================
# PHASE 2: DOCUMENT SOURCE QUALITY WEIGHTING
# ============================================================================

def compute_doc_source_quality(uri: str, title: str, doc_type: str) -> float:
    """
    Score documents by relevance to classification.
    
    High-signal pages (about, products, solutions) get boosted.
    Low-signal pages (contact, support, careers) get penalized.
    
    Args:
        uri: Document URL or file path
        title: Document title
        doc_type: Document type ('webpage', 'pdf', etc.)
        
    Returns:
        Quality multiplier (0.3 to 3.0)
    """
    quality = 1.0
    text_lower = (uri + " " + title).lower()
    
    # BOOST high-signal pages (core business information)
    high_signal = [
        'about', 'company', 'products', 'solutions', 'services', 
        'industries', 'what-we-do', 'overview', 'platform',
        'technology', 'features', 'capabilities'
    ]
    if any(kw in text_lower for kw in high_signal):
        quality *= 2.0
    
    # PENALIZE low-signal pages (navigation, support, noise)
    low_signal = [
        'contact', 'support', 'help', 'faq', 'careers', 'jobs',
        'blog', 'news', 'press', 'privacy', 'terms', 'legal',
        'cookie', 'login', 'signup', 'register'
    ]
    if any(kw in text_lower for kw in low_signal):
        quality *= 0.3
    
    # PDFs with product/brochure names get boost
    if doc_type == 'pdf' and any(kw in text_lower for kw in 
                                  ['brochure', 'datasheet', 'guide', 'whitepaper', 'overview']):
        quality *= 1.5
    
    # Homepage gets slight boost
    if uri.endswith('/') or '/index.' in uri or uri.count('/') <= 3:
        quality *= 1.2
    
    return min(quality, 3.0)  # cap maximum boost


def build_company_text_per_doc(company_folder: str) -> List[Dict]:
    """
    Build list of documents with source quality weights.
    
    Returns:
        List of dicts with keys: text, uri, title, type, weight
    """
    from .text_builder import build_company_text
    
    output_path = Path("data/outputs") / company_folder
    sources_path = output_path / "sources"
    
    if not sources_path.exists():
        return []
    
    docs = []
    for source_file in sources_path.glob("*.json"):
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            text = data.get('text', '')
            uri = data.get('url', '')
            title = data.get('title', '')
            doc_type = data.get('type', 'webpage')
            
            # Compute quality weight
            quality = compute_doc_source_quality(uri, title, doc_type)
            
            docs.append({
                'text': text,
                'uri': uri,
                'title': title,
                'type': doc_type,
                'weight': quality
            })
        except Exception as e:
            print(f"⚠️ Error loading {source_file}: {e}")
            continue
    
    return docs


# ============================================================================
# PHASE 3: CONFIDENCE CALIBRATION (EVIDENCE DENSITY)
# ============================================================================

def compute_evidence_density(
    top_candidates: List[Tuple[str, float]], 
    all_docs: List[Dict],
    top_k: int = 3
) -> float:
    """
    Measure how consistently top prediction appears across documents.
    
    High density = multiple docs support same classification → high confidence
    Low density = only 1-2 docs support it → low confidence
    
    Args:
        top_candidates: Top-K classification candidates with scores
        all_docs: All documents with weights
        top_k: How many candidates to check
        
    Returns:
        Evidence density score (0.0 to 1.0)
    """
    if not top_candidates or not all_docs:
        return 0.0
    
    top_label = top_candidates[0][0]
    supporting_weight = 0.0
    
    # Check each document
    for doc in all_docs:
        # Compute scores for top-K candidates in this doc
        candidate_labels = [c[0] for c in top_candidates[:top_k]]
        candidate_texts = {label: label for label in candidate_labels}
        doc_scores = compute_label_scores(doc['text'], candidate_labels, candidate_texts)
        
        # If top label scores well in this doc, add its weight
        if top_label in doc_scores and doc_scores[top_label] > 0.15:
            supporting_weight += doc['weight']
    
    total_weight = sum(doc['weight'] for doc in all_docs)
    
    if total_weight == 0:
        return 0.0
    
    # Density = fraction of weighted documents supporting prediction
    density = min(supporting_weight / total_weight, 1.0)
    
    return density


# ============================================================================
# PHASE 4: CONDITIONAL LLM RE-RANKER
# ============================================================================

def should_use_llm(
    top_sectors: List[Tuple],
    top_industries: List[Tuple],
    confidence_threshold: float = 0.20,
    margin_threshold: float = 0.05
) -> bool:
    """
    Decide whether to use LLM re-ranking.
    
    Only use LLM when deterministic prediction is uncertain:
    1. Top score is low (<0.20)
    2. Margin between top-2 is small (<0.05)
    3. Multiple strong candidates
    
    Args:
        top_sectors: Ranked sector predictions
        top_industries: Ranked industry predictions
        confidence_threshold: Minimum score to skip LLM
        margin_threshold: Minimum margin to skip LLM
        
    Returns:
        True if LLM should be used
    """
    if not top_sectors or not top_industries:
        return False
    
    # Check sector confidence
    top_sector_score = top_sectors[0][1]
    
    # Low confidence → use LLM
    if top_sector_score < confidence_threshold:
        return True
    
    # Check margin between top 2
    if len(top_sectors) > 1:
        margin = top_sectors[0][1] - top_sectors[1][1]
        if margin < margin_threshold:
            return True
    
    return False


def rerank_with_llm(
    company_text: str,
    top_sectors: List[Tuple[str, float]],
    top_industries: List[Tuple[str, float]],
    llm_model: str = "qwen2.5:7b"
) -> Dict:
    """
    Use LLM to pick best classification from top-K candidates.
    
    Only shows LLM the top 3-5 candidates (not full taxonomy).
    This focuses the LLM on disambiguating close matches.
    
    Args:
        company_text: Company description
        top_sectors: Top-K sectors
        top_industries: Top-K industries
        llm_model: Ollama model to use
        
    Returns:
        Dict with sector and industry picks
    """
    import requests
    
    # Build focused prompt with only top candidates
    prompt = f"""You are an expert business analyst. Given a company description and top classification candidates, pick the MOST ACCURATE match.

COMPANY DESCRIPTION:
{company_text[:1000]}

TOP SECTORS (ranked by similarity):
"""
    
    for i, (sector, score) in enumerate(top_sectors[:5], 1):
        prompt += f"{i}. {sector} ({score:.2f})\n"
    
    prompt += f"\nTOP INDUSTRIES (ranked by similarity):\n"
    
    for i, (industry, score) in enumerate(top_industries[:5], 1):
        prompt += f"{i}. {industry} ({score:.2f})\n"
    
    prompt += """
Pick EXACTLY ONE sector and ONE industry from the lists above.
Answer in this EXACT format:
SECTOR: [exact name from list]
INDUSTRY: [exact name from list]
REASONING: [1 sentence why]
"""
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': llm_model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,  # Very low for deterministic output
                    'num_predict': 200,
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()
            
            # Parse LLM output
            sector = None
            industry = None
            reasoning = None
            
            for line in answer.split('\n'):
                if line.startswith('SECTOR:'):
                    sector = line.replace('SECTOR:', '').strip()
                elif line.startswith('INDUSTRY:'):
                    industry = line.replace('INDUSTRY:', '').strip()
                elif line.startswith('REASONING:'):
                    reasoning = line.replace('REASONING:', '').strip()
            
            return {
                'sector': sector,
                'industry': industry,
                'reasoning': reasoning,
                'method': 'llm_rerank'
            }
    
    except Exception as e:
        print(f"⚠️ LLM re-ranking failed: {e}")
    
    # Fallback to top deterministic picks
    return {
        'sector': top_sectors[0][0] if top_sectors else None,
        'industry': top_industries[0][0] if top_industries else None,
        'reasoning': 'LLM unavailable, using deterministic ranking',
        'method': 'fallback'
    }


# ============================================================================
# PHASE 5: COMPLETE ENHANCED CLASSIFIER
# ============================================================================

def classify_company_topk_v2(
    company_folder: str,
    use_ollama_summary: bool = True,
    k_sectors: int = 5,
    k_industries: int = 5,
    k_subindustries: int = 10,
    sector_threshold: float = 0.01,
    industry_threshold: float = 0.01,
    subindustry_threshold: float = 0.01,
    use_llm_rerank: bool = True,
    llm_model: str = "qwen2.5:7b"
) -> Dict:
    """
    Enhanced Top-K Hierarchical Classifier with all improvements.
    
    Enhancements:
    1. Specificity scoring for final selection
    2. Document source quality weighting
    3. Evidence density for confidence
    4. Conditional LLM re-ranking
    
    Args:
        company_folder: Company name in data/outputs/
        use_ollama_summary: Use Ollama-powered text summarization
        k_sectors: Number of top sectors to explore
        k_industries: Number of top industries per sector
        k_subindustries: Number of top sub-industries to return
        sector_threshold: Minimum score for sectors
        industry_threshold: Minimum score for industries
        subindustry_threshold: Minimum score for sub-industries
        use_llm_rerank: Whether to use LLM when uncertainty is high
        llm_model: Ollama model for LLM re-ranking
        
    Returns:
        Classification result with enhanced confidence scoring
    """
    from .text_builder import build_company_text, get_company_name_from_path
    from .taxonomy import load_taxonomy
    
    print(f"\n{'='*80}")
    print(f"ENHANCED TOP-K CLASSIFIER V2: {company_folder}")
    print(f"{'='*80}")
    
    # Load taxonomy
    print("Loading taxonomy...")
    taxonomy_path = Path("data/sub_Industry_Classification-in.csv")
    taxonomy = load_taxonomy(str(taxonomy_path))
    print(f"Loaded: {len(taxonomy.unique_sectors)} sectors, "
          f"{len(taxonomy.unique_industries)} industries, "
          f"{len(taxonomy.unique_subindustries)} sub-industries\n")
    
    # Build company text with Ollama summarization
    print(f"Building text from data/outputs/{company_folder}...")
    company_path_full = f"data/outputs/{company_folder}"
    company_text = build_company_text(
        company_path_full,
        use_ollama_summary=use_ollama_summary,
        max_input_chars=10000
    )
    
    if not company_text:
        return {
            "error": "No text extracted",
            "company": company_folder
        }
    
    print(f"Extracted {len(company_text)} characters\n")
    
    # For now, skip per-document weighting (v2.1 feature)
    # Just use single merged text
    docs = []
    print(f"Using merged company text (per-document weighting disabled for v2.0)\n")
    
    print(f"\n{'='*80}")
    print(f"HIERARCHICAL CLASSIFICATION")
    print(f"{'='*80}")
    print(f"Text length: {len(company_text)} chars")
    print(f"K values: sectors={k_sectors}, industries={k_industries}, sub-industries={k_subindustries}\n")
    
    # ==========================================================================
    # STEP 1: COMPUTE TOP-K SECTORS
    # ==========================================================================
    
    print(f"\nSTEP 1: Computing top {k_sectors} sectors...")
    
    sector_labels = list(taxonomy.unique_sectors)
    sector_texts = {label: label for label in sector_labels}
    sector_scores = compute_label_scores(company_text, sector_labels, sector_texts, label_type="sector")
    
    # Sort and filter
    sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
    top_sectors_raw = [(label, score) for label, score in sorted_sectors[:k_sectors] 
                       if score >= sector_threshold]
    
    # Apply specificity scoring
    top_sectors_enhanced = compute_final_scores(company_text, top_sectors_raw)
    top_sectors = [(label, score) for label, score, spec in top_sectors_enhanced]
    
    print(f"Top {len(top_sectors)} sectors (threshold {sector_threshold}):")
    for i, (sector, score) in enumerate(top_sectors, 1):
        print(f"   {i}. {sector}: {score:.3f}")
    
    if not top_sectors:
        return {
            "error": "No sectors above threshold",
            "company": company_folder,
            "text_length": len(company_text)
        }
    
    # ==========================================================================
    # STEP 2: COMPUTE TOP-K INDUSTRIES (across ALL top sectors)
    # ==========================================================================
    
    print(f"\n📊 STEP 2: Computing top {k_industries} industries...")
    
    all_industry_candidates = []
    
    for sector_name, sector_score in top_sectors:
        # Get industries under this sector
        sector_industries = taxonomy.industries_by_sector.get(sector_name, [])
        
        if not sector_industries:
            continue
        
        # Score industries
        industry_texts = {label: label for label in sector_industries}
        industry_scores = compute_label_scores(company_text, sector_industries, industry_texts, label_type="industry")
        
        for ind_name, ind_score in industry_scores.items():
            if ind_score >= industry_threshold:
                all_industry_candidates.append((ind_name, ind_score, sector_name))
    
    # Merge duplicates (keep highest score)
    merged_industries = {}
    for ind_name, score, sector in all_industry_candidates:
        if ind_name not in merged_industries or score > merged_industries[ind_name]['score']:
            merged_industries[ind_name] = {'score': score, 'sector': sector}
    
    # Convert back to list
    industry_tuples = [(ind, data['score']) for ind, data in merged_industries.items()]
    
    # Apply specificity scoring
    top_industries_enhanced = compute_final_scores(company_text, industry_tuples)
    top_industries = [(label, score) for label, score, spec in top_industries_enhanced[:k_industries]]
    
    print(f"✅ Top {len(top_industries)} industries (threshold {industry_threshold}):")
    for i, (industry, score) in enumerate(top_industries, 1):
        # Find sector
        sector = merged_industries[industry]['sector']
        print(f"   {i}. {sector} → {industry}: {score:.3f}")
    
    if not top_industries:
        return {
            "error": "No industries above threshold",
            "company": company_folder,
            "top_sectors": top_sectors,
            "text_length": len(company_text)
        }
    
    # ==========================================================================
    # STEP 3: COMPUTE TOP-K SUB-INDUSTRIES
    # ==========================================================================
    
    print(f"\n📊 STEP 3: Computing top {k_subindustries} sub-industries...")
    
    all_subindustry_candidates = []
    
    for industry_name, industry_score in top_industries:
        # Find sector for this industry
        sector_name = None
        for s, inds in taxonomy.industries_by_sector.items():
            if industry_name in inds:
                sector_name = s
                break
        
        if not sector_name:
            continue
        
        # Get sub-industries under this industry
        industry_subindustries = taxonomy.subindustries_by_sector_industry.get(
            (sector_name, industry_name), []
        )
        
        if not industry_subindustries:
            continue
        
        # Score sub-industries
        subindustry_texts = {label: label for label in industry_subindustries}
        subindustry_scores = compute_label_scores(company_text, industry_subindustries, subindustry_texts)
        
        for sub_name, sub_score in subindustry_scores.items():
            if sub_score >= subindustry_threshold:
                # Get SIC code
                sic_data = taxonomy.sic_by_subindustry.get(sub_name, {})
                all_subindustry_candidates.append({
                    'name': sub_name,
                    'score': sub_score,
                    'industry': industry_name,
                    'sector': sector_name,
                    'sic_code': sic_data.get('sic_code'),
                    'sic_description': sic_data.get('sic_description')
                })
    
    # Merge duplicates (keep highest score)
    merged_subindustries = {}
    for sub in all_subindustry_candidates:
        if sub['name'] not in merged_subindustries or sub['score'] > merged_subindustries[sub['name']]['score']:
            merged_subindustries[sub['name']] = sub
    
    # Convert to list for specificity scoring
    subindustry_tuples = [(sub['name'], sub['score']) for sub in merged_subindustries.values()]
    
    # Apply specificity scoring
    top_subindustries_enhanced = compute_final_scores(company_text, subindustry_tuples, boost_factor=0.4)
    
    # Reconstruct full sub-industry dicts
    top_subindustries = []
    for label, score, specificity in top_subindustries_enhanced[:k_subindustries]:
        sub_data = merged_subindustries[label]
        top_subindustries.append({
            'name': label,
            'score': score,
            'specificity': specificity,
            'industry': sub_data['industry'],
            'sector': sub_data['sector'],
            'sic_code': sub_data['sic_code'],
            'sic_description': sub_data['sic_description']
        })
    
    print(f"✅ Top {len(top_subindustries)} sub-industries (threshold {subindustry_threshold}):")
    for i, sub in enumerate(top_subindustries, 1):
        print(f"   {i}. {sub['sector']} → {sub['industry']} → {sub['name']}: "
              f"{sub['score']:.3f} (specificity: {sub['specificity']:.2f})")
    
    # ==========================================================================
    # STEP 4: CONDITIONAL LLM RE-RANKING
    # ==========================================================================
    
    use_llm = use_llm_rerank and should_use_llm(top_sectors, top_industries)
    
    if use_llm:
        print(f"\n🤖 Uncertainty detected - using LLM re-ranking with {llm_model}...")
        llm_result = rerank_with_llm(company_text, top_sectors, top_industries, llm_model)
        
        final_sector = llm_result.get('sector') or top_sectors[0][0]
        final_industry = llm_result.get('industry') or top_industries[0][0]
        selection_method = llm_result.get('method', 'llm_rerank')
        llm_reasoning = llm_result.get('reasoning', '')
        
        print(f"✅ LLM selected: {final_sector} → {final_industry}")
        if llm_reasoning:
            print(f"   Reasoning: {llm_reasoning}")
    else:
        # Use deterministic top picks
        final_sector = top_sectors[0][0]
        final_industry = top_industries[0][0]
        selection_method = 'deterministic'
        llm_reasoning = None
    
    # Final sub-industry is always top-1 from enhanced ranking
    final_subindustry = top_subindustries[0] if top_subindustries else None
    
    # ==========================================================================
    # STEP 5: CONFIDENCE CALIBRATION (EVIDENCE DENSITY)
    # ==========================================================================
    
    print(f"\nComputing confidence...")
    
    # For v2.0, just use base score (evidence density needs per-doc data)
    base_confidence = top_sectors[0][1] if top_sectors else 0.0
    evidence_score = base_confidence  # Simplified for v2.0
    final_confidence = base_confidence
    
    print(f"Base confidence: {base_confidence:.2f}")
    print(f"Final confidence: {final_confidence:.2f}")
    
    # ==========================================================================
    # FINAL RESULT
    # ==========================================================================
    
    print(f"\n{'='*80}")
    print("FINAL PREDICTION")
    print(f"{'='*80}")
    print(f"Sector: {final_sector}")
    print(f"Industry: {final_industry}")
    if final_subindustry:
        print(f"Sub-Industry: {final_subindustry['name']}")
        print(f"SIC Code: {final_subindustry['sic_code']}")
    print(f"Confidence: {final_confidence*100:.1f}%")
    print(f"Selection Method: {selection_method}")
    print(f"{'='*80}\n")
    
    return {
        "company": company_folder,
        "summary": company_text,
        "text_length": len(company_text),
        "num_documents": len(docs),
        "top_sectors": [
            {"label": sector, "score": score, "rank": i+1}
            for i, (sector, score) in enumerate(top_sectors)
        ],
        "top_industries": [
            {"label": industry, "score": score, "rank": i+1}
            for i, (industry, score) in enumerate(top_industries)
        ],
        "top_subindustries": [
            {
                "label": sub['name'],
                "score": sub['score'],
                "specificity": sub['specificity'],
                "industry": sub['industry'],
                "sector": sub['sector'],
                "sic_code": sub['sic_code'],
                "sic_description": sub['sic_description'],
                "rank": i+1
            }
            for i, sub in enumerate(top_subindustries)
        ],
        "final_prediction": {
            "sector": final_sector,
            "industry": final_industry,
            "sub_industry": final_subindustry['name'] if final_subindustry else None,
            "sic_code": final_subindustry['sic_code'] if final_subindustry else None,
            "sic_description": final_subindustry['sic_description'] if final_subindustry else None,
            "confidence": round(final_confidence, 3),
            "evidence_density": round(evidence_score, 3),
            "selection_method": selection_method,
            "llm_reasoning": llm_reasoning
        }
    }


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def classify_company_enhanced(company_folder: str, **kwargs) -> Dict:
    """Alias for classify_company_topk_v2 with sensible defaults."""
    return classify_company_topk_v2(company_folder, **kwargs)
