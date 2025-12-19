"""
Simple classification test without unicode issues.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.classification import load_taxonomy, classify_company

def main():
    print("="*60)
    print("Testing Hybrid Classification System")
    print("="*60)
    
    # Load taxonomy
    taxonomy_path = Path("data/sub_Industry_Classification-in.csv")
    print(f"\nLoading taxonomy from: {taxonomy_path}")
    
    taxonomy = load_taxonomy(str(taxonomy_path))
    print(f"Loaded: {len(taxonomy.unique_sectors)} sectors, {len(taxonomy.unique_industries)} industries, {len(taxonomy.unique_subindustries)} sub-industries")
    
    # Test companies
    companies = ["zoho", "nvidia", "infynd"]
    
    for company in companies:
        print(f"\n{'='*60}")
        print(f"Classifying: {company.upper()}")
        print(f"{'='*60}")
        
        company_folder = f"data/outputs/{company}"
        
        try:
            # Classify with LLM enabled
            result = classify_company(company_folder, taxonomy, use_llm=True)
            
            if result:
                print(f"\nSector: {result.sector.label} (score: {result.sector.score:.4f})")
                print(f"Industry: {result.industry.label} (score: {result.industry.score:.4f})")
                print(f"Sub-Industry: {result.sub_industry.label} (score: {result.sub_industry.score:.4f})")
                
                if hasattr(result, 'extra_attributes') and result.extra_attributes:
                    print(f"\nExtra Attributes:")
                    for key, value in result.extra_attributes.items():
                        print(f"  {key}: {value}")
            else:
                print("Classification returned None")
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
