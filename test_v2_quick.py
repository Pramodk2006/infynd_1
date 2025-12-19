"""
Quick test of enhanced classifier v2
"""

import sys
sys.path.insert(0, 'src')

from classification.classifier_topk_v2 import classify_company_topk_v2

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else 'kredily'
    
    print(f"\nTesting Enhanced Classifier V2 on: {company}\n")
    
    result = classify_company_topk_v2(
        company,
        use_ollama_summary=True,
        use_llm_rerank=False,  # Disable LLM for faster testing
        k_sectors=5,
        k_industries=5,
        k_subindustries=10
    )
    
    if "error" in result:
        print(f"\nERROR: {result['error']}")
    else:
        final = result['final_prediction']
        print(f"\n{'='*80}")
        print("FINAL RESULT:")
        print(f"{'='*80}")
        print(f"Sector: {final['sector']}")
        print(f"Industry: {final['industry']}")
        print(f"Sub-Industry: {final['sub_industry']}")
        print(f"Confidence: {final['confidence']*100:.1f}%")
        print(f"Evidence Density: {final['evidence_density']*100:.1f}%")
        print(f"Selection Method: {final['selection_method']}")
        
        print(f"\nTop 5 Sub-Industries (with specificity):")
        for sub in result['top_subindustries'][:5]:
            print(f"  {sub['rank']}. {sub['label']}")
            print(f"      Score: {sub['score']:.3f}, Specificity: {sub['specificity']:.2f}")
