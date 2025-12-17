# Visual Workflow Guide

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT SOURCES                            │
├─────────────────────────────────────────────────────────────────┤
│  📄 PDF Files    🌐 URLs    📝 HTML Files    📋 Text Files      │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTOR FACTORY                             │
│              (Auto-detect source type)                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├────► PDFExtractor (PyMuPDF)
             ├────► HTMLExtractor (BeautifulSoup4)
             ├────► URLExtractor (httpx + BS4)
             └────► TextExtractor
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTENT EXTRACTION                            │
├─────────────────────────────────────────────────────────────────┤
│  • Parse document structure                                      │
│  • Extract text content                                          │
│  • Extract metadata (title, author, date)                        │
│  • Extract structured elements (headings, lists, tables)         │
│  • Clean and normalize text                                      │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TEXT PROCESSING                               │
├─────────────────────────────────────────────────────────────────┤
│  • Clean whitespace and formatting                               │
│  • Remove unwanted elements (scripts, styles)                    │
│  • Chunk text (512 chars, 50 overlap)                           │
│  • Break at sentence boundaries                                  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT MODEL                                │
│                   (Pydantic Validation)                          │
├─────────────────────────────────────────────────────────────────┤
│  Document {                                                      │
│    document_id: UUID                                             │
│    source: {type, uri, company, timestamp}                       │
│    metadata: {title, description, page_count}                    │
│    content: {                                                    │
│      raw_text: str                                               │
│      chunks: [ContentChunk]                                      │
│      structured: StructuredContent                               │
│    }                                                             │
│  }                                                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT STORE                                │
│                   (JSON File Storage)                            │
├─────────────────────────────────────────────────────────────────┤
│  data/outputs/{company}/                                         │
│    ├── metadata.json                                             │
│    ├── index.json                                                │
│    └── sources/                                                  │
│        └── {timestamp}_{type}_{id}.json                          │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Web Crawling Modes

### Summary Mode (Default)

```
┌──────────────────────────────────────────────────────────────┐
│                    SUMMARY MODE                               │
│              (Fast, 2 pages maximum)                          │
└──────────────────────────────────────────────────────────────┘

Step 1: Fetch Homepage
    ↓
    https://company.com
    ↓
    Extract content
    ↓
Step 2: Find key page (about/products/services)
    ↓
    https://company.com/about
    ↓
    Extract content
    ↓
Step 3: Combine & return

Result: Quick company overview from 2 pages
Time: ~3 seconds (1s delay between requests)
```

### Full Mode

```
┌──────────────────────────────────────────────────────────────┐
│                      FULL MODE                                │
│         (Comprehensive, up to max_pages)                      │
└──────────────────────────────────────────────────────────────┘

Step 1: Start at homepage
    ↓
    https://company.com
    ↓
Step 2: Extract all internal links
    ↓
    Queue: [/about, /products, /team, /contact, ...]
    ↓
Step 3: Visit each page (BFS)
    ├─► Check robots.txt
    ├─► Skip if visited
    ├─► Extract content
    ├─► Find new links
    └─► Add to queue
    ↓
Step 4: Continue until max_pages or queue empty
    ↓
Step 5: Combine all content & return

Result: Complete website content
Time: ~50+ seconds for 50 pages (1s delay each)
```

## 📊 Data Model Structure

```
Document
├── document_id: str (UUID)
│
├── source: Source
│   ├── type: "pdf" | "url" | "html" | "text"
│   ├── uri: str (path or URL)
│   ├── company: str
│   └── extracted_at: datetime
│
├── metadata: Metadata
│   ├── title: Optional[str]
│   ├── author: Optional[str]
│   ├── description: Optional[str]
│   ├── page_count: Optional[int]
│   ├── language: Optional[str]
│   └── extra: Dict[str, Any]
│
└── content: Content
    ├── raw_text: str (full text)
    │
    ├── chunks: List[ContentChunk]
    │   └── ContentChunk
    │       ├── chunk_id: str (UUID)
    │       ├── text: str
    │       ├── start_index: int
    │       ├── end_index: int
    │       └── metadata: Dict[str, Any]
    │
    └── structured: Optional[StructuredContent]
        ├── headings: List[Dict]
        │   └── {tag: "h1", text: "..."}
        ├── paragraphs: List[str]
        ├── lists: List[Dict]
        │   └── {type: "ul", items: [...]}
        ├── tables: List[Dict]
        │   └── {headers: [...], rows: [[...]]}
        └── links: List[Dict]
            └── {text: "...", href: "..."}
```

## 🔧 CLI Command Flow

### Extract Command

```
$ python main.py extract "https://example.com" "Example Corp" --crawl-mode summary

    ↓
[1] Parse arguments
    ├── source: "https://example.com"
    ├── company: "Example Corp"
    └── crawl_mode: "summary"
    ↓
[2] Detect source type
    └── Type: url
    ↓
[3] Get extractor from factory
    └── URLExtractor
    ↓
[4] Extract content (with progress spinner)
    ├── Fetch homepage
    ├── Find key pages
    ├── Extract from 2 pages
    └── Build Document
    ↓
[5] Save to storage
    └── data/outputs/example-corp/sources/{timestamp}_url_{id}.json
    ↓
[6] Display summary
    ├── Document ID
    ├── Title
    ├── Text length
    ├── Number of chunks
    └── Save path
```

