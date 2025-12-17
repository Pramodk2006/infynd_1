# System Architecture - B2B Data Fusion Engine

## Complete Full-Stack Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE (React)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐    │
│  │  Dashboard  │  │   Company    │  │    New      │  │    Batch     │    │
│  │    Page     │  │    Detail    │  │ Extraction  │  │ Extraction   │    │
│  │             │  │     Page     │  │    Page     │  │    Page      │    │
│  └─────────────┘  └──────────────┘  └─────────────┘  └──────────────┘    │
│         │                │                  │                │              │
│         └────────────────┴──────────────────┴────────────────┘              │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │   React Router (v6)     │                             │
│                    └─────────────────────────┘                             │
│                                  │                                          │
│                                  ▼                                          │
│         ┌────────────────────────────────────────────────┐                 │
│         │         Reusable Components Layer              │                 │
│         ├────────────────────────────────────────────────┤                 │
│         │  • Navbar        • CompanyCard                 │                 │
│         │  • CompanyList   • ExtractionForm              │                 │
│         │  • SourceViewer                                │                 │
│         └────────────────────────────────────────────────┘                 │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │   API Service Layer     │                             │
│                    │   (Axios + Mock Data)   │                             │
│                    └─────────────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP/JSON (Port 3000 → 5000)
                                   │ CORS Enabled
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REST API LAYER (Flask)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GET  /api/companies              POST /api/extract                        │
│  GET  /api/companies/<name>       POST /api/batch                          │
│  GET  /api/sources/<id>           GET  /api/health                         │
│                                                                             │
│                    ┌─────────────────────────┐                             │
│                    │   Flask Application     │                             │
│                    │   + Flask-CORS          │                             │
│                    └─────────────────────────┘                             │
│                                  │                                          │
│                                  ▼                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXTRACTION PIPELINE (Python)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌─────────────────────────┐                             │
│                    │   ExtractorFactory      │                             │
│                    │  (Strategy Pattern)     │                             │
│                    └─────────────────────────┘                             │
│                              │                                              │
│                ┌─────────────┼─────────────┬───────────────┐              │
│                │             │             │               │              │
│                ▼             ▼             ▼               ▼              │
│      ┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐       │
│      │     PDF      │ │   HTML   │ │   URL    │ │     Text      │       │
│      │  Extractor   │ │Extractor │ │Extractor │ │  Extractor    │       │
│      │              │ │          │ │          │ │               │       │
│      │  (PyMuPDF)   │ │  (BS4)   │ │ (httpx)  │ │(Plain Text)   │       │
│      └──────────────┘ └──────────┘ └──────────┘ └───────────────┘       │
│                │             │             │               │              │
│                └─────────────┴─────────────┴───────────────┘              │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │   Pydantic Models       │                             │
│                    │   • Document            │                             │
│                    │   • Source              │                             │
│                    │   • Content             │                             │
│                    │   • Metadata            │                             │
│                    └─────────────────────────┘                             │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │  Text Processing Utils  │                             │
│                    │  • Chunking (512 chars) │                             │
│                    │  • Cleaning             │                             │
│                    │  • Sentence detection   │                             │
│                    └─────────────────────────┘                             │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │   DocumentStore         │                             │
│                    │  (Repository Pattern)   │                             │
│                    └─────────────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA STORAGE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        data/outputs/                                        │
│                             │                                               │
│              ┌──────────────┼──────────────┐                               │
│              │              │              │                               │
│              ▼              ▼              ▼                               │
│      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                     │
│      │   Company   │ │   Company   │ │   Company   │                     │
│      │      A      │ │      B      │ │      C      │                     │
│      ├─────────────┤ ├─────────────┤ ├─────────────┤                     │
│      │metadata.json│ │metadata.json│ │metadata.json│                     │
│      │ index.json  │ │ index.json  │ │ index.json  │                     │
│      │             │ │             │ │             │                     │
│      │  sources/   │ │  sources/   │ │  sources/   │                     │
│      │  ├─001.json │ │  ├─001.json │ │  ├─001.json │                     │
│      │  ├─002.json │ │  ├─002.json │ │  ├─002.json │                     │
│      │  └─003.json │ │  └─003.json │ │  └─003.json │                     │
│      └─────────────┘ └─────────────┘ └─────────────┘                     │
│                                                                             │
│  JSON Format (Vector DB Ready):                                           │
│  • document_id (UUID)                                                      │
│  • source (type, uri, company, timestamp)                                 │
│  • metadata (title, author, date, page_count)                             │
│  • content (raw_text, chunks, structured)                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLI INTERFACE (Typer)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Commands:                                                                 │
│  • python main.py extract <source> <company>                              │
│  • python main.py batch <company> <sources...>                            │
│  • python main.py list-companies                                          │
│  • python main.py info <company>                                          │
│  • python main.py version                                                 │
│                                                                             │
│                    ┌─────────────────────────┐                             │
│                    │   Rich Terminal UI      │                             │
│                    │   • Progress bars       │                             │
│                    │   • Colored output      │                             │
│                    │   • Tables              │                             │
│                    └─────────────────────────┘                             │
│                                  │                                          │
│                                  ▼                                          │
│               (Same Extraction Pipeline as API)                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### User Initiates Extraction (Frontend)

