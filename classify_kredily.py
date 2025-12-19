"""
Classify Kredily company using Ollama pipeline
"""
from src.classification.ollama_pipeline import initialize_ollama_classifier, classify_with_ollama
from src.classification.text_builder import build_company_text
from src.classification.taxonomy import load_taxonomy

def main():
    print("="*80)
    print("CLASSIFYING KREDILY")
    print("="*80)
    
    # Load taxonomy
    print("\n📚 Loading taxonomy...")
    taxonomy = load_taxonomy('data/sub_Industry_Classification-in.csv')
    print(f"✅ Loaded {len(taxonomy.unique_subindustries)} taxonomy entries")
    
    # Initialize classifier
    print("\n🚀 Initializing Ollama classifier...")
    initialize_ollama_classifier(taxonomy, index_path='taxonomy_index')
    
    # Build company text
    print("\n📄 Building company text...")
    text = build_company_text('data/outputs/kredily')
    print(f"✅ Text extracted: {len(text)} characters")
    
    # Classify
    print("\n🔍 Classifying...")
    result = classify_with_ollama('kredily', text)
    
    # Display results
    print("\n" + "="*80)
    print("✅ CLASSIFICATION RESULT")
    print("="*80)
    print(f"Company: kredily")
    print(f"Sector: {result.sector}")
    print(f"Industry: {result.industry}")
    print(f"Sub-Industry: {result.sub_industry}")
    print(f"SIC Code: {result.sic_code}")
    print(f"SIC Description: {result.sic_description}")
    print("="*80)

if __name__ == "__main__":
    main()
