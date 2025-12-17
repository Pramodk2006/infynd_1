# Quick Reference Guide

## 🚀 Starting the Application

### Fastest Way

```bash
# Windows
start.bat

# macOS/Linux
./start.sh
```

### Manual Start

```bash
# Terminal 1 - Backend
python api_server.py

# Terminal 2 - Frontend
cd frontend && npm start
```

## 📡 API Endpoints

| Endpoint                | Method | Description    | Example                                                       |
| ----------------------- | ------ | -------------- | ------------------------------------------------------------- |
| `/api/health`           | GET    | Health check   | `curl http://localhost:5000/api/health`                       |
| `/api/companies`        | GET    | List companies | `curl http://localhost:5000/api/companies`                    |
| `/api/companies/<name>` | GET    | Company detail | `curl http://localhost:5000/api/companies/Acme%20Corporation` |
| `/api/sources/<id>`     | GET    | Get document   | `curl http://localhost:5000/api/sources/<doc-id>`             |
| `/api/extract`          | POST   | Single extract | See below                                                     |
| `/api/batch`            | POST   | Batch extract  | See below                                                     |

### POST /api/extract Example

```bash
curl -X POST http://localhost:5000/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Test Company",
    "source": "https://example.com",
    "crawlMode": "summary"
  }'
```

### POST /api/batch Example

```bash
curl -X POST http://localhost:5000/api/batch \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Test Company",
    "sources": [
      {"type": "url", "value": "https://example.com"},
      {"type": "html", "value": "./test.html"}
    ],
    "crawlMode": "summary"
  }'
```

## 🖥️ CLI Commands

### Basic Operations

```bash
# Extract from URL
python main.py extract "https://example.com" "Company Name"

# Extract from PDF
python main.py extract "./docs/brochure.pdf" "Company Name"

# Extract from HTML
python main.py extract "./data/about.html" "Company Name"

# Extract from text file
python main.py extract "./data/overview.txt" "Company Name"
```

### Batch Processing

```bash
# Multiple files for one company
python main.py batch "Company Name" file1.html file2.pdf "https://example.com"
```

### View Data

```bash
# List all companies
python main.py list-companies

# View company details
python main.py info "Company Name"

# Show version
python main.py version
```

### URL Crawl Modes

```bash
# Summary mode (2 pages) - Default
python main.py extract "https://example.com" "Company" --crawl-mode summary

# Full crawl (up to max-pages)
python main.py extract "https://example.com" "Company" --crawl-mode full --max-pages 50
```

## 📂 File Structure

### Output Structure

```
data/outputs/
└── {company-name}/
    ├── metadata.json          # Company metadata
    ├── index.json             # Source index
    └── sources/
        ├── 20240101_120000_url_001.json
        ├── 20240101_120030_pdf_002.json
        └── ...
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/           # Reusable components
│   ├── pages/                # Page components
│   ├── services/             # API services
│   └── App.jsx               # Main app
├── public/
└── package.json
```

### Backend Structure

```
src/pipeline/
├── models/                   # Pydantic models
├── extractors/               # Source extractors
├── storage/                  # Document storage
└── utils/                    # Utilities
```

## 🧪 Testing

### Test Backend

```bash
# Verify setup
python verify_setup.py

# Create test data
python create_test_data.py
python create_test_pdf.py

# Test extraction
python main.py extract test_data/acme_about.html "Test Company"
```

### Test API Server

```bash
# Start server first
python api_server.py

# In another terminal, run tests
python test_api.py
```

### Test Frontend

```bash
cd frontend
npm start

# Opens http://localhost:3000
```

## 🔧 Troubleshooting

### Backend Issues

**Module not found:**

```bash
pip install -r requirements.txt
```

**Port 5000 in use:**

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

**PyMuPDF import error:**

```bash
python -m pip install --upgrade PyMuPDF
```

### Frontend Issues

**Port 3000 in use:**

```bash
# Will auto-prompt to use 3001
# Or set manually:
PORT=3001 npm start
```

**Dependencies missing:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**

- Ensure Flask server is running
- Check flask-cors is installed
- Verify .env has correct API_URL

