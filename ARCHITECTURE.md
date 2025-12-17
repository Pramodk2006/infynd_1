# Project Architecture

## Overview

The B2B Data Fusion Engine is a modular Python pipeline for extracting company data from multiple sources and preparing it for vector database ingestion.

## Project Structure

```
infynd-hackathon-project/
│
├── main.py                      # CLI entry point
├── requirements.txt             # Python dependencies
├── README.md                    # Project overview
├── QUICKSTART.md               # Quick start guide
├── create_test_data.py         # Test data generator
│
├── src/
│   └── pipeline/
│       ├── __init__.py
│       │
│       ├── models/              # Data models
│       │   ├── __init__.py
│       │   └── document.py      # Pydantic models for documents
│       │
│       ├── extractors/          # Content extractors
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract base class
│       │   ├── factory.py       # Extractor routing
│       │   ├── pdf_extractor.py # PDF extraction
│       │   ├── html_extractor.py# HTML file extraction
│       │   ├── url_extractor.py # Web crawling
│       │   └── text_extractor.py# Plain text extraction
│       │
│       ├── storage/             # Data persistence
│       │   ├── __init__.py
│       │   └── document_store.py# JSON storage manager
│       │
│       └── utils/               # Helper utilities
│           ├── __init__.py
│           ├── text_processing.py # Text cleaning/chunking
│           └── url_utils.py      # URL validation/robots.txt
│
└── data/
    └── outputs/                 # Extracted documents
        └── {company-name}/
            ├── metadata.json
            ├── index.json
            └── sources/
                └── {timestamp}_{type}_{id}.json
```

## Architecture Components

### 1. Data Models (`models/`)

**Pydantic-based schemas** for type-safe data structures:

- `Document`: Main container for extracted content
- `Source`: Source metadata (type, URI, company, timestamp)
- `Metadata`: Document metadata (title, author, description, etc.)
- `Content`: Text content with chunks
- `ContentChunk`: Pre-chunked text for vector DB
- `StructuredContent`: Structured HTML data (headings, lists, tables)

**Design Pattern**: Value Objects with validation

### 2. Extractors (`extractors/`)

**Strategy Pattern** for handling different input types:

- `ExtractorStrategy` (ABC): Interface for all extractors
- `PDFExtractor`: PyMuPDF-based PDF text extraction
- `HTMLExtractor`: BeautifulSoup4 HTML parsing
- `URLExtractor`: Web crawling with httpx + BeautifulSoup4
- `TextExtractor`: Plain text file handling
- `ExtractorFactory`: Auto-detection and routing

**Key Features**:

- Automatic source type detection
- Uniform interface across all extractors
- Extensible for new formats

### 3. Storage (`storage/`)

**Repository Pattern** for document persistence:

- `DocumentStore`: Manages JSON file storage
  - Organizes by company
  - Maintains indices
  - Tracks metadata

**Storage Schema**:

```
company-name/
├── metadata.json    # Company-level info
├── index.json       # Source registry
└── sources/         # Individual extractions
```

### 4. Utilities (`utils/`)

**Helper modules**:

- `text_processing.py`: Text cleaning, chunking, sentence splitting
- `url_utils.py`: URL validation, normalization, robots.txt checking

### 5. CLI (`main.py`)

**Typer-based command-line interface**:

Commands:

- `extract`: Single source extraction
- `batch`: Multiple sources for one company
- `list-companies`: List all companies
- `info`: Show company details
- `version`: Version info

**Features**:

- Rich terminal output
- Progress indicators
- Error handling
- Type-safe arguments

## Data Flow

```
Input (URL/PDF/HTML/Text)
    ↓
ExtractorFactory (auto-detect type)
    ↓
Appropriate Extractor (extract content)
    ↓
Document Model (structured data)
    ↓
DocumentStore (save to disk)
    ↓
JSON Output (vector DB ready)
```

## Key Design Decisions

### 1. **Strategy Pattern for Extractors**

- **Why**: Different sources require different extraction logic
- **Benefit**: Easy to add new source types without modifying existing code

### 2. **Pydantic for Data Models**

- **Why**: Type safety, validation, serialization
- **Benefit**: Prevents data corruption, auto-generates schemas

### 3. **JSON Storage**

- **Why**: Human-readable, easily parsed, vector DB compatible
- **Benefit**: Can inspect outputs, easy debugging, portable

### 4. **Pre-chunking Content**

- **Why**: Vector DBs need fixed-size chunks
- **Benefit**: Ready for immediate ingestion, no post-processing

