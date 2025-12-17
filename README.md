# B2B Data Fusion Engine

Multi-source data extraction pipeline with React frontend for building unified company profiles from websites, PDFs, HTML files, and text documents.

## 🎯 Project Overview

This is **Stage 1** of the B2B Data Fusion Engine - a multi-stage system for:

1. ✅ **Stage 1 (Current)**: Multi-format data extraction and storage + **React Frontend UI**
2. 🔄 **Stage 2**: LLM-powered summarization with Ollama
3. 🔄 **Stage 3**: Vector database integration
4. 🔄 **Stage 4**: Profile fusion and advanced analytics

## ✨ Features

### Backend (Python)

- **Multi-format Support**: URLs, PDFs, HTML files, plain text
- **Smart Web Crawling**: Full site or summary mode (2 pages)
- **Structured Extraction**: Headings, paragraphs, lists, tables, links
- **Vector DB Ready**: Pre-chunked JSON with metadata
- **Domain Filtering**: Stays within same domain when crawling
- **Robots.txt Compliance**: Respects site crawling rules
- **Batch Processing**: Extract from multiple sources at once
- **Beautiful CLI**: Rich terminal output with progress indicators
- **REST API**: Flask server with CORS support

### Frontend (React)

- **Modern UI**: Built with React 18 and Tailwind CSS
- **Company Dashboard**: View all companies and their sources
- **Interactive Extraction**: Easy-to-use forms for single and batch extraction
- **Source Viewer**: Browse and download extracted JSON documents
- **Real-time Stats**: Track total companies, sources, and extraction types
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start (Full Stack)

### Option 1: Automated Startup (Recommended)

**Windows:**

```bash
start.bat
```

**macOS/Linux:**

```bash
chmod +x start.sh
./start.sh
```

This will:

1. Start the Flask API server on port 5000
2. Start the React frontend on port 3000
3. Open your browser automatically

### Option 2: Manual Startup

See [FULL_SETUP.md](FULL_SETUP.md) for detailed step-by-step instructions.

## 📦 Installation

### 1. Backend Setup

```bash
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 3. Verify Setup

```bash
python verify_setup.py
```

## 🖥️ Running the Application

### Full Stack (Backend + Frontend)

**Windows:**

```bash
start.bat
```

**macOS/Linux:**

```bash
chmod +x start.sh
./start.sh
```

Then open [http://localhost:3000](http://localhost:3000) in your browser!

### CLI Only (Without Frontend)

#### 1. Create Test Data

```bash
python create_test_data.py
```

#### 2. Run Your First Extraction

```bash
# Extract from HTML file
python main.py extract test_data/acme_about.html "Acme Corporation"

# Extract from text file
python main.py extract test_data/acme_overview.txt "Acme Corporation"

# Batch processing both files
python main.py batch "Acme Corporation" test_data/acme_about.html test_data/acme_overview.txt
```

#### 3. View Results

```bash
# List all companies
python main.py list-companies

# View company details
python main.py info "Acme Corporation"
```

## 📖 Usage

### Extract from Single Source

```bash
# Website (summary mode - homepage + 1 key page)
python main.py extract "https://example.com" "Example Corp" --crawl-mode summary

# Website (full crawl - entire site, up to 50 pages)
python main.py extract "https://example.com" "Example Corp" --crawl-mode full --max-pages 50

# PDF document
python main.py extract "./company-brochure.pdf" "Example Corp"

# HTML file
python main.py extract "./about.html" "Example Corp"

# Text file
python main.py extract "./company-info.txt" "Example Corp"
```

### Batch Processing

```bash
# Process multiple sources for one company
python main.py batch "Example Corp" brochure.pdf https://example.com about.html info.txt
```

### Management Commands

```bash
# List all companies in data store
python main.py list-companies

# Show company information
python main.py info "Example Corp"

# Show version
python main.py version

# Get help
python main.py --help
```

## Output Structure

```
data/outputs/
└── example-corp/
    ├── metadata.json
    ├── index.json
    └── sources/
        ├── 2025-12-17_website_abc123.json
        └── 2025-12-17_brochure_def456.json
