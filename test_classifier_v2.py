"""
Test script to compare Top-K v1 vs Enhanced v2 classifier
"""

import sys
import os
sys.path.insert(0, 'src')

# Fix Windows console encoding
if os.name == 'nt':  # Windows
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from classification.topk_classifier import classify_company_from_folder
from classification.classifier_topk_v2 import classify_company_topk_v2
import json


def compare_classifiers(company_folder: str):
    """Run both classifiers and compare results."""
    
    print(f"\n{'='*80}")
    print(f"COMPARING CLASSIFIERS FOR: {company_folder}")
    print(f"{'='*80}\n")
    
    # Run v1 (original)
    print("v1: Running Top-K v1 (original)...")
    print("-" * 80)
    v1_result = classify_company_from_folder(company_folder)
    
    print("\n\n")
    
    # Run v2 (enhanced)
    print("v2: Running Top-K v2 (enhanced with specificity, source quality, LLM)...")
    print("-" * 80)
    v2_result = classify_company_topk_v2(
        company_folder,
        use_ollama_summary=True,
        use_llm_rerank=True,
        llm_model="qwen2.5:7b"
    )
    
    # Compare results
    print("\n\n")
    print(f"{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}\n")
    
    # V1 results
    v1_final = v1_result.get('final_prediction', {})
    print("[v1] TOP-K V1 (Original):")
    print(f"   Sector: {v1_final.get('sector')}")
    print(f"   Industry: {v1_final.get('industry')}")
    print(f"   Sub-Industry: {v1_final.get('sub_industry')}")
    print(f"   Confidence: {v1_final.get('confidence', 0)*100:.1f}%")
    print()
    
    # V2 results
    v2_final = v2_result.get('final_prediction', {})
    print("[v2] TOP-K V2 (Enhanced):")
    print(f"   Sector: {v2_final.get('sector')}")
    print(f"   Industry: {v2_final.get('industry')}")
    print(f"   Sub-Industry: {v2_final.get('sub_industry')}")
    print(f"   Confidence: {v2_final.get('confidence', 0)*100:.1f}%")
    print(f"   Evidence Density: {v2_final.get('evidence_density', 0)*100:.1f}%")
    print(f"   Selection Method: {v2_final.get('selection_method')}")
    if v2_final.get('llm_reasoning'):
        print(f"   LLM Reasoning: {v2_final.get('llm_reasoning')}")
    print()
    
    # Highlight differences
    if v1_final.get('sector') != v2_final.get('sector'):
        print("!!! SECTOR CHANGED:")
        print(f"   v1: {v1_final.get('sector')}")
        print(f"   v2: {v2_final.get('sector')}")
        print()
    
    if v1_final.get('industry') != v2_final.get('industry'):
        print("!!! INDUSTRY CHANGED:")
        print(f"   v1: {v1_final.get('industry')}")
        print(f"   v2: {v2_final.get('industry')}")
        print()
    
    if v1_final.get('sub_industry') != v2_final.get('sub_industry'):
        print("*** SUB-INDUSTRY CHANGED (specificity boost working!):")
        print(f"   v1: {v1_final.get('sub_industry')}")
        print(f"   v2: {v2_final.get('sub_industry')}")
        print()
    
    # Show top sub-industries comparison
    print("\nTOP SUB-INDUSTRIES COMPARISON:")
    print("\n[v1] V1 Top 5:")
    for sub in v1_result.get('top_subindustries', [])[:5]:
        print(f"   {sub.get('rank')}. {sub.get('label')} - {sub.get('score', 0):.3f}")
    
    print("\n[v2] V2 Top 5 (with specificity scores):")
    for sub in v2_result.get('top_subindustries', [])[:5]:
        print(f"   {sub.get('rank')}. {sub.get('label')} - "
              f"{sub.get('score', 0):.3f} (spec: {sub.get('specificity', 0):.2f})")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Test on multiple companies
    test_companies = ['kredily', '1', '2', '3']
    
    if len(sys.argv) > 1:
        # Test specific company from command line
        company = sys.argv[1]
        compare_classifiers(company)
    else:
        # Test all
        for company in test_companies:
            try:
                compare_classifiers(company)
                print("\n" + "="*80)
                print("Press Enter to continue to next company...")
                print("="*80)
                input()
            except Exception as e:
                print(f"❌ Error testing {company}: {e}")
                continue
