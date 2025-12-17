# Quick Start Guide

## Installation

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

## Usage Examples

### 1. Extract from a Website (Summary Mode)

Extract from main page + 1 key page:

```bash
python main.py extract "https://example.com" "Example Corporation" --crawl-mode summary
```

### 2. Extract from a Website (Full Crawl)

Crawl entire website (up to 50 pages):

```bash
python main.py extract "https://example.com" "Example Corporation" --crawl-mode full --max-pages 50
```

### 3. Extract from PDF

```bash
python main.py extract "path/to/company-brochure.pdf" "Example Corporation"
```

### 4. Extract from HTML File

```bash
python main.py extract "path/to/about.html" "Example Corporation"
```

### 5. Extract from Text File

```bash
python main.py extract "path/to/company-info.txt" "Example Corporation"
```

### 6. Batch Processing

Process multiple sources for one company:

```bash
python main.py batch "Example Corporation" brochure.pdf https://example.com about.html info.txt
```

## CLI Commands

### `extract` - Extract from single source

```bash
python main.py extract [SOURCE] [COMPANY] [OPTIONS]

Options:
  --crawl-mode, -m    Web crawl mode: summary or full (default: summary)
  --max-pages, -p     Maximum pages to crawl in full mode (default: 50)
  --chunk-size, -c    Text chunk size for vector DB (default: 512)
  --output, -o        Output directory (default: data/outputs)
```

### `batch` - Extract from multiple sources

```bash
python main.py batch [COMPANY] [SOURCES...] [OPTIONS]
```

### `list-companies` - List all companies

```bash
python main.py list-companies
```

### `info` - Show company information

```bash
python main.py info "Example Corporation"
```

### `version` - Show version

```bash
python main.py version
```

## Output Structure

Extracted data is saved in the following structure:

```
data/outputs/
└── example-corporation/
    ├── metadata.json          # Company metadata
    ├── index.json             # Source registry
    └── sources/
        ├── 20251217_120000_url_abc12345.json
        ├── 20251217_120500_pdf_def67890.json
        └── 20251217_121000_html_ghi11121.json
```

## Output JSON Schema

Each extracted document has this structure:

```json
{
  "document_id": "uuid-v4",
  "source": {
    "type": "pdf|url|html|text",
    "uri": "original-source-path",
    "company": "company-name",
    "extracted_at": "2025-12-17T10:30:00"
  },
  "metadata": {
    "title": "Document Title",
    "description": "Meta description",
    "page_count": 10,
    "extra": {}
  },
  "content": {
    "raw_text": "full extracted text...",
    "chunks": [
      {
        "chunk_id": "uuid",
        "text": "chunk text...",
        "start_index": 0,
        "end_index": 512,
        "metadata": {}
      }
    ],
    "structured": {
      "headings": [{ "tag": "h1", "text": "..." }],
      "paragraphs": ["..."],
      "lists": [{ "type": "ul", "items": ["..."] }],
      "tables": [{ "headers": [], "rows": [] }],
      "links": [{ "text": "...", "href": "..." }]
    }
  }
}
```

## Features

✅ **Multi-format Support**: URLs, PDFs, HTML files, text files  
✅ **Smart Crawling**: Full site or summary mode (2 pages)  
✅ **Structured Extraction**: Headings, paragraphs, lists, tables  
✅ **Vector DB Ready**: Pre-chunked content with metadata  
✅ **Domain Filtering**: Stays within same domain  
✅ **Robots.txt Compliance**: Respects crawling rules  
✅ **Batch Processing**: Process multiple sources at once  
✅ **Rich CLI**: Beautiful terminal output with progress bars

## Tips

- **Use summary mode** for quick overviews (homepage + about page)
- **Use full mode** for comprehensive extraction (entire website)
- **Adjust chunk size** based on your vector DB requirements (default: 512 chars)
- **Process PDFs and URLs together** using batch mode for complete company profiles
- All outputs are **JSON** files ready for vector database ingestion

## Next Steps

After extraction, you can:

1. Load JSON files into your vector database
2. Use the LLM integration (coming in next stage) for summarization
3. Build the React dashboard for visualization
4. Implement company profile fusion logic
