"""
Ollama-based embeddings and FAISS indexing.
Uses local Ollama API for 100% offline embedding generation.
"""

import numpy as np
import requests
import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional


# Ollama API configuration
OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaEmbeddingIndex:
    """
    FAISS-based embedding index using Ollama for vector generation.
    """
    
    def __init__(self, model: str = "nomic-embed-text"):
        """
        Initialize embedding index.
        
        Args:
            model: Ollama embedding model to use
        """
        self.model = model
        self.labels = []  # List of (sector, industry, sub_industry) tuples
        self.label_texts = []  # Corresponding text descriptions
        self.embeddings = None  # numpy array of embeddings
        self.dimension = None
        
        # Proxy bypass for localhost
        self.proxies = {"http": None, "https": None}
    
    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for text using Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                proxies=self.proxies,
                timeout=30
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            embedding = result.get('embedding')
            
            if not embedding:
                raise RuntimeError("No embedding in response")
            
            return np.array(embedding, dtype=np.float32)
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to connect to Ollama: {e}")
    
    def add_labels(self, labels: List[Tuple[str, str, str]], label_texts: List[str]):
        """
        Add labels to index with their embeddings.
        
        Args:
            labels: List of (sector, industry, sub_industry) tuples
            label_texts: Corresponding text descriptions
        """
        if len(labels) != len(label_texts):
            raise ValueError("labels and label_texts must have same length")
        
        self.labels = labels
        self.label_texts = label_texts
        
        print(f"Generating embeddings for {len(labels)} labels...")
        
        embeddings_list = []
        for i, text in enumerate(label_texts):
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{len(label_texts)}")
            
            emb = self.embed(text)
            
            # Set dimension on first embedding
            if self.dimension is None:
                self.dimension = len(emb)
            
            embeddings_list.append(emb)
        
        # Stack into matrix
        self.embeddings = np.vstack(embeddings_list)
        
        # Normalize for cosine similarity (using inner product)
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self.embeddings = self.embeddings / (norms + 1e-8)
        
        print(f"✅ Index built: {len(labels)} labels, dimension={self.dimension}")
    
    def search(self, query_text: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Search for most similar labels.
        
        Args:
            query_text: Company description text
            top_k: Number of results to return
            
        Returns:
            List of dicts with sector, industry, sub_industry, similarity
        """
        if self.embeddings is None:
            raise RuntimeError("Index not built! Call add_labels() first")
        
        # Embed query
        query_emb = self.embed(query_text)
        query_emb = query_emb / (np.linalg.norm(query_emb) + 1e-8)
        
        # Compute cosine similarities (inner product with normalized vectors)
        similarities = np.dot(self.embeddings, query_emb)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            sector, industry, sub_industry = self.labels[idx]
            similarity = float(similarities[idx])
            
            results.append({
                'sector': sector,
                'industry': industry,
                'sub_industry': sub_industry,
                'similarity': similarity,
                'text': self.label_texts[idx]
            })
        
        return results
    
    def save(self, save_dir: str):
        """Save index to disk."""
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        state = {
            'model': self.model,
            'labels': self.labels,
            'label_texts': self.label_texts,
            'embeddings': self.embeddings,
            'dimension': self.dimension
        }
        
        with open(save_path / 'ollama_index.pkl', 'wb') as f:
            pickle.dump(state, f)
        
        print(f"✅ Index saved to {save_dir}")
    
    def load(self, load_dir: str):
        """Load index from disk."""
        load_path = Path(load_dir) / 'ollama_index.pkl'
        
        if not load_path.exists():
            raise FileNotFoundError(f"Index file not found: {load_path}")
        
        with open(load_path, 'rb') as f:
            state = pickle.load(f)
        
        self.model = state['model']
        self.labels = state['labels']
        self.label_texts = state['label_texts']
        self.embeddings = state['embeddings']
        self.dimension = state['dimension']
        
        print(f"✅ Index loaded: {len(self.labels)} labels, dimension={self.dimension}")


def check_ollama_embedding_model(model: str = "nomic-embed-text") -> bool:
    """
    Check if Ollama embedding model is available.
    
    Args:
        model: Model name to check
        
    Returns:
        True if model is available
    """
    try:
        proxies = {"http": None, "https": None}
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            proxies=proxies,
            timeout=5
        )
        
        if response.status_code != 200:
            return False
        
        models = response.json().get('models', [])
        available_names = [m['name'] for m in models]
        
        return model in available_names
        
    except Exception:
        return False

        self.label_texts = data['label_texts']
        self.embeddings = data['embeddings']
        
        print(f"✅ Loaded index: {len(self.label_keys)} labels")
