from src.classification import load_taxonomy, build_company_text
from src.classification.similarity import compute_label_scores, get_top_candidates

tax = load_taxonomy('data/sub_Industry_Classification-in.csv')
text = build_company_text('data/outputs/nvidia')

print("NVIDIA Company Text (first 500 chars):")
print(text[:500])
print(f"\nTotal length: {len(text)} characters\n")

# Test flat industry classification
scores = compute_label_scores(text, tax.unique_industries, tax.industry_texts)
top = get_top_candidates(scores, top_k=10)

print("Top 10 industries for NVIDIA (flat classification):")
for i, c in enumerate(top):
    print(f"{i+1}. {c['label']}: {c['score']:.4f}")

# Check if IT-related industries are in the list
it_keywords = ['software', 'technology', 'ai', 'computing', 'data', 'semiconductor']
print("\nIT-related industries in top 20:")
top20 = get_top_candidates(scores, top_k=20)
for c in top20:
    label_lower = c['label'].lower()
    if any(kw in label_lower for kw in it_keywords):
        print(f"  - {c['label']}: {c['score']:.4f}")