### Batch Command

```
$ python main.py batch "Example Corp" file1.pdf https://example.com file2.html

    ↓
[1] Parse arguments
    ├── company: "Example Corp"
    └── sources: [file1.pdf, https://example.com, file2.html]
    ↓
[2] Loop through sources
    ├── Source 1: file1.pdf
    │   ├── Detect type: pdf
    │   ├── Extract with PDFExtractor
    │   └── Save
    │
    ├── Source 2: https://example.com
    │   ├── Detect type: url
    │   ├── Extract with URLExtractor
    │   └── Save
    │
    └── Source 3: file2.html
        ├── Detect type: html
        ├── Extract with HTMLExtractor
        └── Save
    ↓
[3] Display summary
    ├── Total sources: 3
    ├── Successful: 3
    └── Failed: 0
```

## 📂 Output File Structure

```
data/outputs/
│
├── example-corp/
│   ├── metadata.json
│   │   {
│   │     "company": "Example Corp",
│   │     "created": "2025-12-17T10:00:00",
│   │     "last_updated": "2025-12-17T12:30:00",
│   │     "total_sources": 5
│   │   }
│   │
│   ├── index.json
│   │   {
│   │     "sources": [
│   │       {
│   │         "document_id": "abc-123",
│   │         "type": "url",
│   │         "uri": "https://example.com",
│   │         "title": "Example Corp - Homepage",
│   │         "extracted_at": "2025-12-17T10:00:00",
│   │         "filepath": "sources/20251217_100000_url_abc123.json"
│   │       },
│   │       ...
│   │     ]
│   │   }
│   │
│   └── sources/
│       ├── 20251217_100000_url_abc123.json
│       ├── 20251217_100530_pdf_def456.json
│       └── 20251217_101000_html_ghi789.json
│
├── acme-corporation/
│   ├── metadata.json
│   ├── index.json
│   └── sources/
│       └── ...
│
└── techstart-inc/
    ├── metadata.json
    ├── index.json
    └── sources/
        └── ...
```

## 🎨 Terminal Output Examples

### Successful Extraction

```
B2B Data Fusion Engine
Company: Acme Corporation
Source: https://acme.com
Type: url
Crawl mode: summary

⠋ Extracting content...

✓ Extraction complete!

Document ID:      abc-123-def-456
Title:            Acme Corporation - Innovative Solutions
Raw text length:  15,234 characters
Chunks:           30
Headings:         12
Paragraphs:       45
Lists:            5
Tables:           2
Saved to:         data/outputs/acme-corporation/sources/20251217_120000_url_abc123.json
```

### Batch Processing

```
B2B Data Fusion Engine - Batch Processing
Company: Acme Corporation
Sources: 3

Processing 1/3: brochure.pdf
  Type: pdf
  ⠋ Extracting...
  ✓ Saved to 20251217_120000_pdf_abc123.json

Processing 2/3: https://acme.com
  Type: url
  ⠋ Extracting...
  ✓ Saved to 20251217_120530_url_def456.json

Processing 3/3: about.html
  Type: html
  ⠋ Extracting...
  ✓ Saved to 20251217_121000_html_ghi789.json

Batch processing complete!
Successful: 3/3
```

### Company Info

```
Company Information
Name:          Acme Corporation
Total sources: 5
Created:       2025-12-17 10:00:00
Last updated:  2025-12-17 12:30:00

Sources:

┌──────┬─────────────────────────┬──────────────────────┬─────────────────────┐
│ Type │ Title                   │ URI                  │ Extracted           │
├──────┼─────────────────────────┼──────────────────────┼─────────────────────┤
│ url  │ Acme Corp - Homepage    │ https://acme.com     │ 2025-12-17 10:00:00 │
│ pdf  │ Annual Report 2024      │ /path/to/report.pdf  │ 2025-12-17 10:05:00 │
│ html │ About Acme              │ /path/to/about.html  │ 2025-12-17 10:10:00 │
└──────┴─────────────────────────┴──────────────────────┴─────────────────────┘
```

## 🚀 Quick Start Workflow

```
Step 1: Install
├─ pip install -r requirements.txt

Step 2: Verify
├─ python verify_setup.py

Step 3: Create test data
├─ python create_test_data.py

Step 4: Test extraction
├─ python main.py extract test_data/acme_about.html "Acme Corp"

Step 5: View results
├─ python main.py list-companies
└─ python main.py info "Acme Corp"

Step 6: Use with real data
├─ python main.py extract "https://realcompany.com" "Real Company"
└─ python main.py batch "Real Company" doc1.pdf doc2.html
```

---

**You now have a complete visual guide to the data extraction pipeline!** 🎉
