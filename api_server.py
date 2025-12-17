"""
Flask API Server for B2B Data Fusion Engine
Provides REST endpoints for the React frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional

from src.pipeline.extractors.factory import ExtractorFactory
from src.pipeline.storage.document_store import DocumentStore
from src.pipeline.models.document import Document

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize storage
store = DocumentStore()
factory = ExtractorFactory()


@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get list of all companies with metadata"""
    try:
        companies_dir = Path("data/outputs")
        if not companies_dir.exists():
            return jsonify([])

        companies = []
        for company_dir in companies_dir.iterdir():
            if not company_dir.is_dir():
                continue

            metadata_file = company_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    companies.append({
                        "name": company_dir.name,
                        "totalSources": len(metadata.get("sources", [])),
                        "created": metadata.get("created_at"),
                        "lastUpdated": metadata.get("last_updated"),
                    })

        # Sort by last updated
        companies.sort(key=lambda x: x.get("lastUpdated", ""), reverse=True)
        return jsonify(companies)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/companies/<company_name>', methods=['GET'])
def get_company_detail(company_name: str):
    """Get detailed information about a specific company"""
    try:
        company_dir = Path("data/outputs") / company_name
        if not company_dir.exists():
            return jsonify({"error": "Company not found"}), 404

        metadata_file = company_dir / "metadata.json"
        if not metadata_file.exists():
            return jsonify({"error": "Company metadata not found"}), 404

        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Load source details
        sources = []
        index_file = company_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                sources = index_data.get("sources", [])

        return jsonify({
            "name": company_name,
            "totalSources": len(sources),
            "created": metadata.get("created_at"),
            "lastUpdated": metadata.get("last_updated"),
            "sources": sources,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sources/<path:document_id>', methods=['GET'])
def get_source_document(document_id: str):
    """Get the full document JSON for a specific source"""
    try:
        # Search for the document in all companies
        companies_dir = Path("data/outputs")
        for company_dir in companies_dir.iterdir():
            if not company_dir.is_dir():
                continue

            sources_dir = company_dir / "sources"
            if not sources_dir.exists():
                continue

            # Look for file containing this document_id
            for source_file in sources_dir.glob("*.json"):
                with open(source_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("document_id") == document_id:
                        return jsonify(data)

        return jsonify({"error": "Document not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/extract', methods=['POST'])
def extract_single():
    """Start a new extraction from a single source"""
    try:
        data = request.json
        print(f"[DEBUG] Received extraction request: {data}")
        
        company = data.get("company")
        source = data.get("source")
        crawl_mode = data.get("crawlMode", "summary")
        max_pages = int(data.get("maxPages", 50))  # Convert to int
        
        print(f"[DEBUG] Params: company={company}, source={source}, mode={crawl_mode}, max={max_pages}")

        if not company or not source:
            return jsonify({"error": "Missing required fields: company, source"}), 400

        # Get appropriate extractor
        extractor = factory.get_extractor(source)
        if not extractor:
            return jsonify({"error": f"No extractor found for source: {source}"}), 400

        print(f"[DEBUG] Using extractor: {extractor.__class__.__name__}")

        # Extract document
        options = {
            "crawl_mode": crawl_mode,
            "max_pages": max_pages,
        }
        document = extractor.extract(source, company, **options)

        if not document:
            return jsonify({"error": "Extraction failed"}), 500

        # Save to storage
        filepath = store.save(document)

        return jsonify({
            "success": True,
            "document_id": document.document_id,
            "company": company,
            "source_type": document.source.type,
            "filepath": str(filepath),
            "message": f"Successfully extracted from {source}",
        })

    except Exception as e:
        print(f"[ERROR] Extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/batch', methods=['POST'])
def extract_batch():
    """Start a batch extraction from multiple sources"""
    try:
        data = request.json
        company = data.get("company")
        sources = data.get("sources", [])
        crawl_mode = data.get("crawlMode", "summary")

        if not company or not sources:
            return jsonify({"error": "Missing required fields: company, sources"}), 400

        results = {
            "success": [],
            "failed": [],
        }

        for source_item in sources:
            source_value = source_item.get("value")
            if not source_value:
                continue

            try:
                extractor = factory.get_extractor(source_value)
                if not extractor:
                    results["failed"].append({
                        "source": source_value,
                        "error": "No extractor found",
                    })
                    continue

                options = {"crawl_mode": crawl_mode}
                document = extractor.extract(source_value, company, **options)

                if document:
                    filepath = store.save(document)
                    results["success"].append({
                        "source": source_value,
                        "document_id": document.document_id,
                        "filepath": str(filepath),
                    })
                else:
                    results["failed"].append({
                        "source": source_value,
                        "error": "Extraction failed",
                    })

            except Exception as e:
                results["failed"].append({
                    "source": source_value,
                    "error": str(e),
                })

        return jsonify({
            "company": company,
            "total": len(sources),
            "successful": len(results["success"]),
            "failed": len(results["failed"]),
            "results": results,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 B2B Data Fusion Engine API Server")
    print("=" * 60)
    print("📡 Server running at: http://localhost:5000")
    print("📊 API endpoints:")
    print("   GET  /api/companies")
    print("   GET  /api/companies/<name>")
    print("   GET  /api/sources/<id>")
    print("   POST /api/extract")
    print("   POST /api/batch")
    print("   GET  /api/health")
    print("=" * 60)
    print("💡 Frontend: Run 'cd frontend && npm start' in another terminal")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
