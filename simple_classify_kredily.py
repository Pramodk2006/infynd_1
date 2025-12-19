"""
Simple Ollama classification for Kredily
"""
from src.classification.ollama_embeddings import OllamaEmbeddingIndex
from src.classification.ollama_llm import classify_with_llm
from src.classification.taxonomy import load_taxonomy
from src.classification.text_builder import build_company_text

def main():
    # Load taxonomy
    print("📚 Loading taxonomy...")
    taxonomy = load_taxonomy('data/sub_Industry_Classification-in.csv')
    print(f"✅ Loaded {len(taxonomy.unique_subindustries)} entries")
    
    # Initialize embeddings
    print("\n🚀 Loading index...")
    index = OllamaEmbeddingIndex()
    index.load('taxonomy_index')
    print(f"✅ Index loaded: {len(index.labels)} labels")
    
    # Get company text
    print("\n📄 Extracting kredily text...")
    text = build_company_text('data/outputs/kredily')
    print(f"✅ Text length: {len(text)} characters")
    
    # Classify
    print("\n🔍 Classifying kredily...")
    print(f"   Searching embeddings (top 20)...")
    candidates = index.search(text, top_k=20)
    print(f"✅ Found {len(candidates)} candidates")
    print(f"   Top match: {candidates[0]['sub_industry']} ({candidates[0]['similarity']:.3f})")
    
    print("\n🤖 Classifying with llama2:latest...")
    result = classify_with_llm(text, candidates, company_name="kredily")
    
    if result:
        print(f"\n✅ LLM selected: {result['sector']} → {result['industry']} → {result['sub_industry']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        
        print(f"\n{'='*80}")
        print("✅ FINAL RESULT FOR KREDILY:")
        print(f"{'='*80}")
        print(f"   Sector: {result['sector']} (confidence: {result['confidence']:.3f})")
        print(f"   Industry: {result['industry']}")
        print(f"   Sub-Industry: {result['sub_industry']}")
        
        print(f"\n   Top alternatives:")
        for i, c in enumerate(candidates[:3], 1):
            print(f"      {i}. {c['sub_industry']} ({c['similarity']:.3f})")
        print(f"{'='*80}")
    else:
        print("❌ Classification failed")

if __name__ == "__main__":
    main()
