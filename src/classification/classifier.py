"""
Hierarchical classifier implementation.

Implements sector → industry → sub_industry classification using:
- Text similarity scoring (TF-IDF + keywords + domain signals + embeddings)
- LLM re-ranking (taxonomy-constrained)
- Conditional hierarchical classification
- Confidence thresholds
"""

from typing import Optional
from pathlib import Path

from .models import Taxonomy, ClassificationResult, CompanyClassification
from .text_builder import build_company_text, get_company_name_from_path
from .similarity import compute_label_scores, get_top_candidates, compute_margin
from .llm_reranker import llm_rerank_sector, llm_rerank_industry, check_ollama_available, llm_extract_attributes


# Confidence thresholds
MIN_SECTOR_SCORE = 0.06  # Lower threshold since sectors are broad categories
MIN_INDUSTRY_SCORE = 0.12
MIN_SUBINDUSTRY_SCORE = 0.10

# LLM settings
USE_LLM_RERANKING = True  # Set to False to disable LLM re-ranking
LLM_AVAILABLE = None  # Cached check


def classify_company(company_folder: str, taxonomy: Taxonomy, use_llm: bool = True) -> CompanyClassification:
    """
    Perform complete hierarchical classification for a company.
    
    Steps:
    1. Build company text from all documents
    2. Classify sector (deterministic + optional LLM re-ranking)
    3. Classify industry (conditional on sector + optional LLM)
    4. Classify sub_industry (conditional on sector + industry)
    5. Attach SIC metadata
    6. Extract additional attributes (optional LLM)
    
    Args:
        company_folder: Path to company folder (e.g., data/outputs/company_name)
        taxonomy: Loaded taxonomy object
        use_llm: Whether to use LLM re-ranking (requires Ollama)
        
    Returns:
        CompanyClassification with sector, industry, sub_industry results
    """
    global LLM_AVAILABLE
    
    # Check Ollama availability once
    if LLM_AVAILABLE is None and use_llm:
        LLM_AVAILABLE = check_ollama_available()
        if LLM_AVAILABLE:
            print("Ollama available - using LLM re-ranking")
        else:
            print("Ollama not available - using deterministic classification only")
    
    # Extract company name
    company_name = get_company_name_from_path(company_folder)
    
    # Build text representation
    company_text = build_company_text(company_folder)
    
    if not company_text:
        # Return unknown classification if no text available
        return _create_unknown_classification(company_name)
    
    # Step 1: Classify sector (with optional LLM re-ranking)
    sector_result = classify_sector(company_text, taxonomy, company_name, use_llm and LLM_AVAILABLE)
    
    if sector_result is None:
        return _create_unknown_classification(company_name)
    
    # Step 2: Classify industry (conditional on sector, with optional LLM)
    if sector_result.label != "Unknown" and sector_result.score >= MIN_SECTOR_SCORE:
        industry_result = classify_industry(
            company_text, taxonomy, sector_result.label, company_name, use_llm and LLM_AVAILABLE
        )
    else:
        # Fallback: classify across all industries
        industry_result = _classify_industry_fallback(company_text, taxonomy)
    
    # Step 3: Classify sub_industry (conditional on sector + industry)
    if (sector_result.label != "Unknown" and 
        industry_result.label != "Unknown" and
        industry_result.score >= MIN_INDUSTRY_SCORE):
        subindustry_result = classify_subindustry(
            company_text, 
            taxonomy, 
            sector_result.label,
            industry_result.label
        )
    else:
        # Fallback: classify across all sub_industries
        subindustry_result = _classify_subindustry_fallback(company_text, taxonomy)
    
    # Step 4: Attach SIC metadata
    sic_metadata = taxonomy.get_sic_metadata(subindustry_result.label)
    sic_code = sic_metadata.get('sic_code', '') if sic_metadata else None
    sic_description = sic_metadata.get('sic_description', '') if sic_metadata else None
    
    # Step 5: Extract additional attributes (optional LLM)
    extra_attributes = {}
    if use_llm and LLM_AVAILABLE:
        extra_attributes = llm_extract_attributes(company_text, company_name)
    
    result = CompanyClassification(
        company=company_name,
        sector=sector_result,
        industry=industry_result,
        sub_industry=subindustry_result,
        sic_code=sic_code,
        sic_description=sic_description
    )


