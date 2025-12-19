"""
Embedding-based semantic similarity using Ollama local LLM.

Provides semantic matching beyond keyword/TF-IDF by encoding text into vector space.
Uses Ollama's native embedding API instead of external models.
"""

from typing import Dict, List, Optional
import numpy as np
from pathlib import Path
import json
import hashlib
import requests

OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "llama2:latest"  # Use your installed model for embeddings
_cache_dir = Path("data/embeddings_cache")
_ollama_available = None


def check_ollama_embeddings() -> bool:
    """Check if Ollama is available for embeddings."""
    global _ollama_available
    if _ollama_available is None:
        try:
            session = requests.Session()
            session.trust_env = False
            response = session.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            _ollama_available = response.status_code == 200
        except Exception:
            _ollama_available = False
    return _ollama_available


def compute_embedding(text: str, use_cache: bool = True) -> Optional[np.ndarray]:
    """
    Compute embedding vector for text using Ollama.
    
    Args:
        text: Input text
        use_cache: Whether to cache embeddings to disk
        
    Returns:
        Embedding vector or None if Ollama unavailable
    """
    if not check_ollama_embeddings():
        return None
    
    # Check cache
    if use_cache:
        cached = _load_from_cache(text)
        if cached is not None:
            return cached
    
    # Compute embedding via Ollama API
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text[:2000]  # Limit text length
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = np.array(result.get('embedding', []))
            
            # Save to cache
            if use_cache and len(embedding) > 0:
                _save_to_cache(text, embedding)
            
            return embedding
        else:
            return None
            
    except Exception:
        return None


def compute_embeddings_batch(texts: List[str], use_cache: bool = True) -> Optional[np.ndarray]:
    """
    Compute embeddings for multiple texts.
    
    Args:
        texts: List of input texts
        use_cache: Whether to cache embeddings
        
    Returns:
        Array of embeddings or None
    """
    if not check_ollama_embeddings():
        return None
    
    embeddings = []
    
    for text in texts:
        emb = compute_embedding(text, use_cache)
        if emb is not None:
            embeddings.append(emb)
        else:
            # Return None if any embedding fails
            return None
    
    if not embeddings:
        return None
    
    return np.array(embeddings)


def cosine_similarity_embeddings(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    
    Returns:
        Similarity score (0-1)
    """
    if emb1 is None or emb2 is None:
        return 0.0
    
    # Normalize
    emb1_norm = emb1 / (np.linalg.norm(emb1) + 1e-8)
    emb2_norm = emb2 / (np.linalg.norm(emb2) + 1e-8)
    
    # Cosine similarity
    similarity = np.dot(emb1_norm, emb2_norm)
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, similarity))


def compute_embedding_scores(
    company_text: str,
    candidates: List[str],
    candidate_texts: Dict[str, str]
) -> Dict[str, float]:
    """
    Compute embedding-based similarity scores for all candidates.
    
    Args:
        company_text: Combined company text
        candidates: List of candidate labels
        candidate_texts: Dict mapping labels to their text representations
        
    Returns:
        Dict mapping each candidate to similarity score (0-1)
    """
    # Get company embedding
    company_emb = compute_embedding(company_text)
    if company_emb is None:
        # Fallback: return zeros if embeddings unavailable
        return {c: 0.0 for c in candidates}
    
    # Get candidate embeddings
    candidate_text_list = [candidate_texts.get(c, c) for c in candidates]
    candidate_embs = compute_embeddings_batch(candidate_text_list)
    
    if candidate_embs is None:
        return {c: 0.0 for c in candidates}
    
    # Compute similarities
    scores = {}
    for i, candidate in enumerate(candidates):
        scores[candidate] = cosine_similarity_embeddings(company_emb, candidate_embs[i])
    
    return scores


def _get_cache_key(text: str) -> str:
    """Generate cache key from text hash."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def _load_from_cache(text: str) -> Optional[np.ndarray]:
    """Load embedding from cache if exists."""
    if not _cache_dir.exists():
        return None
    
    cache_key = _get_cache_key(text)
    cache_file = _cache_dir / f"{cache_key}.npy"
    
    if cache_file.exists():
        try:
            return np.load(cache_file)
        except Exception:
            return None
    
    return None


def _save_to_cache(text: str, embedding: np.ndarray):
    """Save embedding to cache."""
    _cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_key = _get_cache_key(text)
    cache_file = _cache_dir / f"{cache_key}.npy"
    
    try:
        np.save(cache_file, embedding)
    except Exception:
        pass  # Silently fail on cache errors
