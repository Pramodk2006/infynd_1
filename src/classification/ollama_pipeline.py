"""
Complete Ollama-based classification pipeline.
Uses local embeddings + LLM for industry classification.
"""

from typing import Optional
from pathlib import Path

from .models import Taxonomy, ClassificationResult, CompanyClassification
from .text_builder import build_company_text, get_company_name_from_path
from .ollama_embeddings import OllamaEmbeddingIndex, check_ollama_embedding_model
from .ollama_llm import check_ollama_available, classify_with_llm, extract_attributes_with_llm, get_available_models


# Default models
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_LLM_MODEL = "llama2:latest"

# Global state
_embedding_index = None
_taxonomy = None


def initialize_ollama_classifier(
    taxonomy: Taxonomy,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    index_path: Optional[str] = None
) -> OllamaEmbeddingIndex:
    """
    Initialize Ollama-based classifier with taxonomy.
    
    Args:
        taxonomy: Loaded taxonomy object
        embedding_model: Ollama embedding model to use
        index_path: Path to save/load index
        
    Returns:
        OllamaEmbeddingIndex ready for classification
    """
    global _embedding_index, _taxonomy
    
    print("\n" + "=" * 60)
    print("INITIALIZING OLLAMA CLASSIFIER")
    print("=" * 60)
    
    # Check Ollama availability
    if not check_ollama_available():
        raise RuntimeError(
            "Ollama is not running! Start it with: ollama serve\n"
            "Or install from: https://ollama.com"
        )
    
    print(f"✅ Ollama is running")
    
    # Show available models
    models = get_available_models()
    print(f"Available models: {', '.join(models) if models else 'None'}")
    
    # Check embedding model (match with or without :latest tag)
    model_found = False
    actual_model = embedding_model
    
    for model in models:
        if model == embedding_model or model.startswith(f"{embedding_model}:"):
            model_found = True
            actual_model = model
            break
    
    if not model_found:
        print(f"\n⚠️  Embedding model '{embedding_model}' not found!")
        print(f"Install with: ollama pull {embedding_model}")
        raise RuntimeError(f"Embedding model '{embedding_model}' not available")
    
    print(f"✅ Using embedding model: {actual_model}")
    
    # Create or load index
    index = OllamaEmbeddingIndex(actual_model)
    
    if index_path:
        index_file = Path(index_path) / 'ollama_index.pkl'
        if index_file.exists():
            print(f"\n📂 Loading existing index from {index_path}...")
            index.load(index_path)
        else:
            print(f"\n🔨 Building new index (will save to {index_path})...")
            _build_index(index, taxonomy)
            index.save(index_path)
    else:
        print(f"\n🔨 Building index (not saving to disk)...")
        _build_index(index, taxonomy)
    
    _embedding_index = index
    _taxonomy = taxonomy
    
    print("\n" + "=" * 60)
    print("✅ OLLAMA CLASSIFIER READY")
    print("=" * 60 + "\n")
    
    return index


def _build_index(index: OllamaEmbeddingIndex, taxonomy: Taxonomy):
    """Build embedding index from taxonomy."""
    
    # Get all taxonomy entries
    labels = []
    label_texts = []
    
    for _, row in taxonomy.df.iterrows():
        sector = row.get('sector', '')
        industry = row.get('Industry', '')
        sub_industry = row.get('sub_industry', '')
        
        if sector and industry and sub_industry:
            labels.append((sector, industry, sub_industry))
            
            # Build descriptive text
            parts = [
                f"Sub-Industry: {sub_industry}",
                f"Industry: {industry}",
                f"Sector: {sector}"
            ]
            
            # Add SIC info if available
            if 'sic_description' in row and str(row['sic_description']) != 'nan':
                parts.append(f"Description: {row['sic_description']}")
            
            label_texts.append(". ".join(parts))
    
    # Add to index
    index.add_labels(labels, label_texts)


def classify_with_ollama(
    company_folder: str,
    llm_model: str = DEFAULT_LLM_MODEL,
    top_k: int = 20
) -> CompanyClassification:
    """
    Classify company using Ollama embeddings + LLM.
    
    Args:
        company_folder: Path to company folder
        llm_model: Ollama LLM model to use
        top_k: Number of embedding candidates to retrieve
        
    Returns:
        CompanyClassification result
    """
    global _embedding_index, _taxonomy
    
    if _embedding_index is None or _taxonomy is None:
        raise RuntimeError("Classifier not initialized! Call initialize_ollama_classifier() first")
    
    # Get company name
    company_name = get_company_name_from_path(company_folder)
    
    # Build company text
    company_text = build_company_text(company_folder)
    
    if not company_text or len(company_text) < 50:
        return _create_unknown_classification(company_name)
    
    print(f"\nClassifying: {company_name}")
    print(f"Text length: {len(company_text)} characters")
    
    # Step 1: Get embedding candidates
    print(f"🔍 Searching embeddings (top {top_k})...")
    candidates = _embedding_index.search(company_text, top_k=top_k)
    
    if not candidates:
        print("⚠️  No candidates found")
        return _create_unknown_classification(company_name)
    
    print(f"✅ Found {len(candidates)} candidates")
    print(f"   Top match: {candidates[0]['sub_industry']} ({candidates[0]['similarity']:.3f})")
    
    # Step 2: LLM classification
    print(f"🤖 Classifying with {llm_model}...")
    llm_result = classify_with_llm(company_text, candidates, company_name, llm_model)
    
    if llm_result:
        sector = llm_result['sector']
        industry = llm_result['industry']
        sub_industry = llm_result['sub_industry']
        confidence = llm_result['confidence']
        reasoning = llm_result['reasoning']
        
        print(f"✅ LLM selected: {sector} → {industry} → {sub_industry}")
        print(f"   Confidence: {confidence:.2f}")
    else:
        # Fallback to top embedding
        print("⚠️  LLM failed, using top embedding match")
        sector = candidates[0]['sector']
        industry = candidates[0]['industry']
        sub_industry = candidates[0]['sub_industry']
        confidence = candidates[0]['similarity']
        reasoning = "Using embedding match (LLM unavailable)"
    
    # Get SIC metadata
    sic_metadata = _taxonomy.sic_by_subindustry.get(sub_industry, {})
    sic_code = sic_metadata.get('sic_code', '')
    sic_description = sic_metadata.get('sic_description', '')
    
    # Build result
    sector_result = ClassificationResult(
        label=sector,
        score=confidence,
        margin=0.0,
        candidates=[{'label': c['sector'], 'score': c['similarity']} for c in candidates[:5]]
    )
    
    industry_result = ClassificationResult(
        label=industry,
        score=confidence,
        margin=0.0,
        candidates=[{'label': c['industry'], 'score': c['similarity']} for c in candidates[:5]]
    )
    
    subindustry_result = ClassificationResult(
        label=sub_industry,
        score=confidence,
        margin=0.0,
        candidates=[{'label': c['sub_industry'], 'score': c['similarity']} for c in candidates[:5]]
    )
    
    # Extract additional attributes (optional)
    extra_attrs = extract_attributes_with_llm(company_text, company_name, llm_model)
    
    result = CompanyClassification(
        company=company_name,
        sector=sector_result,
        industry=industry_result,
        sub_industry=subindustry_result,
        sic_code=sic_code,
        sic_description=sic_description
    )
    
    if extra_attrs:
        result.extra_attributes = extra_attrs
    
    return result


def _create_unknown_classification(company_name: str) -> CompanyClassification:
    """Create unknown classification result."""
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
