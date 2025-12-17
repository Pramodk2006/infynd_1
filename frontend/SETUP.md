# Frontend Setup Guide

## Prerequisites

- Node.js 16+ and npm installed
- Python backend running (see main README.md)

## Installation

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Configure environment variables:
   The `.env` file is already created with default settings:

```
REACT_APP_API_URL=http://localhost:5000/api
```

## Running the Application

### Development Mode

```bash
npm start
```

This runs the app at [http://localhost:3000](http://localhost:3000).

The page will reload when you make changes.

### Production Build

```bash
npm run build
```

Builds the app for production to the `build/` folder.

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/         # Reusable components
│   │   ├── CompanyCard.jsx
│   │   ├── CompanyList.jsx
│   │   ├── ExtractionForm.jsx
│   │   ├── Navbar.jsx
│   │   └── SourceViewer.jsx
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx
│   │   ├── CompanyDetail.jsx
│   │   ├── NewExtraction.jsx
│   │   └── BatchExtraction.jsx
│   ├── services/
│   │   └── api.js          # API service layer
│   ├── App.jsx             # Main app with routing
│   ├── App.css
│   ├── index.js            # Entry point
│   └── index.css           # Global styles (Tailwind)
├── package.json
└── tailwind.config.js
```

## Features

### 1. Dashboard

- View all companies
- Search and filter companies
- Quick stats overview
- Navigate to company details

### 2. Company Details

- View company information
- Browse all sources
- View extracted data
- Download JSON documents

### 3. New Extraction

- Extract from single source
- Support for URL, PDF, HTML, text
- Choose crawl mode (summary/full)
- Real-time progress

### 4. Batch Extraction

- Process multiple sources at once
- Mix different source types
- Progress tracking
- Error handling

## Current Status

🟡 **Mock Mode**: The frontend currently uses mock data defined in `src/services/api.js`.

To connect to the real Python backend:

1. Ensure the backend API server is running (you'll need to create this)
2. Update API endpoints in `src/services/api.js`
3. Remove or comment out the mock data

## Next Steps

### Backend API Required

The Python backend currently only has CLI functionality. You need to create a REST API server using Flask or FastAPI with these endpoints:

```python
GET    /api/companies                 # List all companies
GET    /api/companies/:name            # Get company details
GET    /api/companies/:name/sources    # Get company sources
POST   /api/extract                    # Start new extraction
POST   /api/batch                      # Start batch extraction
GET    /api/sources/:id                # Get source document
```

Example Flask structure:

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
from src.pipeline.extractors.factory import ExtractorFactory
from src.pipeline.storage.document_store import DocumentStore

app = Flask(__name__)
CORS(app)

@app.route('/api/companies', methods=['GET'])
def get_companies():
    store = DocumentStore()
    companies = store.list_companies()
    return jsonify(companies)

# Add more endpoints...

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Styling

The project uses Tailwind CSS with custom utilities defined in:

- `src/index.css` - Global styles
- `src/App.css` - Component-specific styles
- `tailwind.config.js` - Tailwind configuration

Custom color scheme:

- Primary: Blue (#2563eb)
- Success: Green (#10b981)
- Warning: Yellow (#f59e0b)
- Danger: Red (#ef4444)

## Troubleshooting

### Port Already in Use

If port 3000 is busy:

```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
PORT=3001 npm start
```

### Module Not Found

```bash
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues

1. Check backend server is running
2. Verify CORS is enabled on backend
3. Check `.env` has correct API URL
4. Look at browser console for errors

## Development Tips

1. **Hot Reload**: Changes auto-reload in dev mode
2. **React DevTools**: Install browser extension for debugging
3. **Mock Data**: Edit `src/services/api.js` to change mock responses
4. **Styling**: Use Tailwind utility classes for rapid development
5. **Icons**: Import from `lucide-react` for consistent iconography

## Support

For issues or questions about the frontend, check:

- Browser console for errors
- Network tab for API issues
- React error overlay in dev mode
- Main project README.md for backend setup
