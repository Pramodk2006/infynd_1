### How Sector Classification Works

The system uses a multi-layered approach to identify the correct sector for a company. It combines statistical analysis, keyword matching, and semantic understanding.

The total score for each sector is calculated using the following weighted formula:

`Total Score = (35% * TF-IDF) + (20% * Keyword Overlap) + (15% * Domain Signal) + (30% * Semantic Embeddings)`

#### The 4 Layers of Analysis:

1.  **TF-IDF Cosine Similarity (35% Weight)**
    *   **What it does:** Compares the frequency of important words in the company's text against the standard vocabulary of each sector.
    *   **Why:** It finds statistically significant word patterns (e.g., "patient", "diagnosis", "clinic" strongly correlate with text in the "Health Care" sector).

2.  **Semantic Embeddings (30% Weight)**
    *   **What it does:** Uses AI (Sentence Transformers) to understand the *meaning* of the text, not just exact word matches.
    *   **Why:** It connects concepts. For example, if a company mentions "neural networks", the AI knows this is related to the "Technology" sector, even if the word "Technology" isn't explicitly used.

3.  **Keyword Overlap (20% Weight)**
    *   **What it does:** Checks for direct matches of specific terminology.
    *   **Why:** Ensures that if a company uses specific industry jargon, it gets credit for it.

4.  **Domain Signal (15% Weight)**
    *   **What it does:** Looks for "strong signals" in specific parts of the text (like the `<title>` tag, meta description, or "About Us" section).
    *   **Why:** Information in these key areas is usually more reliable than random text on a page.

#### Final Selection Process
1.  **Ranking:** All potential sectors are ranked based on their Total Score.
2.  **Top-K Selection:** The top 5 sectors are selected as candidates.
3.  **Specificity Scoring:** A bonus score is applied to more specific sectors to favor precise classification over generic ones.
4.  **LLM Re-ranking (The "Judge"):** If the top scores are close (low confidence margin), the `qwen2.5:7b` AI model reviews the top candidates and makes the final decision based on the generated business summary.
