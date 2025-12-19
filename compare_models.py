"""
Compare Qwen 2.5 7B vs Llama 3.2 3B for company summarization
"""
import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

from src.classification.text_builder import _summarize_with_ollama, build_company_text

# Test on kredily
company_folder = 'data/outputs/kredily'

# Get raw text (without summarization)
from src.classification.text_builder import (
    Path, json, _extract_text_from_document, _clean_text, _is_priority_source
)

# Extract raw text
company_path = Path(company_folder)
sources_path = company_path / "sources"
priority_docs = []
regular_docs = []

for json_file in sources_path.glob("*.json"):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            doc = json.load(f)
        source_uri = doc.get("source", {}).get("uri", "")
        if _is_priority_source(source_uri):
            priority_docs.append(doc)
        else:
            regular_docs.append(doc)
    except:
        continue

all_text_parts = []
for doc in priority_docs:
    text_parts = _extract_text_from_document(doc, weight_multiplier=2.0)
    all_text_parts.extend(text_parts)
for doc in regular_docs:
    text_parts = _extract_text_from_document(doc, weight_multiplier=1.0)
    all_text_parts.extend(text_parts)

combined_text = " ".join(all_text_parts)
cleaned_text = _clean_text(combined_text)[:10000]

print(f"{'='*80}")
print(f"RAW TEXT LENGTH: {len(cleaned_text)} characters")
print(f"{'='*80}\n")

# Test Llama 3.2 3B
print("Testing Llama 3.2 3B (Balanced - 2GB)")
print("-" * 80)
llama_summary = _summarize_with_ollama(cleaned_text, company_folder, model="llama3.2:3b")
if llama_summary:
    print(f"Length: {len(llama_summary)} chars\n")
    print(llama_summary)
print(f"\n{'='*80}\n")

# Test Qwen 2.5 7B
print("Testing Qwen 2.5 7B Instruct (High Accuracy - 4.7GB)")
print("-" * 80)
qwen_summary = _summarize_with_ollama(cleaned_text, company_folder, model="qwen2.5:7b")
if qwen_summary:
    print(f"Length: {len(qwen_summary)} chars\n")
    print(qwen_summary)
print(f"\n{'='*80}\n")

# Test Gemma 3 4B
print("Testing Gemma 3 4B (High Accuracy - 3.3GB)")
print("-" * 80)
gemma_summary = _summarize_with_ollama(cleaned_text, company_folder, model="gemma3:4b")
if gemma_summary:
    print(f"Length: {len(gemma_summary)} chars\n")
    print(gemma_summary)
print(f"\n{'='*80}\n")

print("\n📊 COMPARISON SUMMARY:")
print("="*80)
print(f"Llama 3.2 3B:  {len(llama_summary) if llama_summary else 0} chars - Balanced speed/quality")
print(f"Qwen 2.5 7B:   {len(qwen_summary) if qwen_summary else 0} chars - Best instruction following")
print(f"Gemma 3 4B:    {len(gemma_summary) if gemma_summary else 0} chars - Google's best small model")
print("="*80)