```
User
  │
  ▼ (Fills form)
ExtractionForm Component
  │
  ▼ (Submit)
API Service (Axios)
  │
  ▼ (POST /api/extract)
Flask API Server
  │
  ▼ (Validate)
ExtractorFactory.get_extractor()
  │
  ▼ (Route to appropriate extractor)
PDFExtractor / HTMLExtractor / URLExtractor / TextExtractor
  │
  ▼ (Extract & Parse)
Pydantic Document Model
  │
  ▼ (Validate)
Text Processing Utils
  │
  ▼ (Chunk & Clean)
DocumentStore.save()
  │
  ▼ (Write JSON)
data/outputs/{company}/sources/{timestamp}_{type}_{id}.json
  │
  ▼ (Response)
API Response (JSON)
  │
  ▼ (Display)
React UI (Success Message + Navigate to Company Detail)
```

### User Views Company (Frontend)

```
User
  │
  ▼ (Click company card)
CompanyDetail Page
  │
  ▼ (Load data)
API Service (Axios)
  │
  ▼ (GET /api/companies/<name>)
Flask API Server
  │
  ▼ (Read files)
data/outputs/{company}/
  ├─ metadata.json
  └─ index.json
  │
  ▼ (Parse JSON)
API Response (Company + Sources)
  │
  ▼ (Display)
CompanyDetail Component
  │
  ▼ (User selects source)
SourceViewer Component
  │
  ▼ (GET /api/sources/<id>)
Flask API Server
  │
  ▼ (Read file)
data/outputs/{company}/sources/{source}.json
  │
  ▼ (Parse JSON)
API Response (Full Document)
  │
  ▼ (Display)
JSON Viewer (react-json-view)
```

### CLI Extraction Flow

```
User
  │
  ▼ (python main.py extract ...)
Typer CLI
  │
  ▼ (Parse args)
extract() function
  │
  ▼ (Get extractor)
ExtractorFactory.get_extractor()
  │
  ▼ (Extract)
Extractor.extract()
  │
  ▼ (Process)
Text Processing
  │
  ▼ (Save)
DocumentStore.save()
  │
  ▼ (Write)
data/outputs/{company}/sources/{file}.json
  │
  ▼ (Display)
Rich Terminal Output (Success message + stats)
```

