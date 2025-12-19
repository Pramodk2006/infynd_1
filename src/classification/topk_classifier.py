"""
Top-K Hierarchical Classification
Progressively narrows candidates at each level to avoid early mistakes.
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import json

from .taxonomy import load_taxonomy
from .text_builder import build_company_text
from .similarity import compute_label_scores


# Thresholds for each level
SECTOR_THRESHOLD = 0.01  # Lowered from 0.08
INDUSTRY_THRESHOLD = 0.01  # Lowered from 0.12
SUBINDUSTRY_THRESHOLD = 0.01  # Lowered from 0.10

# Top-K limits
TOP_K_SECTORS = 5
TOP_K_INDUSTRIES = 5
TOP_K_SUBINDUSTRIES = 10


def classify_company_topk_hierarchical(
    company_name: str,
    company_text: str,
    taxonomy,
    top_k_sectors: int = TOP_K_SECTORS,
    top_k_industries: int = TOP_K_INDUSTRIES,
    top_k_subindustries: int = TOP_K_SUBINDUSTRIES
) -> Dict[str, Any]:
    """
    Top-K hierarchical classification.
    
    Instead of picking best sector → best industry → best sub-industry,
    we get TOP K at each level and search all their children.
    
    This prevents early mistakes from eliminating correct paths.
    
    Args:
        company_name: Company identifier
        company_text: Aggregated company description
        taxonomy: Loaded taxonomy object
        top_k_sectors: Number of top sectors to explore
        top_k_industries: Number of top industries to explore
        top_k_subindustries: Number of final sub-industries to return
        
    Returns:
        Dict with top candidates at each level + final prediction
    """
    
    print(f"\n{'='*80}")
    print(f"TOP-K HIERARCHICAL CLASSIFICATION: {company_name}")
    print(f"{'='*80}")
    print(f"Text length: {len(company_text)} chars")
    print(f"K values: sectors={top_k_sectors}, industries={top_k_industries}, sub-industries={top_k_subindustries}")
    
    # ========================================================================
    # STEP 1: TOP-K SECTORS
    # ========================================================================
    print(f"\n📊 STEP 1: Computing top {top_k_sectors} sectors...")
    
    sector_texts = {
        sector: f"{sector}"
        for sector in taxonomy.unique_sectors
    }
    
    sector_scores = compute_label_scores(
        company_text,
        list(sector_texts.keys()),
        candidate_texts=sector_texts,
        label_type="sector",
        use_embeddings=True  # Enable embeddings
    )
    
    # Sort and filter
    top_sectors = sorted(
        sector_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k_sectors]
    
    # Apply threshold
    top_sectors = [(sector, score) for sector, score in top_sectors if score >= SECTOR_THRESHOLD]
    
    if not top_sectors:
        return {
            "error": "insufficient_data",
            "message": f"No sectors passed threshold {SECTOR_THRESHOLD}"
        }
    
    print(f"✅ Top {len(top_sectors)} sectors (threshold {SECTOR_THRESHOLD}):")
    for i, (sector, score) in enumerate(top_sectors, 1):
        print(f"   {i}. {sector}: {score:.3f}")
    
    # ========================================================================
    # STEP 2: TOP-K INDUSTRIES (across all top sectors)
    # ========================================================================
    print(f"\n📊 STEP 2: Computing top {top_k_industries} industries...")
    
    all_industry_candidates = []
    
    for sector, sector_score in top_sectors:
        # Get industries for this sector
        sector_industries = taxonomy.industries_by_sector.get(sector, [])
        
        if not sector_industries:
            continue
        
        # Compute scores for these industries
        industry_texts = {
            ind: f"{sector} {ind}"
            for ind in sector_industries
        }
        
        industry_scores = compute_label_scores(
            company_text,
            list(industry_texts.keys()),
            candidate_texts=industry_texts,
            label_type="industry",
            use_embeddings=True  # Enable embeddings
        )
        
        # Collect candidates with sector context
        for industry, score in industry_scores.items():
            if score >= INDUSTRY_THRESHOLD:
                all_industry_candidates.append({
                    'industry': industry,
                    'sector': sector,
                    'score': score,
                    'sector_score': sector_score
                })
    
    # Merge duplicates (same industry can appear in multiple sectors)
    # Take highest score
    merged_industries = {}
    for cand in all_industry_candidates:
        key = cand['industry']
        if key not in merged_industries or cand['score'] > merged_industries[key]['score']:
            merged_industries[key] = cand
    
    # Sort by score and take top K
    top_industries = sorted(
        merged_industries.values(),
        key=lambda x: x['score'],
        reverse=True
    )[:top_k_industries]
    
    if not top_industries:
        print(f"⚠️ No industries passed threshold {INDUSTRY_THRESHOLD}")
        # Fallback: use all industries from top sector
        top_sector = top_sectors[0][0]
        top_industries = [
            {
                'industry': ind,
                'sector': top_sector,
                'score': 0.0,
                'sector_score': top_sectors[0][1]
            }
            for ind in taxonomy.industries_by_sector.get(top_sector, [])[:top_k_industries]
        ]
    
    print(f"✅ Top {len(top_industries)} industries (threshold {INDUSTRY_THRESHOLD}):")
    for i, ind_data in enumerate(top_industries, 1):
        print(f"   {i}. {ind_data['sector']} → {ind_data['industry']}: {ind_data['score']:.3f}")
    
    # ========================================================================
    # STEP 3: TOP-K SUB-INDUSTRIES (across all top industries)
    # ========================================================================
    print(f"\n📊 STEP 3: Computing top {top_k_subindustries} sub-industries...")
    
    all_subindustry_candidates = []
    
    for ind_data in top_industries:
        sector = ind_data['sector']
        industry = ind_data['industry']
        industry_score = ind_data['score']
        
        # Get sub-industries for this (sector, industry) pair
        key = (sector, industry)
        sector_subindustries = taxonomy.subindustries_by_sector_industry.get(key, [])
        
        if not sector_subindustries:
            continue
        
        # Compute scores
        subind_texts = {
            subind: f"{sector} {industry} {subind}"
            for subind in sector_subindustries
        }
        
        subind_scores = compute_label_scores(
            company_text,
            list(subind_texts.keys()),
            candidate_texts=subind_texts,
            label_type=None,
            use_embeddings=True  # Enable embeddings
        )
        
        # Collect candidates
        for subind, score in subind_scores.items():
            if score >= SUBINDUSTRY_THRESHOLD:
                # Get SIC code
                sic_info = taxonomy.sic_by_subindustry.get(subind, {})
                
                all_subindustry_candidates.append({
                    'sub_industry': subind,
                    'industry': industry,
                    'sector': sector,
                    'score': score,
                    'industry_score': industry_score,
                    'sic_code': sic_info.get('sic_code'),
                    'sic_description': sic_info.get('sic_description')
                })
    
    # Merge duplicates (same sub-industry can appear in multiple industries)
    merged_subindustries = {}
    for cand in all_subindustry_candidates:
        key = cand['sub_industry']
        if key not in merged_subindustries or cand['score'] > merged_subindustries[key]['score']:
            merged_subindustries[key] = cand
    
    # Sort and take top K
    top_subindustries = sorted(
        merged_subindustries.values(),
        key=lambda x: x['score'],
        reverse=True
    )[:top_k_subindustries]
    
    if not top_subindustries:
        print(f"⚠️ No sub-industries passed threshold {SUBINDUSTRY_THRESHOLD}")
        # Use top industry as fallback
        top_ind = top_industries[0]
        top_subindustries = [{
            'sub_industry': 'Unknown',
            'industry': top_ind['industry'],
            'sector': top_ind['sector'],
            'score': 0.0,
            'industry_score': top_ind['score'],
            'sic_code': None,
            'sic_description': None
        }]
    
    print(f"✅ Top {len(top_subindustries)} sub-industries (threshold {SUBINDUSTRY_THRESHOLD}):")
    for i, subind_data in enumerate(top_subindustries, 1):
        print(f"   {i}. {subind_data['sector']} → {subind_data['industry']} → {subind_data['sub_industry']}: {subind_data['score']:.3f}")
    
    # ========================================================================
    # STEP 4: FINAL PREDICTION
    # ========================================================================
    final_sector = top_sectors[0][0]
    final_industry = top_industries[0]['industry']
    final_subindustry = top_subindustries[0]['sub_industry']
    final_sic_code = top_subindustries[0]['sic_code']
    final_sic_desc = top_subindustries[0]['sic_description']
    
    # Confidence: weighted average of top scores
    confidence = min(1.0, (
        top_sectors[0][1] * 0.4 +
        top_industries[0]['score'] * 0.4 +
        top_subindustries[0]['score'] * 0.2
    ))
    
    result = {
        "company": company_name,
        "top_sectors": [
            {"label": s, "score": round(score, 4), "rank": i+1}
            for i, (s, score) in enumerate(top_sectors)
        ],
        "top_industries": [
            {
                "label": ind['industry'],
                "sector": ind['sector'],
                "score": round(ind['score'], 4),
                "rank": i+1
            }
            for i, ind in enumerate(top_industries)
        ],
        "top_subindustries": [
            {
                "label": sub['sub_industry'],
                "industry": sub['industry'],
                "sector": sub['sector'],
                "score": round(sub['score'], 4),
                "sic_code": sub['sic_code'],
                "sic_description": sub['sic_description'],
                "rank": i+1
            }
            for i, sub in enumerate(top_subindustries)
        ],
        "final_prediction": {
            "sector": final_sector,
            "industry": final_industry,
            "sub_industry": final_subindustry,
            "sic_code": final_sic_code,
            "sic_description": final_sic_desc,
            "confidence": round(confidence, 3)
        }
    }
    
    print(f"\n{'='*80}")
    print(f"✅ FINAL PREDICTION")
    print(f"{'='*80}")
    print(f"Sector: {final_sector}")
    print(f"Industry: {final_industry}")
    print(f"Sub-Industry: {final_subindustry}")
    print(f"SIC Code: {final_sic_code}")
    print(f"Confidence: {confidence:.1%}")
    print(f"{'='*80}\n")
    
    return result


def classify_company_from_folder(
    company_folder: str,
    method: str = "topk"
) -> Dict[str, Any]:
    """
    Classify a company from its extracted data folder.
    
    Args:
        company_folder: Path to company folder (e.g., 'data/outputs/kredily')
        method: Classification method ('topk' or 'single')
        
    Returns:
        Classification result dict
    """
    # Load taxonomy
    print("📚 Loading taxonomy...")
    taxonomy = load_taxonomy('data/sub_Industry_Classification-in.csv')
    print(f"✅ Loaded: {len(taxonomy.unique_sectors)} sectors, "
          f"{len(taxonomy.unique_industries)} industries, "
          f"{len(taxonomy.unique_subindustries)} sub-industries")
    
    # Build company text
    print(f"\n📄 Building text from {company_folder}...")
    company_text = build_company_text(company_folder)
    company_name = Path(company_folder).name
    print(f"✅ Extracted {len(company_text)} characters")
    
    # Classify
    if method == "topk":
        result = classify_company_topk_hierarchical(
            company_name,
            company_text,
            taxonomy
        )
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return result


def save_classification_result(result: Dict[str, Any], output_path: str):
    """Save classification result to JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved result to {output_path}")
