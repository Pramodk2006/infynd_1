# Ollama-Based Classification Pipeline

Complete local classification system using Ollama embeddings + LLM for industry classification.

## Architecture

```
Company Text → Ollama Embeddings → FAISS Search (top-20) → LLM Re-rank → Classification
```

### Components

1. **ollama_embeddings.py**: Vector embeddings using Ollama API

   - Model: `nomic-embed-text` (274MB)
   - FAISS indexing with cosine similarity
   - 3680 taxonomy labels embedded

2. **ollama_llm.py**: LLM-based re-ranking

   - Model: `llama2:latest` (3.8GB)
   - JSON-structured prompts
   - Candidate scoring with reasoning

3. **ollama_pipeline.py**: Complete orchestration
   - Initialize index from taxonomy
   - Classify companies end-to-end
   - Fallback strategies

## Setup

### 1. Install Ollama

**Windows:**

```bash
# Download from https://ollama.com/download
```

**Mac:**

```bash
brew install ollama
```

**Linux:**

```bash
curl https://ollama.ai/install.sh | sh
```

### 2. Start Ollama Server

```bash
ollama serve
```

Leave this running in a separate terminal.

### 3. Pull Required Models

Run the automated setup script:

```bash
python setup_ollama_models.py
```

Or manually:

```bash
# Embedding model (required)
ollama pull nomic-embed-text

# LLM model (required)
ollama pull llama2:latest
```

### 4. Verify Setup

```bash
ollama list
```

You should see:

- `nomic-embed-text:latest`
- `llama2:latest`

## Usage

### Test the Pipeline

```bash
python test_ollama_pipeline.py
```

This will:

1. Load the taxonomy (3680 entries)
2. Build embedding index (takes ~5-10 minutes first time)
3. Save index to `taxonomy_index/` (reused on next run)
4. Classify Zoho, NVIDIA, Infynd

### Integrate into Your App

```python
from src.classification.taxonomy import load_taxonomy
from src.classification.ollama_pipeline import (
    initialize_ollama_classifier,
    classify_with_ollama
)

# One-time initialization
taxonomy = load_taxonomy("data/sub_Industry_Classification-in.csv")
index = initialize_ollama_classifier(
    taxonomy,
    embedding_model="nomic-embed-text",
    index_path="taxonomy_index"  # Cache for faster startup
)

# Classify a company
result = classify_with_ollama(
    "path/to/company/folder",
    llm_model="llama2:latest",
    top_k=20  # Number of embedding candidates
)

print(f"Sector: {result.sector.label}")
print(f"Industry: {result.industry.label}")
print(f"Sub-Industry: {result.sub_industry.label}")
print(f"Confidence: {result.sector.score:.2f}")
```

## How It Works

### Step 1: Embedding Search (Fast)

```python
# Embed company description
company_embedding = embed(company_text)

# Find top-20 similar taxonomy entries
candidates = faiss_search(company_embedding, top_k=20)
# Example: [
#   {"sub_industry": "Enterprise Software", "similarity": 0.85},
#   {"sub_industry": "Cloud Computing", "similarity": 0.82},
#   ...
# ]
```

### Step 2: LLM Re-ranking (Accurate)

```python
# LLM analyzes company + candidates
prompt = f"""
Company: {company_text}

Choose the BEST match from these candidates:
1. Enterprise Software (Industry: Software Development, Sector: IT)
2. Cloud Computing (Industry: Internet Services, Sector: IT)
...

Respond with JSON:
{{"choice": 1, "confidence": 0.9, "reasoning": "..."}}
"""

llm_result = ollama.generate(prompt)
# Returns: {"sector": "IT", "industry": "Software Development", ...}
```

### Step 3: Validation

- Verify selected classification exists in taxonomy
- Fallback to top embedding match if LLM fails
- Return structured result with SIC codes

## Performance

**First Run:**

- Build index: 5-10 minutes (embedding 3680 labels)
- Save to disk: Instant on subsequent runs

**Classification:**

- Embedding search: <1 second
- LLM re-ranking: 2-5 seconds
- Total: ~3-6 seconds per company

## Models

### Embedding Models

- **nomic-embed-text** (default): 274MB, 768-dim, optimized for semantic search
- **mxbai-embed-large**: 670MB, 1024-dim, higher quality but slower

### LLM Models

- **llama2:latest** (default): 3.8GB, good balance of speed/quality
- **mistral:latest**: 4.1GB, faster, good for structured output
- **gemma2:2b**: 1.6GB, very fast but lower quality

## Comparison: Old vs New

### Phase 2 (Deterministic)

```
TF-IDF (55%) + Keywords (25%) + Domain Signals (20%)
✅ Fast (<1 sec)
❌ Struggles with ambiguous cases
❌ No semantic understanding
```

### Ollama Pipeline (Semantic + LLM)

```
Embeddings → FAISS → LLM Re-rank
✅ Semantic understanding
✅ Handles ambiguous cases
✅ LLM provides reasoning
❌ Slower (3-6 sec)
```

## Troubleshooting

### Ollama not running

```bash
# Start the server
ollama serve
```

### Model not found

```bash
# Pull the model
ollama pull nomic-embed-text
```

### Proxy issues

The code already includes proxy bypass for localhost:

```python
proxies = {"http": None, "https": None}
```

### Index build fails

Delete the cache and rebuild:

```bash
rm -rf taxonomy_index/
python test_ollama_pipeline.py
```

## Files

```
src/classification/
├── ollama_embeddings.py    # Embedding generation + FAISS
├── ollama_llm.py           # LLM classification
├── ollama_pipeline.py      # Complete orchestration
└── taxonomy.py             # Taxonomy loading

test_ollama_pipeline.py     # Test script
setup_ollama_models.py      # Model downloader

taxonomy_index/             # Cached embeddings (generated)
└── ollama_index.pkl        # 3680 pre-computed vectors
```

## Next Steps

1. **Run the setup**: `python setup_ollama_models.py`
2. **Test the pipeline**: `python test_ollama_pipeline.py`
3. **Integrate into Flask API**: Add Ollama endpoints to your web service
4. **Compare results**: Test against Phase 2 deterministic classifier

## References

- [Ollama Documentation](https://github.com/ollama/ollama)
- [nomic-embed-text](https://ollama.com/library/nomic-embed-text)
- [Llama 2](https://ollama.com/library/llama2)
