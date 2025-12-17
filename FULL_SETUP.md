# B2B Data Fusion Engine - Complete Setup Guide

This guide walks you through setting up both the Python backend and React frontend.

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 16 or higher
- **npm**: Comes with Node.js
- **Git**: For cloning the repository (optional)

## 🚀 Quick Start (5 Minutes)

### Step 1: Set Up Python Backend

1. **Create and activate virtual environment:**

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

3. **Verify setup:**

```bash
python verify_setup.py
```

You should see: ✅ All dependencies installed correctly

### Step 2: Set Up React Frontend

1. **Navigate to frontend directory:**

```bash
cd frontend
```

2. **Install Node.js dependencies:**

```bash
npm install
```

This will install React, React Router, Axios, Tailwind CSS, and other dependencies.

3. **Return to project root:**

```bash
cd ..
```

### Step 3: Start the Application

You'll need **two terminal windows**:

**Terminal 1 - Backend API Server:**

```bash
# Make sure virtual environment is activated
python api_server.py
```

You should see:

```
🚀 B2B Data Fusion Engine API Server
📡 Server running at: http://localhost:5000
```

**Terminal 2 - Frontend Development Server:**

```bash
cd frontend
npm start
```

The React app will automatically open at [http://localhost:3000](http://localhost:3000)

## ✨ Using the Application

### Dashboard (Home Page)

- View all companies and their extraction statistics
- Search and filter companies
- Quick overview of total companies, sources, and source types

### New Extraction

1. Click **"New Extraction"** in the navigation
2. Enter company name
3. Choose source type (URL, PDF, HTML, or Text file)
4. Enter source (URL or file path)
5. For URLs: Select crawl mode (Summary or Full)
6. Click **"Start Extraction"**

### Batch Extraction

1. Click **"Batch Extract"** in the navigation
2. Enter company name
3. Add multiple sources using the **"Add Source"** button
4. Mix different source types (URL + PDF + HTML + text)
5. Click **"Start Batch Extraction"**

### View Company Details

1. Click on any company card in the dashboard
2. Browse all sources for that company
3. Click a source to view extracted data
4. View/download JSON documents

## 🧪 Test the System

### 1. Create Test Data

```bash
python create_test_data.py
python create_test_pdf.py
```

### 2. Test via CLI (Optional)

```bash
# Single extraction
python main.py extract test_data/acme_about.html "Acme Corporation"

# Batch extraction
python main.py batch "Test Company" test_data/*.html test_data/*.txt
```

### 3. Test via Frontend

1. Start both servers (backend + frontend)
2. Navigate to [http://localhost:3000](http://localhost:3000)
3. Try the "New Extraction" feature
4. View results in the dashboard

## 📁 Project Structure

```
infynd-hackathon-project/
├── frontend/                    # React application
│   ├── public/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API service layer
│   │   ├── App.jsx              # Main app with routing
│   │   └── index.js             # Entry point
│   ├── package.json
│   └── README.md
│
├── src/pipeline/                # Python extraction pipeline
│   ├── models/                  # Pydantic data models
│   ├── extractors/              # Source extractors
│   ├── storage/                 # Document storage
│   └── utils/                   # Utility functions
│
├── data/outputs/                # Extracted company data
│   └── {company-name}/
│       ├── metadata.json
│       ├── index.json
│       └── sources/
│
├── main.py                      # CLI interface
├── api_server.py                # Flask API server
├── requirements.txt             # Python dependencies
└── README.md                    # Main documentation
```

## 🔧 Configuration

### Backend (.env not needed for basic usage)

The backend works out of the box with default settings.

### Frontend (.env)

Already configured in `frontend/.env`:

```
REACT_APP_API_URL=http://localhost:5000/api
```

## 📡 API Endpoints

The Flask server exposes these endpoints:

| Method | Endpoint                | Description         |
| ------ | ----------------------- | ------------------- |
| GET    | `/api/companies`        | List all companies  |
| GET    | `/api/companies/<name>` | Get company details |
| GET    | `/api/sources/<id>`     | Get source document |
| POST   | `/api/extract`          | Single extraction   |
| POST   | `/api/batch`            | Batch extraction    |
| GET    | `/api/health`           | Health check        |

## 🐛 Troubleshooting

### Python Issues

**"Module not found" error:**

```bash
pip install -r requirements.txt
```

**"Command not found: python":**

```bash
# Try python3 instead
python3 -m venv venv
python3 api_server.py
```

**Port 5000 already in use:**

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

### Frontend Issues

**"npm: command not found":**

- Install Node.js from [nodejs.org](https://nodejs.org)

**Dependencies fail to install:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Port 3000 already in use:**

```bash
# It will automatically prompt to use port 3001
# Or set manually:
PORT=3001 npm start
```

**Blank page / "Cannot GET /":**

- Make sure you're in the `frontend/` directory when running `npm start`
- Clear browser cache and reload

### CORS Errors

If you see CORS errors in the browser console:

1. Ensure Flask server is running with `flask-cors` installed
2. Check that frontend `.env` has correct API URL
3. Restart both servers

## 🎯 Next Steps

### Stage 2: Vector Database Integration

- Set up Qdrant or Weaviate
- Add embeddings generation
- Implement semantic search

### Stage 3: LLM Summarization (Ollama)

- Install Ollama locally
- Add summarization endpoints
- Create summary UI

### Stage 4: Enhanced Dashboard

- Real-time extraction progress
- Advanced filtering and sorting
- Export capabilities
- Analytics and visualizations

## 📚 Additional Documentation

- [Frontend Setup](frontend/SETUP.md) - Detailed frontend guide
- [Architecture](ARCHITECTURE.md) - System architecture overview
- [CLI Guide](QUICKSTART.md) - Command-line interface guide
- [Test Results](TEST_RESULTS.md) - Testing documentation

## 💡 Tips

1. **Development Workflow:**

   - Keep both servers running during development
   - Frontend hot-reloads automatically on changes
   - Backend requires restart after code changes

2. **Data Organization:**

   - Each company gets its own folder
   - Sources are timestamped and numbered
   - JSON format is optimized for vector databases

3. **Performance:**

   - Summary mode: ~2-5 seconds per URL
   - Full crawl: Depends on website size
   - PDF extraction: ~1-2 seconds per file
   - HTML/Text: Near-instant

4. **Best Practices:**
   - Use meaningful company names
   - Start with summary mode for unknown websites
   - Batch process multiple sources from same company
   - Check `data/outputs/` for saved extractions

## 🤝 Support

For issues or questions:

1. Check this setup guide
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify both servers are running
5. Check browser console for frontend errors
6. Check terminal output for backend errors

## 🎉 Success Indicators

You know everything is working when:

- ✅ `python verify_setup.py` shows all green checkmarks
- ✅ Backend server shows API endpoints at startup
- ✅ Frontend opens automatically at localhost:3000
- ✅ No errors in browser console
- ✅ Can navigate between pages
- ✅ Dashboard shows "Total Companies" stats
- ✅ Extraction forms load correctly

Happy data extraction! 🚀