def classify_sector(
    company_text: str, 
    taxonomy: Taxonomy,
    company_name: str = "the company",
    use_llm: bool = False
) -> ClassificationResult:
    """
    Classify company into a sector with domain signal boosting and optional LLM re-ranking.
    
    Args:
        company_text: Combined text from company documents
        taxonomy: Loaded taxonomy
        company_name: Name of company for LLM context
        use_llm: Whether to use LLM re-ranking
        
    Returns:
        ClassificationResult with best sector and candidates
    """
    candidates = taxonomy.unique_sectors
    candidate_texts = taxonomy.sector_texts
    
    # Compute scores with domain signals and embeddings
    scores = compute_label_scores(company_text, candidates, candidate_texts, label_type="sector")
    
    # Get top candidates
    top_candidates = get_top_candidates(scores, top_k=5)
    
    # Try LLM re-ranking if enabled
    if use_llm and top_candidates:
        llm_choice = llm_rerank_sector(company_text, top_candidates, company_name)
        if llm_choice and llm_choice != "Unknown":
            # LLM chose a valid candidate, use it
            for cand in top_candidates:
                if cand['label'] == llm_choice:
                    return ClassificationResult(
                        label=llm_choice,
                        score=cand['score'],
                        margin=compute_margin(scores, llm_choice),
                        candidates=top_candidates
                    )
    
    # Fallback to deterministic best
    # Best label
    if not top_candidates:
        return ClassificationResult(
            label="Unknown",
            score=0.0,
            margin=0.0,
            candidates=[]
        )
    
    best_label = top_candidates[0]["label"]
    best_score = top_candidates[0]["score"]
    
    # Compute margin
    margin = compute_margin(scores)
    
    # Apply threshold
    if best_score < MIN_SECTOR_SCORE:
        return ClassificationResult(
            label="Unknown",
            score=best_score,
            margin=margin,
            candidates=top_candidates
        )
    
    return ClassificationResult(
        label=best_label,
        score=best_score,
        margin=margin,
        candidates=top_candidates
    )


def classify_industry(
    company_text: str, 
    taxonomy: Taxonomy, 
    sector_label: str,
    company_name: str = "the company",
    use_llm: bool = False
) -> ClassificationResult:
    """
    Classify company into an industry within a given sector with domain signal boosting and optional LLM.
    
    Args:
        company_text: Combined text from company documents
        taxonomy: Loaded taxonomy
        sector_label: The classified sector
        company_name: Name of company for LLM context
        use_llm: Whether to use LLM re-ranking
        
    Returns:
        ClassificationResult with best industry and candidates
    """
    # Get industries for this sector
    candidates = taxonomy.get_industries_for_sector(sector_label)
    
    if not candidates:
        return ClassificationResult(
            label="Unknown",
            score=0.0,
            margin=0.0,
            candidates=[]
        )
    
    candidate_texts = taxonomy.industry_texts
    
    # Compute scores with domain signals and embeddings
    scores = compute_label_scores(company_text, candidates, candidate_texts, label_type="industry")
    
    # Get top candidates
    top_candidates = get_top_candidates(scores, top_k=7)
    
    # Try LLM re-ranking if enabled
    if use_llm and top_candidates:
        llm_choice = llm_rerank_industry(company_text, top_candidates, sector_label, company_name)
        if llm_choice and llm_choice != "Unknown":
            for cand in top_candidates:
                if cand['label'] == llm_choice:
                    return ClassificationResult(
                        label=llm_choice,
                        score=cand['score'],
                        margin=compute_margin(scores, llm_choice),
                        candidates=top_candidates
                    )
    
    # Fallback to deterministic
    if not top_candidates:
        return ClassificationResult(
            label="Unknown",
            score=0.0,
            margin=0.0,
            candidates=[]
        )
    
    best_label = top_candidates[0]["label"]
    best_score = top_candidates[0]["score"]
    margin = compute_margin(scores)
    
    # Apply threshold
    if best_score < MIN_INDUSTRY_SCORE:
        return ClassificationResult(
            label="Unknown",
            score=best_score,
            margin=margin,
            candidates=top_candidates
        )
    
    return ClassificationResult(
        label=best_label,
        score=best_score,
        margin=margin,
        candidates=top_candidates
    )


