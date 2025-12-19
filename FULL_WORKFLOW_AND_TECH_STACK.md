# B2B Data Fusion Engine: Full Workflow & Technology Stack

This document details the end-to-end technical workflow of the system, mapping each functional step to the specific technologies and algorithms used.

## 1. High-Level Architecture

*   **Frontend**: React (Vite) - Interactive UI for triggering analysis and viewing results.
*   **Backend API**: Python (Flask) - Orchestrates the entire pipeline.
*   **AI Engine**: Ollama (Local LLM Server) - Running `qwen2.5:7b` for text generation and reasoning.
*   **ML Core**: Scikit-Learn (TF-IDF) & SentenceTransformers (Embeddings) - For statistical and semantic classification.

---

## 2. Detailed Workflow

### Step 1: Input & Text Construction
**Goal**: Convert raw scattered data (PDFs, HTML, JSON) into a clean, coherent text representation of the company.

*   **Process**:
    1.  Aggregates text from all source files in `data/outputs/<company>/sources`.
    2.  Applies "Source Quality Weighting" to prioritize high-value pages (e.g., "About Us", "Products" get 3x weight; "Contact" gets 1x).
    3.  Cleans noise (cookies, navigation menus) using regex patterns.
*   **Technology Used**:
    *   **Python**: Core logic (`text_builder.py`).
    *   **Regex (`re`)**: Pattern matching for noise removal.
    *   **JSON**: Data serialization for source documents.

### Step 2: Intelligent Summarization (The "Brain")
**Goal**: Understand the business before classifying it. Generate a human-readable "Executive Summary".

*   **Process**:
    1.  Feeds the cleaned text into the LLM.
    2.  Prompts the AI to generate a structured summary with headers: **Core Business**, **Key Offerings**, **Target Audience**, **Value Proposition**.
    3.  Instructions enforce bullet points and professional tone.
*   **Technology Used**:
    *   **Ollama**: Local AI Inference Server.
    *   **Model**: `qwen2.5:7b` (Qwen 2.5 7-Billion Parameter Model).
    *   **Prompt Engineering**: Context-aware prompts to ensure structured output.

### Step 3: Hierarchical Classification (Sector -> Industry -> Sub-Industry)
**Goal**: Scientifically categorize the company into the correct market taxonomy.

*   **Process**:
    1.  **Vectorization**: Converts company text and taxonomy labels into mathematical vectors.
    2.  **Scoring (The Hybrid Algorithm)**:
        *   **35% TF-IDF**: Matches specific keywords (statistical).
        *   **30% Semantic Embeddings**: Matches meaning/concepts (AI).
        *   **20% Keyword Overlap**: Matches exact terminology.
        *   **15% Domain Signal**: Weighting from high-value sources (Title tags).
    3.  **LLM Re-Ranking**: If the top 2 sectors are close in score, the LLM reviews the summary and picks the winner (Logic check).
*   **Technology Used**:
    *   **Scikit-Learn**: `TfidfVectorizer`, `cosine_similarity`.
    *   **Sentence Transformers**: `all-MiniLM-L6-v2` (for semantic embeddings).
    *   **NumPy**: Efficient matrix operations for score calculation.

### Step 4: Chained Data Extraction
**Goal**: Extract precise structured data fields (Phone, Email, Registration #) based on the Classification and Summary.

*   **Process**:
    1.  Takes the **Executive Summary** (from Step 2) as the input context (Source of Truth).
    2.  Runs a second LLM pass to extract specific JSON fields:
        *   **One-Liner**: Generates a compelling elevator pitch.
        *   **Contact Info**: Extracts Phone, Email, Address.
        *   **Logic**: Determines "Hours of Operation" and "HQ Location".
    3.  Validates extracted domains using URL parsing.
*   **Technology Used**:
    *   **Model**: `qwen2.5:7b` (Chained execution).
    *   **Python (`urllib`)**: Robust domain parsing.
    *   **JSON**: Structured data formatting.

### Step 5: Frontend Presentation & Export
**Goal**: Display the insights to the user and allow export.

*   **Process**:
    1.  **Polls** the API until the background task is complete.
    2.  **Renders** the Enhanced Summary Card.
    3.  **Hides** empty sections dynamically (conditional rendering).
    4.  **Generates CSV** on the client side for download.
*   **Technology Used**:
    *   **React**: Component-based UI (`EnhancedSummaryCard.jsx`).
    *   **CSS**: Styling for the "One-Liner" box and tables.
    *   **JavaScript (Blob API)**: Client-side CSV file generation.