### 5. **Structured + Raw Content**

- **Why**: Preserve both structure and searchable text
- **Benefit**: Flexible for different use cases (search vs analysis)

## Crawl Modes

### Summary Mode (Default)

- Fetches **main page + 1 key page** (about/products)
- Fast extraction for quick overviews
- ~2 pages total
- Use case: Quick company profiles

### Full Mode

- Crawls **entire website** (up to max_pages)
- Respects robots.txt
- Stays within same domain
- Use case: Comprehensive data collection

## Output Format

### Vector DB Ready JSON

Each document contains:

1. **Metadata**: Source tracking, company info
2. **Raw Text**: Full content as single string
3. **Chunks**: Pre-split content with positions
4. **Structured**: Parsed elements (headings, tables, etc.)

### Chunk Structure

```json
{
  "chunk_id": "unique-id",
  "text": "chunk content...",
  "start_index": 0,
  "end_index": 512,
  "metadata": { "section": "introduction" }
}
```

**Chunking Strategy**:

- Default size: 512 characters
- Overlap: 50 characters
- Break on sentence boundaries
- Preserves context

## Technologies Used

| Component           | Technology              | Purpose                     |
| ------------------- | ----------------------- | --------------------------- |
| HTTP Client         | `httpx`                 | Web requests, async support |
| HTML Parser         | `BeautifulSoup4 + lxml` | HTML parsing                |
| PDF Extraction      | `PyMuPDF (fitz)`        | PDF text extraction         |
| Data Validation     | `Pydantic`              | Type-safe models            |
| CLI Framework       | `Typer`                 | Command-line interface      |
| Terminal UI         | `Rich`                  | Beautiful output            |
| File Type Detection | `filetype`              | MIME type detection         |

## Extensibility Points

### Adding New Extractors

1. Create new class inheriting `ExtractorStrategy`
2. Implement `can_handle()` and `extract()` methods
3. Add to `ExtractorFactory._extractors`

Example:

```python
class DocxExtractor(ExtractorStrategy):
    def can_handle(self, source: str) -> bool:
        return source.endswith('.docx')

    def extract(self, source: str, company: str, **kwargs):
        # Extraction logic
        pass
```

### Adding New Storage Backends

1. Create new class implementing storage interface
2. Replace `DocumentStore` in main.py
3. Maintain same API (save, load, list)

### Adding New CLI Commands

1. Add `@app.command()` decorated function in main.py
2. Use Typer annotations for arguments
3. Follow existing patterns

## Next Steps (Stage 2+)

### 1. LLM Integration (Ollama)

- Add `llm_client.py` for Ollama API calls
- Implement summarization prompt engineering
- Generate unified company profiles

### 2. Vector Database Integration

- Add connectors for Pinecone/Weaviate/Chroma
- Implement embedding generation
- Batch upload functionality

### 3. React Dashboard

- Company search interface
- Source management
- Summary visualization
- Profile editor

### 4. Data Fusion Logic

- Deduplication across sources
- Confidence scoring
- Entity resolution
- Profile merging

## Testing

### Manual Testing

1. **Create test data**:

   ```bash
   python create_test_data.py
   ```

2. **Run extractions**:

   ```bash
   python main.py extract test_data/acme_about.html "Acme Corporation"
   ```

3. **Verify outputs**:
   ```bash
   python main.py list-companies
   python main.py info "Acme Corporation"
   ```

### Future Automated Testing

- Unit tests for each extractor
- Integration tests for full pipeline
- Mock HTTP responses for URL extractor
- Fixtures for PDF/HTML parsing

## Performance Considerations

### Current Implementation

- Synchronous processing (simple, reliable)
- Polite crawling (1 second delay)
- In-memory processing (limited by RAM)

### Future Optimizations

- Async crawling with `httpx.AsyncClient`
- Parallel processing with `multiprocessing`
- Streaming for large PDFs
- Caching for repeated URLs

## Security Considerations

1. **Input Validation**: Pydantic validates all inputs
2. **File Path Safety**: Uses Path objects to prevent traversal
3. **URL Safety**: Validates URLs before fetching
4. **Robots.txt**: Respects site crawling rules
5. **Timeout**: All HTTP requests have timeouts

## Error Handling

- Network errors: Logged and skipped
- Parsing errors: Returned as None
- File errors: Caught with descriptive messages
- Batch processing: Continues on individual failures

## Logging

Currently: Print statements for debugging
Future: Add proper logging with `logging` module

## Configuration

Currently: CLI arguments
Future: Add config file support (YAML/TOML)