def classify_subindustry(
    company_text: str,
    taxonomy: Taxonomy,
    sector_label: str,
    industry_label: str
) -> ClassificationResult:
    """
    Classify company into a sub_industry within a given sector and industry.
    
    Args:
        company_text: Combined text from company documents
        taxonomy: Loaded taxonomy
        sector_label: The classified sector
        industry_label: The classified industry
        
    Returns:
        ClassificationResult with best sub_industry and candidates
    """
    # Get sub_industries for this sector + industry
    candidates = taxonomy.get_subindustries_for_sector_industry(sector_label, industry_label)
    
    if not candidates:
        return ClassificationResult(
            label="Unknown",
            score=0.0,
            margin=0.0,
            candidates=[]
        )
    
    candidate_texts = taxonomy.subindustry_texts
    
    # Compute scores
    scores = compute_label_scores(company_text, candidates, candidate_texts)
    
    # Get top candidates
    top_candidates = get_top_candidates(scores, top_k=5)
    
    if not top_candidates:
        return ClassificationResult(
            label="Unknown",
            score=0.0,
            margin=0.0,
            candidates=[]
        )
    
    best_label = top_candidates[0]["label"]
    best_score = top_candidates[0]["score"]
    margin = compute_margin(scores)
    
    # Apply threshold
    if best_score < MIN_SUBINDUSTRY_SCORE:
        return ClassificationResult(
            label="Unknown",
            score=best_score,
            margin=margin,
            candidates=top_candidates
        )
    
    return ClassificationResult(
        label=best_label,
        score=best_score,
        margin=margin,
        candidates=top_candidates
    )


def _classify_industry_fallback(
    company_text: str,
    taxonomy: Taxonomy
) -> ClassificationResult:
    """
    Classify industry across all industries (no sector constraint).
    Used when sector classification fails.
    """
    candidates = taxonomy.unique_industries
    candidate_texts = taxonomy.industry_texts
    
    scores = compute_label_scores(company_text, candidates, candidate_texts)
    top_candidates = get_top_candidates(scores, top_k=5)
    
    if not top_candidates:
        return ClassificationResult(
            label="Unknown",
            score=0.0,
            margin=0.0,
            candidates=[]
        )
    
    best_label = top_candidates[0]["label"]
    best_score = top_candidates[0]["score"]
    margin = compute_margin(scores)
    
    if best_score < MIN_INDUSTRY_SCORE:
        return ClassificationResult(
            label="Unknown",
            score=best_score,
            margin=margin,
            candidates=top_candidates
        )
    
    return ClassificationResult(
        label=best_label,
        score=best_score,
        margin=margin,
        candidates=top_candidates
    )


def _classify_subindustry_fallback(
    company_text: str,
    taxonomy: Taxonomy
) -> ClassificationResult:
    """
    Classify sub_industry across all sub_industries (no constraints).
    Used when sector/industry classification fails.
    """
    candidates = taxonomy.unique_subindustries
    candidate_texts = taxonomy.subindustry_texts
    
    scores = compute_label_scores(company_text, candidates, candidate_texts)
    top_candidates = get_top_candidates(scores, top_k=5)
    
    if not top_candidates:
        return ClassificationResult(
            label="Unknown",
            score=0.0,
            margin=0.0,
            candidates=[]
        )
    
    best_label = top_candidates[0]["label"]
    best_score = top_candidates[0]["score"]
    margin = compute_margin(scores)
    
    if best_score < MIN_SUBINDUSTRY_SCORE:
        return ClassificationResult(
            label="Unknown",
            score=best_score,
            margin=margin,
            candidates=top_candidates
        )
    
    return ClassificationResult(
        label=best_label,
        score=best_score,
        margin=margin,
        candidates=top_candidates
    )


def _create_unknown_classification(company_name: str) -> CompanyClassification:
    """Create a classification result with all unknowns."""
    unknown_result = ClassificationResult(
        label="Unknown",
        score=0.0,
        margin=0.0,
        candidates=[]
    )
    
    return CompanyClassification(
        company=company_name,
        sector=unknown_result,
        industry=unknown_result,
        sub_industry=unknown_result,
        sic_code=None,
        sic_description=None
    )
