"""
Similarity and feature scoring functions.

Implements:
- TF-IDF vectorization and cosine similarity
- Keyword overlap scoring
- Domain signal detection
- Semantic embeddings (sentence transformers)
- Combined scoring with configurable weights
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Set, Optional
import re
import numpy as np
from .domain_signals import get_all_domain_signals
from .embeddings import compute_embedding_scores


# Configurable weights for combined scoring
TFIDF_WEIGHT = 0.35
KEYWORD_WEIGHT = 0.20
DOMAIN_SIGNAL_WEIGHT = 0.15
EMBEDDING_WEIGHT = 0.30

# Common English stopwords to ignore
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with',
    'the', 'this', 'but', 'they', 'have', 'had', 'what', 'when', 'where', 'who', 'which',
    'or', 'not', 'no', 'all', 'can', 'also', 'other', 'been', 'their', 'more', 'than'
}


def compute_label_scores(
    company_text: str,
    candidates: List[str],
    candidate_texts: Dict[str, str],
    label_type: Optional[str] = None,
    use_embeddings: bool = True
) -> Dict[str, float]:
    """
    Compute similarity scores for all candidate labels against company text.
    
    Combines:
    - TF-IDF cosine similarity (35%)
    - Keyword overlap (20%)
    - Domain signal (15%)
    - Semantic embeddings (30%)
    
    Args:
        company_text: Combined text representation of the company
        candidates: List of candidate labels (sectors/industries/sub_industries)
        candidate_texts: Dict mapping each candidate to its precomputed text
        label_type: "sector" or "industry" for domain signal matching
        use_embeddings: Whether to include embedding similarity (slower but more accurate)
        
    Returns:
        Dict mapping each candidate label to a score (0-1)
    """
    if not company_text or not candidates:
        return {candidate: 0.0 for candidate in candidates}
    
    # Build corpus: company text + all candidate texts
    texts = [company_text] + [candidate_texts.get(c, c) for c in candidates]
    
    # Compute TF-IDF similarities
    tfidf_scores = _compute_tfidf_similarity(texts, candidates)
    
    # Compute keyword overlap scores
    keyword_scores = {
        candidate: _keyword_overlap_score(company_text, candidate_texts.get(candidate, candidate))
        for candidate in candidates
    }
    
    # Compute domain signals if label_type provided
    domain_scores = {}
    if label_type in ["sector", "industry"]:
        domain_scores = get_all_domain_signals(company_text, candidates, label_type)
    else:
        domain_scores = {candidate: 0.0 for candidate in candidates}
    
    # Compute embedding scores if enabled
    embedding_scores = {}
    if use_embeddings:
        try:
            embedding_scores = compute_embedding_scores(company_text, candidates, candidate_texts)
        except Exception as e:
            # Fallback if embeddings fail
            print(f"⚠️  Embedding computation failed: {e}")
            embedding_scores = {candidate: 0.0 for candidate in candidates}
    else:
        embedding_scores = {candidate: 0.0 for candidate in candidates}
    
    # Combine scores
    combined_scores = {}
    for candidate in candidates:
        tfidf_score = tfidf_scores.get(candidate, 0.0)
        keyword_score = keyword_scores.get(candidate, 0.0)
        domain_score = domain_scores.get(candidate, 0.0)
        embedding_score = embedding_scores.get(candidate, 0.0)
        
        combined_scores[candidate] = (
            TFIDF_WEIGHT * tfidf_score +
            KEYWORD_WEIGHT * keyword_score +
            DOMAIN_SIGNAL_WEIGHT * domain_score +
            EMBEDDING_WEIGHT * embedding_score
        )
    
    return combined_scores


def _compute_tfidf_similarity(texts: List[str], candidates: List[str]) -> Dict[str, float]:
    """
    Compute TF-IDF cosine similarity between company text and candidate texts.
    
    Args:
        texts: [company_text, candidate_text_1, candidate_text_2, ...]
        candidates: List of candidate labels (same order as texts[1:])
        
    Returns:
        Dict mapping candidate label to cosine similarity score
    """
    if len(texts) < 2:
        return {candidate: 0.0 for candidate in candidates}
    
    try:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)  # Unigrams and bigrams
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Company text is first vector
        company_vector = tfidf_matrix[0:1]
        
        # Candidate vectors are remaining
        candidate_vectors = tfidf_matrix[1:]
        
        # Compute cosine similarities
        similarities = cosine_similarity(company_vector, candidate_vectors)[0]
        
        # Map back to candidate labels
        scores = {}
        for i, candidate in enumerate(candidates):
            scores[candidate] = float(similarities[i])
        
        return scores
        
    except Exception as e:
        # Fallback: return zero scores
        return {candidate: 0.0 for candidate in candidates}


def _keyword_overlap_score(company_text: str, label_text: str) -> float:
    """
    Compute keyword overlap score between company text and label text.
    
    Fraction of important tokens from label that appear in company text.
    
    Args:
        company_text: Text from company documents
        label_text: Precomputed text for a label
        
    Returns:
        Score 0-1 representing token overlap
    """
    # Extract tokens from label (remove stopwords)
    label_tokens = _extract_important_tokens(label_text)
    
    if not label_tokens:
        return 0.0
    
    # Extract tokens from company text
    company_tokens = _extract_important_tokens(company_text)
    
    # Count matches
    matches = sum(1 for token in label_tokens if token in company_tokens)
    
    # Compute fraction
    score = matches / len(label_tokens)
    
    return score


def _extract_important_tokens(text: str) -> Set[str]:
    """
    Extract important tokens from text.
    
    - Lowercase
    - Remove punctuation
    - Split on whitespace
    - Remove stopwords
    - Keep tokens with 3+ characters
    
    Args:
        text: Input text
        
    Returns:
        Set of important tokens
    """
    # Lowercase
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Split into tokens
    tokens = text.split()
    
    # Filter: remove stopwords and short tokens
    important_tokens = {
        token for token in tokens
        if token not in STOPWORDS and len(token) >= 3
    }
    
    return important_tokens


def get_top_candidates(
    scores: Dict[str, float],
    top_k: int = 5
) -> List[Dict[str, float]]:
    """
    Get top K candidates sorted by score (descending).
    
    Args:
        scores: Dict of label -> score
        top_k: Number of candidates to return
        
    Returns:
        List of dicts with 'label' and 'score' keys
    """
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {"label": label, "score": score}
        for label, score in sorted_items[:top_k]
    ]


def compute_margin(scores: Dict[str, float]) -> float:
    """
    Compute margin between top score and second-best score.
    
    Args:
        scores: Dict of label -> score
        
    Returns:
        Margin value (top_score - second_score)
    """
    if len(scores) < 2:
        return 0.0
    
    sorted_scores = sorted(scores.values(), reverse=True)
    
    return sorted_scores[0] - sorted_scores[1]