## 📊 Data Format

### Document JSON Structure

```json
{
  "document_id": "uuid",
  "source": {
    "source_type": "pdf|html|url|text",
    "uri": "path or url",
    "company_name": "Company Name",
    "extracted_at": "2024-01-01T12:00:00"
  },
  "metadata": {
    "title": "Document Title",
    "author": "Author",
    "creation_date": "2024-01-01",
    "page_count": 10
  },
  "content": {
    "raw_text": "Full text...",
    "chunks": [
      {
        "chunk_id": "001",
        "text": "Chunk text...",
        "start_pos": 0,
        "end_pos": 512
      }
    ],
    "structured": {
      "headings": [...],
      "paragraphs": [...],
      "lists": [...],
      "tables": [...]
    }
  }
}
```

## 🎯 Common Tasks

### Add a New Company

**Via Frontend:**

1. Go to "New Extraction"
2. Enter company name
3. Choose source type
4. Enter source path/URL
5. Click "Start Extraction"

**Via CLI:**

```bash
python main.py extract "source" "Company Name"
```

### View Existing Data

**Via Frontend:**

1. Go to Dashboard
2. Click on company card
3. Browse sources
4. View JSON documents

**Via CLI:**

```bash
python main.py info "Company Name"
```

### Batch Process Multiple Sources

**Via Frontend:**

1. Go to "Batch Extract"
2. Enter company name
3. Add sources with "+ Add Source"
4. Click "Start Batch Extraction"

**Via CLI:**

```bash
python main.py batch "Company" file1.pdf file2.html "https://url"
```

## 🌐 URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **API Health:** http://localhost:5000/api/health
- **API Companies:** http://localhost:5000/api/companies

## 📖 Documentation

- [README.md](README.md) - Main documentation
- [FULL_SETUP.md](FULL_SETUP.md) - Complete setup guide
- [FRONTEND_COMPLETE.md](FRONTEND_COMPLETE.md) - Frontend overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [QUICKSTART.md](QUICKSTART.md) - CLI quick start
- [frontend/SETUP.md](frontend/SETUP.md) - Frontend setup
- [frontend/README.md](frontend/README.md) - Frontend features

## 💡 Tips

1. **Always activate venv first:**

   ```bash
   # Windows: venv\Scripts\activate
   # Unix: source venv/bin/activate
   ```

2. **Check logs for errors:**

   - Backend: Terminal running api_server.py
   - Frontend: Terminal running npm start
   - Browser: Developer Console (F12)

3. **Data location:**

   - All extractions: `data/outputs/`
   - Test data: `test_data/`

4. **Restart after changes:**

   - Backend: Restart api_server.py
   - Frontend: Auto-reloads (no restart needed)

5. **Use summary mode first:**
   - Faster extraction
   - Good for testing
   - Can always do full crawl later

## 🚨 Common Errors

| Error                    | Solution                                       |
| ------------------------ | ---------------------------------------------- |
| `ModuleNotFoundError`    | `pip install -r requirements.txt`              |
| `Port already in use`    | Kill process on port or use different port     |
| `CORS error`             | Ensure flask-cors installed and server running |
| `Cannot connect to API`  | Start api_server.py first                      |
| `npm: command not found` | Install Node.js from nodejs.org                |
| `React page blank`       | Check browser console, ensure in frontend/ dir |

## 📞 Getting Help

1. Check error messages in terminal
2. Look at browser console (F12)
3. Review relevant documentation
4. Verify all dependencies installed
5. Ensure both servers are running
6. Check file paths are correct

## ✅ Success Checklist

- [ ] Virtual environment activated
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Node.js dependencies installed (`cd frontend && npm install`)
- [ ] Verify setup passes (`python verify_setup.py`)
- [ ] Backend server starts (`python api_server.py`)
- [ ] Frontend starts (`npm start` in frontend/)
- [ ] Can access http://localhost:3000
- [ ] Dashboard loads successfully
- [ ] Can create new extraction
- [ ] API health check works (`python test_api.py`)

---

**Need more help?** Check [FULL_SETUP.md](FULL_SETUP.md) for detailed step-by-step instructions.
