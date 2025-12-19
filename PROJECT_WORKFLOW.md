# B2B Data Fusion Engine - Project Workflow

This document outlines the end-to-end workflow for the "Prepare Summary" functionality in the B2B Data Fusion Engine.

## 1. User Input & Initiation
*   **Action**: User selects a company (e.g., "OfficeRnD") in the frontend and clicks **"Prepare Summary"**.
*   **API Call**: Frontend sends a `POST` request to `/api/companies/<company>/enhanced/prepare`.
*   **Status**: The system immediately returns a "preparing" status, and the frontend begins polling for results.

## 2. Background Processing (Backend)
The `_prepare_enhanced_data_background` task in `api_server.py` orchestrates the following steps:

### A. Hierarchical Classification (Top-K)
*   **Function**: `classify_company_topk_v2`
*   **Model**: `qwen2.5:7b` (via Ollama)
*   **Process**:
    1.  **Sector Identification**: Analyzes company text to find the top 5 most likely sectors.
    2.  **Industry Refinement**: For the top sectors, identifies the top 5 industries.
    3.  **Sub-Industry Precision**: Drills down to find the specific sub-industry (e.g., "Business Support").
    4.  **LLM Re-ranking**: The LLM reviews the top candidates and selects the best match based on evidence density and specificity.

### B. Comprehensive Data Extraction
*   **Function**: `extract_all_data` -> `extract_all_business_info_llm`
*   **Model**: `qwen2.5:7b`
*   **Process**:
    1.  **Text Aggregation**: Combines text from all available source documents (PDFs, web pages) for the company.
    2.  **Prompt Engineering**: Constructs a detailed prompt containing the company text and the *known classification* (from Step A).
    3.  **LLM Extraction**: The AI analyzes the text to extract:
        *   **Core Details**: Company Name, Acronym, Description (generated if missing).
        *   **Contact Info**: Address, Phone (Sales/Main/Mobile/Fax), Email, VAT, Registration Number.
        *   **Business Logic**: Hours of Operation, HQ Indicator.
        *   **Lists**: Team Members (People), Certifications, Services & Solutions.
    4.  **Structured Output**: Returns a JSON object where every field includes a `value`, `confidence` score, and `explanation`.

## 3. Frontend Display & Export
*   **Polling**: The React frontend polls `/api/companies/<company>/enhanced` until the status is "ready".
*   **Rendering**:
    *   **Card View**: Displays a rich, visual summary of the company.
    *   **Table View**: Shows a detailed line-by-line view of all extracted fields.
*   **CSV Export**:
    *   User clicks "Download CSV".
    *   Generates a CSV file matching the `Topic2_Output_Format` requirements.
    *   Includes `Domain` as the first column and expands nested lists (People, Services) into rows.

## System Architecture
*   **Frontend**: React + Vite (Port 3000)
*   **Backend**: Flask API (Port 5000)
*   **AI Engine**: Ollama running `qwen2.5:7b` (Port 11434)
*   **Data Storage**: Local JSON files in `data/outputs/` and SQLite cache.
