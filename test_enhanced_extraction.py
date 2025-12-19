"""
Test script for enhanced data extraction
"""
import json
from src.extraction.enhanced_extractor import extract_all_data
from src.classification.classifier_topk_v2 import classify_company_topk_v2

def test_enhanced_extraction(company_name):
    """Test enhanced extraction on a company"""
    print(f"\n{'='*80}")
    print(f"Testing Enhanced Extraction: {company_name}")
    print(f"{'='*80}\n")
    
    # Step 1: Classify the company
    print("Step 1: Running classification...")
    classification_result = classify_company_topk_v2(
        company_name,
        use_ollama_summary=True,
        use_llm_rerank=False,
        k_sectors=5,
        k_industries=5,
        k_subindustries=10
    )
    
    print(f"✓ Sector: {classification_result['final_prediction']['sector']}")
    print(f"✓ Industry: {classification_result['final_prediction']['industry']}")
    print(f"✓ Sub-Industry: {classification_result['final_prediction']['sub_industry']}")
    print(f"✓ SIC Code: {classification_result['final_prediction']['sic_code']}")
    print(f"✓ Confidence: {classification_result['final_prediction']['confidence']:.1%}\n")
    
    # Step 2: Extract all data
    print("Step 2: Extracting comprehensive data...")
    company_path = f"data/outputs/{company_name}"
    enhanced_data = extract_all_data(company_path, classification_result)
    
    # Print extracted data
    print(f"\n{'='*80}")
    print("EXTRACTED DATA SUMMARY")
    print(f"{'='*80}\n")
    
    # Mandatory fields
    print("📋 MANDATORY FIELDS:")
    print(f"  Domain: {enhanced_data['domain']}")
    print(f"  Short Description: {enhanced_data['short_description'][:100]}...")
    print(f"  Sector: {enhanced_data['sector']}")
    print(f"  Industry: {enhanced_data['industry']}")
    print(f"  Sub-Industry: {enhanced_data['sub_industry']}")
    print(f"  SIC Code: {enhanced_data['sic_code']}")
    print(f"  Tags: {', '.join(enhanced_data['tags'][:5])}")
    
    # Company identity
    print(f"\n🏢 COMPANY IDENTITY:")
    print(f"  Company Name: {enhanced_data['company_name']}")
    print(f"  Acronym: {enhanced_data['acronym']}")
    print(f"  Domain Status: {enhanced_data['domain_status']}")
    print(f"  Registration Number: {enhanced_data['company_registration_number']}")
    print(f"  VAT Number: {enhanced_data['vat_number']}")
    
    # Contact information
    print(f"\n📞 CONTACT INFORMATION:")
    print(f"  Email: {enhanced_data['email']}")
    print(f"  All Emails: {', '.join(enhanced_data['all_emails'][:3])}")
    print(f"  Phone: {enhanced_data['phone']}")
    print(f"  Address: {enhanced_data['full_address']}")
    print(f"  Hours: {enhanced_data['hours_of_operation']}")
    
    # People
    if enhanced_data['people'] and enhanced_data['people'][0]['name'] != '-':
        print(f"\n👥 PEOPLE:")
        for idx, person in enumerate(enhanced_data['people'][:3], 1):
            print(f"  {idx}. {person['name']} - {person['title']}")
            if person['email'] != '-':
                print(f"     Email: {person['email']}")
    
    # Certifications
    if enhanced_data['certifications'] and enhanced_data['certifications'][0] != '-':
        print(f"\n🏆 CERTIFICATIONS:")
        for cert in enhanced_data['certifications']:
            print(f"  • {cert}")
    
    # Services
    if enhanced_data['services'] and enhanced_data['services'][0]['service'] != '-':
        print(f"\n🛠️ SERVICES:")
        for idx, service in enumerate(enhanced_data['services'][:5], 1):
            print(f"  {idx}. {service['service']} ({service['type']})")
    
    print(f"\n{'='*80}")
    print(f"Total Text Length: {enhanced_data['text_length']:,} characters")
    print(f"Extraction Timestamp: {enhanced_data['extraction_timestamp']}")
    print(f"{'='*80}\n")
    
    # Save to file
    output_file = f"data/outputs/{company_name}_enhanced.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Enhanced data saved to: {output_file}\n")
    
    return enhanced_data

if __name__ == "__main__":
    # Test on all three companies
    companies = ["kredily", "1", "3"]
    
    for company in companies:
        try:
            test_enhanced_extraction(company)
        except Exception as e:
            print(f"❌ Error testing {company}: {e}\n")
    
    print("\n✅ All tests complete!")