## Technology Stack Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
├─────────────────────────────────────────────────────────────────┤
│ React 18.2           │ UI Framework                             │
│ React Router 6.20    │ Client-side routing                      │
│ Axios 1.6.2          │ HTTP client                              │
│ Tailwind CSS 3.3.6   │ Styling                                  │
│ Lucide React 0.294   │ Icons                                    │
│ date-fns 3.0         │ Date formatting                          │
│ react-json-view 1.21 │ JSON viewer                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND API                             │
├─────────────────────────────────────────────────────────────────┤
│ Flask 3.0            │ Web framework                            │
│ Flask-CORS 4.0       │ CORS support                             │
│ Requests 2.31        │ HTTP client (for testing)                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTION PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│ httpx 0.27           │ Async HTTP client                        │
│ BeautifulSoup4 4.12  │ HTML parsing                             │
│ lxml 5.1             │ XML/HTML parser                          │
│ PyMuPDF 1.24         │ PDF extraction                           │
│ Pydantic 2.5         │ Data validation                          │
│ Typer 0.12           │ CLI framework                            │
│ Rich 13.7            │ Terminal UI                              │
│ filetype 1.2         │ MIME type detection                      │
│ python-dateutil 2.8  │ Date parsing                             │
│ tenacity 8.2         │ Retry logic                              │
└─────────────────────────────────────────────────────────────────┘
```

## Design Patterns Used

### 1. Strategy Pattern

```python
# Extractor interface
class ExtractorStrategy(ABC):
    @abstractmethod
    def can_handle(self, source: str) -> bool: ...

    @abstractmethod
    def extract(self, source: str, ...) -> Document: ...

# Concrete strategies
class PDFExtractor(ExtractorStrategy): ...
class HTMLExtractor(ExtractorStrategy): ...
class URLExtractor(ExtractorStrategy): ...
class TextExtractor(ExtractorStrategy): ...
```

### 2. Factory Pattern

```python
class ExtractorFactory:
    def get_extractor(self, source: str) -> ExtractorStrategy:
        # Auto-detect and return appropriate extractor
        for extractor in [PDFExtractor(), HTMLExtractor(), ...]:
            if extractor.can_handle(source):
                return extractor
```

### 3. Repository Pattern

```python
class DocumentStore:
    def save(self, document: Document, company: str) -> Path: ...
    def load(self, filepath: Path) -> Document: ...
    def list_sources(self, company: str) -> List[Dict]: ...
```

### 4. Component-Based Architecture (React)

```jsx
// Container components
<Dashboard>
  <CompanyList>
    <CompanyCard />
    <CompanyCard />
  </CompanyList>
</Dashboard>

// Presentational components
<ExtractionForm />
<SourceViewer />
```

## Key Features by Layer

### Frontend Layer

- ✅ Single Page Application (SPA)
- ✅ Client-side routing
- ✅ Responsive design
- ✅ Form validation
- ✅ Loading states
- ✅ Error handling
- ✅ Mock data support

### API Layer

- ✅ RESTful endpoints
- ✅ JSON responses
- ✅ CORS enabled
- ✅ Error handling
- ✅ Health checks
- ✅ Request validation

### Business Logic Layer

- ✅ Multi-format support
- ✅ Auto-detection
- ✅ Parallel processing
- ✅ Retry logic
- ✅ Text chunking
- ✅ Structure extraction
- ✅ Robots.txt compliance

### Storage Layer

- ✅ JSON format
- ✅ Company organization
- ✅ Timestamped sources
- ✅ Metadata tracking
- ✅ Index files
- ✅ Vector DB ready

## Deployment Considerations

### Development

- Frontend: npm start (port 3000)
- Backend: python api_server.py (port 5000)
- Hot reload enabled for frontend
- Debug mode for Flask

### Production (Future)

- Frontend: npm build → static files
- Backend: Gunicorn + Nginx
- Environment variables for config
- Database instead of JSON files
- CDN for static assets
- SSL/TLS encryption
- Load balancing
- Caching layer

## Security Considerations

### Current Implementation

- CORS enabled (development mode)
- No authentication (local use)
- File path validation
- JSON response sanitization

### Future Enhancements

- JWT authentication
- Rate limiting
- Input sanitization
- XSS protection
- CSRF tokens
- API key management
- Role-based access control

## Performance Optimization

### Current

- Pre-chunked content
- Lazy loading (React)
- Efficient JSON storage
- Minimal dependencies

### Future

- Redis caching
- Database indexing
- CDN integration
- Image optimization
- Code splitting
- Service workers
- Background jobs (Celery)

---

This architecture supports the current Stage 1 implementation and is designed to scale for future stages (LLM integration, vector database, advanced analytics).
