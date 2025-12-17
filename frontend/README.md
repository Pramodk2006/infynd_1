# B2B Data Fusion - React Frontend

Modern React dashboard for managing company data extraction and visualization.

## Features

- 📊 Company dashboard with search and filtering
- 📝 Interactive extraction form (URL, PDF, HTML, text)
- 🔍 Company detail view with all sources
- 📄 JSON viewer for extracted data
- 📦 Batch processing interface
- 🎨 Modern UI with Tailwind CSS
- 📱 Responsive design

## Tech Stack

- React 18
- React Router for navigation
- Axios for API calls
- Tailwind CSS for styling
- Lucide React for icons
- React JSON View for data visualization

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── CompanyCard.jsx
│   │   ├── CompanyList.jsx
│   │   ├── ExtractionForm.jsx
│   │   ├── SourceViewer.jsx
│   │   └── Navbar.jsx
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── CompanyDetail.jsx
│   │   ├── NewExtraction.jsx
│   │   └── BatchExtraction.jsx
│   ├── services/
│   │   └── api.js
│   ├── App.jsx
│   ├── App.css
│   └── index.js
├── package.json
└── tailwind.config.js
```

## API Integration

The frontend expects a REST API backend running on `http://localhost:5000` with the following endpoints:

- `GET /api/companies` - List all companies
- `GET /api/companies/:name` - Get company details
- `POST /api/extract` - Submit extraction job
- `POST /api/batch` - Submit batch extraction
- `GET /api/sources/:id` - Get source document

## Environment Variables

Create a `.env` file:

```
REACT_APP_API_URL=http://localhost:5000
```

## Usage

1. **Dashboard**: View all companies and their extraction status
2. **New Extraction**: Submit single source for extraction
3. **Batch Extraction**: Submit multiple sources for one company
4. **Company Details**: View all sources and extracted data for a company