```

## 📁 Project Structure

```
infynd-hackathon-project/
├── main.py                    # CLI entry point
├── requirements.txt           # Dependencies
├── verify_setup.py           # Setup verification
├── create_test_data.py       # Test data generator
│
├── src/pipeline/
│   ├── models/               # Pydantic data models
│   │   └── document.py       # Document, Source, Content schemas
│   │
│   ├── extractors/           # Content extractors
│   │   ├── base.py          # Abstract base class
│   │   ├── factory.py       # Auto-detection & routing
│   │   ├── pdf_extractor.py # PDF extraction (PyMuPDF)
│   │   ├── html_extractor.py# HTML parsing (BeautifulSoup4)
│   │   ├── url_extractor.py # Web crawling (httpx)
│   │   └── text_extractor.py# Plain text handling
│   │
│   ├── storage/              # Data persistence
│   │   └── document_store.py# JSON file management
│   │
│   └── utils/                # Helper functions
│       ├── text_processing.py# Text cleaning & chunking
│       └── url_utils.py      # URL validation & robots.txt
│
└── data/outputs/             # Extracted documents (JSON)
    └── {company-name}/
        ├── metadata.json
        ├── index.json
        └── sources/
```

## 🏗️ Architecture

- **Design Pattern**: Strategy Pattern for extractors
- **Data Models**: Pydantic for type-safe validation
- **Storage**: JSON files organized by company
- **CLI**: Typer with Rich for beautiful output
- **Extensible**: Easy to add new extractors or storage backends

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

## 📊 Output Format

Each extraction creates a JSON document with:

```json
{
  "document_id": "unique-uuid",
  "source": {
    "type": "pdf|url|html|text",
    "uri": "source-path-or-url",
    "company": "Company Name",
    "extracted_at": "2025-12-17T10:30:00"
  },
  "metadata": {
    "title": "Document Title",
    "description": "Meta description",
    "page_count": 10
  },
  "content": {
    "raw_text": "Full extracted text...",
    "chunks": [
      {
        "chunk_id": "uuid",
        "text": "Pre-chunked content for vector DB...",
        "start_index": 0,
        "end_index": 512
      }
    ],
    "structured": {
      "headings": [{ "tag": "h1", "text": "..." }],
      "paragraphs": ["..."],
      "lists": [{ "type": "ul", "items": ["..."] }],
      "tables": [{ "headers": [], "rows": [] }]
    }
  }
}
```

## ⚙️ Configuration Options

### Command Line Options

```bash
--crawl-mode, -m    # summary or full (default: summary)
--max-pages, -p     # Max pages in full crawl (default: 50)
--chunk-size, -c    # Chunk size for vector DB (default: 512)
--output, -o        # Output directory (default: data/outputs)
```

## 🔧 Technologies

| Component     | Technology            | Purpose                         |
| ------------- | --------------------- | ------------------------------- |
| HTTP Client   | httpx                 | Web requests with async support |
| HTML Parser   | BeautifulSoup4 + lxml | HTML parsing                    |
| PDF Extractor | PyMuPDF (fitz)        | PDF text extraction             |
| Data Models   | Pydantic              | Type-safe validation            |
| CLI           | Typer                 | Command-line interface          |
| Terminal UI   | Rich                  | Beautiful formatted output      |

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide with examples
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed technical architecture
- **[requirements.txt](requirements.txt)** - Python dependencies

## 🎯 Next Steps (Future Stages)

### Stage 2: LLM Integration

- Ollama client for local LLM
- Summarization prompt engineering
- Generate unified company profiles

### Stage 3: Vector Database

- Integration with Pinecone/Weaviate/Chroma
- Embedding generation
- Semantic search

### Stage 4: Web Dashboard

- React-based UI
- Company search & management
- Profile visualization & editing

## 🤝 Contributing

This is a hackathon project. Key areas for improvement:

- Add unit tests
- Implement async web crawling
- Add more extractors (DOCX, PPTX, etc.)
- Improve error handling
- Add logging

## 📝 License

MIT License - feel free to use for your projects!
#   i n f y n d _ 1  
 