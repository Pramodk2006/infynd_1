"""
Compare Ollama and Top-K Hierarchical classifiers on company in data/outputs/1
"""
from src.classification.text_builder import build_company_text
from src.classification.topk_classifier import classify_company_from_folder, save_classification_result
from src.classification.ollama_embeddings import OllamaEmbeddingIndex
from src.classification.ollama_llm import classify_with_llm

def classify_with_ollama(company_folder: str):
    """Classify using Ollama pipeline"""
    print("\n" + "="*80)
    print("OLLAMA CLASSIFIER (Embeddings + LLM)")
    print("="*80)
    
    # Load index
    print("Loading Ollama index...")
    index = OllamaEmbeddingIndex()
    index.load('taxonomy_index')
    
    # Get text
    text = build_company_text(company_folder)
    company_name = company_folder.split('/')[-1]
    
    print(f"Company: {company_name}")
    print(f"Text length: {len(text)} characters")
    
    # Search embeddings
    print("\nSearching embeddings (top 20)...")
    candidates = index.search(text, top_k=20)
    print(f"Top match: {candidates[0]['sub_industry']} ({candidates[0]['similarity']:.3f})")
    
    # LLM classification
    print("\nClassifying with llama2:latest...")
    result = classify_with_llm(text, candidates, company_name=company_name)
    
    if result:
        print(f"\n✅ OLLAMA RESULT:")
        print(f"   Sector: {result['sector']}")
        print(f"   Industry: {result['industry']}")
        print(f"   Sub-Industry: {result['sub_industry']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"\n   Top alternatives:")
        for i, c in enumerate(candidates[:3], 1):
            print(f"      {i}. {c['sub_industry']} ({c['similarity']:.3f})")
    
    return result

def main():
    import os
    os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
    
    company_folder = 'data/outputs/1'
    
    # First, show the company text
    text = build_company_text(company_folder)
    print("="*80)
    print("COMPANY DATA PREVIEW")
    print("="*80)
    print(f"Text length: {len(text)} characters")
    print(f"\nFirst 800 characters:")
    print(text[:800])
    print("...")
    
    # 1. Top-K Hierarchical Classifier
    print("\n\n")
    topk_result = classify_company_from_folder(company_folder, method='topk')
    save_classification_result(topk_result, 'company_1_topk.json')
    
    # 2. Ollama Classifier
    print("\n\n")
    ollama_result = classify_with_ollama(company_folder)
    
    # Compare results
    print("\n\n")
    print("="*80)
    print("COMPARISON")
    print("="*80)
    
    if 'final_prediction' in topk_result:
        print("\nTop-K Hierarchical:")
        print(f"  Sector: {topk_result['final_prediction']['sector']}")
        print(f"  Industry: {topk_result['final_prediction']['industry']}")
        print(f"  Sub-Industry: {topk_result['final_prediction']['sub_industry']}")
        print(f"  Confidence: {topk_result['final_prediction']['confidence']:.3f}")
    else:
        print("\nTop-K Hierarchical: FAILED")
        print(f"  Error: {topk_result.get('error', 'Unknown')}")
    
    if ollama_result:
        print("\nOllama (Embedding + LLM):")
        print(f"  Sector: {ollama_result['sector']}")
        print(f"  Industry: {ollama_result['industry']}")
        print(f"  Sub-Industry: {ollama_result['sub_industry']}")
        print(f"  Confidence: {ollama_result['confidence']:.3f}")
    else:
        print("\nOllama: FAILED")
    
    print("="*80)

if __name__ == "__main__":
    main()
