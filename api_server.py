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
from src.classification import load_taxonomy, classify_company
from src.classification.topk_classifier import classify_company_from_folder
from src.classification.classifier_topk_v2 import classify_company_topk_v2
from src.classification.ollama_embeddings import OllamaEmbeddingIndex
from src.classification.ollama_llm import classify_with_llm
from src.classification.text_builder import build_company_text
from src.extraction.enhanced_extractor import extract_all_data
from src.pipeline.extractors.llm_extractor import extract_all_business_info_llm
from src.database.cache import get_cache
import os
import threading

app = Flask(__name__)

# Enable CORS for all origins (development mode)
# Enable CORS for all origins (development mode)
CORS(app)

# Initialize storage
store = DocumentStore()
factory = ExtractorFactory()

# Initialize taxonomy (load once at startup)
TAXONOMY_PATH = Path("data/sub_Industry_Classification-in.csv")
taxonomy = None
if TAXONOMY_PATH.exists():
    try:
        taxonomy = load_taxonomy(str(TAXONOMY_PATH))
        print(f"✅ Taxonomy loaded: {len(taxonomy.unique_sectors)} sectors, "
              f"{len(taxonomy.unique_industries)} industries, "
              f"{len(taxonomy.unique_subindustries)} sub-industries")
    except Exception as e:
        print(f"⚠️  Failed to load taxonomy: {e}")
else:
    print(f"⚠️  Taxonomy file not found: {TAXONOMY_PATH}")


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
    """Get detailed information about a specific company with enhanced extraction"""
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

        # Get enhanced details parameter
        include_enhanced = request.args.get('enhanced', 'true').lower() == 'true'
        
        base_response = {
            "name": company_name,
            "totalSources": len(sources),
            "created": metadata.get("created_at"),
            "lastUpdated": metadata.get("last_updated"),
            "sources": sources,
        }
        
        if not include_enhanced:
            return jsonify(base_response)
        
        # Get enhanced business information
        try:
            # Get classification from v2 classifier
            classification = classify_company_topk_v2(
                company_name,
                use_ollama_summary=True,
                use_llm_rerank=False,
                k_sectors=5,
                k_industries=5,
                k_subindustries=10
            )
            
            # Extract all text from sources
            all_text = []
            html_content = None
            sources_dir = company_dir / "sources"
            
            if sources_dir.exists():
                for source_file in sources_dir.glob("*.json"):
                    with open(source_file, 'r', encoding='utf-8') as f:
                        source_data = json.load(f)
                        
                        # Get text
                        content = source_data.get('content', {})
                        raw_text = content.get('raw_text', '')
                        all_text.append(raw_text)
                        
                        # Get HTML if available (for logo extraction)
                        if not html_content and source_data.get('source', {}).get('type') == 'webpage':
                            html_content = content.get('html', '')
            
            combined_text = ' '.join(all_text)
            
            # Get classification results
            final_pred = classification.get('final_prediction', {})
            
            # Get domain from first source
            domain = company_name
            if sources and len(sources) > 0:
                first_source = sources[0]
                if 'url' in first_source:
                    from urllib.parse import urlparse
                    parsed = urlparse(first_source['url'])
                    domain = parsed.netloc or company_name
            
            # Extract all business info using Phi3.5 LLM
            enhanced_info = extract_all_business_info_llm(
                text=combined_text,
                html_content=html_content,
                domain=domain,
                company_name=company_name,
                short_description=metadata.get('description', '-'),
                long_description=final_pred.get('long_description', '-'),
                sector=final_pred.get('sector', '-'),
                industry=final_pred.get('industry', '-'),
                sub_industry=final_pred.get('sub_industry', '-'),
                sic_code=final_pred.get('sic_code', '-'),
                sic_text=final_pred.get('sic_description', '-')
            )
            
            # Merge with base response
            base_response['enhanced'] = enhanced_info
            
        except Exception as e:
            print(f"Error extracting enhanced info: {e}")
            import traceback
            traceback.print_exc()
            base_response['enhanced'] = {'error': str(e)}
        
        return jsonify(base_response)

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
        "taxonomy_loaded": taxonomy is not None
    })


@app.route('/api/classify/<company_name>', methods=['POST'])
def classify_company_endpoint(company_name):
    """
    Classify a company into sector/industry/sub_industry.
    
    Returns classification results with confidence scores.
    """
    try:
        if not taxonomy:
            return jsonify({
                "error": "Taxonomy not loaded. Please ensure sub_Industry_Classification-in.csv exists."
            }), 500
        
        # Check if company exists
        company_path = Path("data/outputs") / company_name
        if not company_path.exists():
            return jsonify({"error": f"Company '{company_name}' not found"}), 404
        
        # Perform classification
        print(f"🔍 Classifying company: {company_name}")
        result = classify_company(str(company_path), taxonomy)
        
        # Convert to dict for JSON response
        response = result.to_dict()
        
        print(f"✅ Classification complete:")
        print(f"   Sector: {result.sector.label} (score: {result.sector.score:.4f})")
        print(f"   Industry: {result.industry.label} (score: {result.industry.score:.4f})")
        print(f"   Sub-industry: {result.sub_industry.label} (score: {result.sub_industry.score:.4f})")
        
        # Save classification to company metadata
        _save_classification(company_name, response)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Classification error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def _save_classification(company_name: str, classification: Dict):
    """Save classification results to company metadata."""
    try:
        metadata_path = Path("data/outputs") / company_name / "metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        # Add classification
        metadata['classification'] = classification
        metadata['classification_updated_at'] = datetime.now().isoformat()
        
        # Save back
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
    except Exception as e:
        print(f"⚠️  Failed to save classification: {e}")


@app.route('/api/classify_compare/<company>', methods=['POST'])
def classify_compare(company):
    """
    Compare Ollama and Top-K Hierarchical classifiers.
    Returns results from both methods for comparison.
    """
    try:
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
        
        company_folder = Path("data/outputs") / company
        
        if not company_folder.exists():
            return jsonify({"error": f"Company '{company}' not found"}), 404
        
        # Get company text
        company_text = build_company_text(str(company_folder))
        
        # 1. Top-K Hierarchical Classifier
        print(f"Running Top-K classifier for {company}...")
        topk_result = None
        topk_error = None
        try:
            topk_result = classify_company_from_folder(str(company_folder), method='topk')
        except Exception as e:
            topk_error = str(e)
            print(f"Top-K error: {e}")
        
        # 2. Ollama Classifier
        print(f"Running Ollama classifier for {company}...")
        ollama_result = None
        ollama_error = None
        try:
            # Load index
            index = OllamaEmbeddingIndex()
            index.load('taxonomy_index')
            
            # Search embeddings
            candidates = index.search(company_text, top_k=20)
            
            # LLM classification
            ollama_result = classify_with_llm(company_text, candidates, company_name=company)
            
            if ollama_result:
                # Format to match expected structure
                ollama_result['alternatives'] = [
                    {
                        'sub_industry': c['sub_industry'],
                        'similarity': c['similarity']
                    }
                    for c in candidates[:5]
                ]
        except Exception as e:
            ollama_error = str(e)
            print(f"Ollama error: {e}")
        
        # Build response
        response = {
            "company": company,
            "text_length": len(company_text),
            "text_preview": company_text[:500],
            "topk": {
                "success": topk_result is not None and 'final_prediction' in topk_result,
                "error": topk_error,
                "result": topk_result if topk_result and 'final_prediction' in topk_result else None
            },
            "ollama": {
                "success": ollama_result is not None,
                "error": ollama_error,
                "result": ollama_result
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Classification comparison error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/classify_v2/<company>', methods=['POST'])
def classify_v2(company):
    """
    Enhanced Top-K classifier with specificity scoring, source quality weighting,
    evidence density, and conditional LLM re-ranking.
    """
    try:
        print(f"\n{'='*80}")
        print(f"🟢 Enhanced Classification (v2) for: {company}")
        print(f"{'='*80}\n")
        
        # Check if company data exists
        company_path = Path("data/outputs") / company
        if not company_path.exists():
            return jsonify({"error": f"Company '{company}' not found"}), 404
        
        # Run enhanced classifier
        result = classify_company_topk_v2(
            company,
            use_ollama_summary=True,
            k_sectors=5,
            k_industries=5,
            k_subindustries=10,
            use_llm_rerank=True,
            llm_model="qwen2.5:7b"
        )
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Enhanced classification error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/compare_v1_v2/<company>', methods=['POST'])
def compare_v1_v2(company):
    """
    Run both v1 and v2 classifiers side-by-side for comparison.
    """
    try:
        print(f"\n{'='*80}")
        print(f"⚖️ Comparing v1 vs v2 for: {company}")
        print(f"{'='*80}\n")
        
        # Check if company data exists
        company_path = Path("data/outputs") / company
        if not company_path.exists():
            return jsonify({"error": f"Company '{company}' not found"}), 404
        
        # Get company text for preview
        company_text = build_company_text(company, use_ollama_summary=True)
        
        # Run v1 (original Top-K)
        print("\n🔵 Running Top-K v1...")
        v1_result = None
        v1_error = None
        try:
            v1_result = classify_company_from_folder(company)
        except Exception as e:
            v1_error = str(e)
            print(f"❌ v1 failed: {e}")
        
        # Run v2 (enhanced)
        print("\n🟢 Running Top-K v2...")
        v2_result = None
        v2_error = None
        try:
            v2_result = classify_company_topk_v2(
                company,
                use_ollama_summary=True,
                use_llm_rerank=True,
                llm_model="qwen2.5:7b"
            )
        except Exception as e:
            v2_error = str(e)
            print(f"❌ v2 failed: {e}")
        
        response = {
            "company": company,
            "text_preview": company_text[:500] if company_text else None,
            "text_length": len(company_text) if company_text else 0,
            "v1": {
                "success": v1_result is not None and "error" not in v1_result,
                "error": v1_error,
                "result": v1_result
            },
            "v2": {
                "success": v2_result is not None and "error" not in v2_result,
                "error": v2_error,
                "result": v2_result
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Comparison error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def _prepare_enhanced_data_background(company: str, company_path: str):
    """Background task to prepare enhanced data"""
    cache = get_cache()
    
    try:
        print(f"\n🔄 [Background] Starting preparation for: {company}")
        
        # Mark as preparing
        cache.set(company, company_path, {}, status='preparing')
        
        # Run classification
        print(f"[Background] Running classification for {company}...")
        classification_result = classify_company_topk_v2(
            company,
            use_ollama_summary=True,
            use_llm_rerank=True,
            llm_model="qwen2.5:7b",
            k_sectors=5,
            k_industries=5,
            k_subindustries=10
        )
        
        # Extract all data
        print(f"[Background] Extracting enhanced data for {company}...")
        enhanced_data = extract_all_data(company_path, classification_result)
        enhanced_data['classification'] = classification_result
        
        # Save to cache as ready
        cache.set(company, company_path, enhanced_data, status='ready')
        
        print(f"✅ [Background] Preparation complete for: {company}\n")
        
    except Exception as e:
        error_msg = f"❌ [Background] Error preparing {company}: {e}"
        print(error_msg)
        
        # Log to file
        try:
            with open("backend_debug.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now().isoformat()}] {error_msg}\n")
                import traceback
                traceback.print_exc(file=f)
        except:
            pass
            
        cache.set_status(company, 'error')


@app.route('/api/companies/<company>/enhanced/status', methods=['GET'])
def get_enhanced_status(company):
    """Check if enhanced data is ready for a company"""
    try:
        cache = get_cache()
        status = cache.get_status(company)
        
        if status is None:
            return jsonify({'status': 'not_started', 'ready': False})
        
        return jsonify({
            'status': status,
            'ready': status == 'ready'
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/companies/<company>/enhanced/prepare', methods=['POST'])
def prepare_enhanced_data(company):
    """Start background preparation of enhanced data"""
    try:
        company_path = f"data/outputs/{company}"
        
        # Check if company exists
        if not Path(company_path).exists():
            return jsonify({"error": f"Company '{company}' not found"}), 404
        
        cache = get_cache()
        
        # Check if already preparing or ready
        status = cache.get_status(company)
        if status == 'preparing':
            return jsonify({
                'message': 'Already preparing',
                'status': 'preparing'
            })
        
        if status == 'ready':
            # Check if cache is still valid
            cached_data = cache.get(company, company_path)
            if cached_data:
                return jsonify({
                    'message': 'Already ready',
                    'status': 'ready'
                })
        
        # Start background preparation
        thread = threading.Thread(
            target=_prepare_enhanced_data_background,
            args=(company, company_path),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'message': 'Preparation started',
            'status': 'preparing'
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/summaries', methods=['GET'])
def get_all_summaries():
    """Get list of all prepared summaries"""
    try:
        cache = get_cache()
        summaries = cache.list_all()
        
        return jsonify({
            'summaries': summaries,
            'total': len(summaries)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/companies/<company>/enhanced', methods=['GET'])
def get_enhanced_company_data(company):
    """
    Get comprehensive extracted data for a company including:
    - All mandatory fields (domain, descriptions, SIC codes, sector/industry)
    - Company identity (registration, VAT, logo, acronym)
    - Contact information (address, phone, email, hours)
    - People information (names, titles)
    - Certifications
    - Services offered
    
    Uses database caching for fast retrieval on subsequent requests.
    """
    try:
        print(f"\n{'='*80}")
        print(f"Enhanced Data Extraction for: {company}")
        print(f"{'='*80}\n")
        
        company_path = f"data/outputs/{company}"
        
        # Check if company data exists
        if not Path(company_path).exists():
            return jsonify({"error": f"Company '{company}' not found"}), 404
        
        # Try to get from cache first
        cache = get_cache()
        cached_data = cache.get(company, company_path)
        
        if cached_data:
            print("✅ Retrieved from cache (fast retrieval)")
            print(f"   Cached at: {cached_data.get('extraction_timestamp', 'unknown')}")
            print(f"\n{'='*80}")
            print("Enhanced extraction complete (from cache)!")
            print(f"{'='*80}\n")
            return jsonify(cached_data)
        
        # Check if currently preparing
        status = cache.get_status(company)
        if status == 'preparing':
            return jsonify({
                'status': 'preparing',
                'message': 'Enhanced summary is being prepared in the background'
            }), 202  # 202 Accepted
        
        # Cache miss - run full extraction
        print("⚠️  Cache miss - running full extraction...")
        
        # First, run classification to get sector/industry/SIC
        print("Running classification...")
        classification_result = None
        try:
            classification_result = classify_company_topk_v2(
                company,
                use_ollama_summary=True,
                use_llm_rerank=False,
                k_sectors=5,
                k_industries=5,
                k_subindustries=10
            )
        except Exception as e:
            print(f"Classification failed: {e}")
        
        # Extract all data
        print("\nExtracting enhanced data...")
        enhanced_data = extract_all_data(company_path, classification_result)
        
        # Add classification results
        enhanced_data['classification'] = classification_result
        
        # Store in cache for future requests
        print("\n💾 Saving to cache...")
        cache.set(company, company_path, enhanced_data)
        
        print(f"\n{'='*80}")
        print("Enhanced extraction complete (saved to cache)!")
        print(f"{'='*80}\n")
        
        return jsonify(enhanced_data)
        
    except Exception as e:
        print(f"❌ Enhanced extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """Get cache statistics"""
    try:
        cache = get_cache()
        stats = cache.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached data"""
    try:
        cache = get_cache()
        cache.clear_all()
        return jsonify({"message": "Cache cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/cache/invalidate/<company>', methods=['DELETE'])
def invalidate_cache(company):
    """Invalidate cache for a specific company"""
    try:
        cache = get_cache()
        cache.delete(company)
        return jsonify({"message": f"Cache for '{company}' invalidated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    print("   POST /api/classify/<company>")
    print("   POST /api/classify_compare/<company>")
    print("   POST /api/classify_v2/<company>  [ENHANCED]")
    print("   POST /api/compare_v1_v2/<company>  [COMPARISON]")
    print("")
    print("   📑 Enhanced Summaries (Background Preparation):")
    print("   GET  /api/summaries                               [List all summaries]")
    print("   POST /api/companies/<name>/enhanced/prepare       [Start background prep]")
    print("   GET  /api/companies/<name>/enhanced/status        [Check prep status]")
    print("   GET  /api/companies/<name>/enhanced               [Get summary data]")
    print("")
    print("   💾 Cache Management:")
    print("   GET    /api/cache/stats              [View cache statistics]")
    print("   POST   /api/cache/clear              [Clear all cached data]")
    print("   DELETE /api/cache/invalidate/<name>  [Invalidate company cache]")
    print("")
    print("   GET  /api/health")
    print("=" * 60)
    print("💡 Frontend: Run 'cd frontend && npm start' in another terminal")
    print("=" * 60)
    
    # Show cache stats on startup
    try:
        cache = get_cache()
        stats = cache.get_stats()
        print(f"\n📊 Cache Status:")
        print(f"   Total: {stats['total_cached']} companies")
        print(f"   Ready: {stats['ready']} | Preparing: {stats['preparing']}")
        if stats['total_cached'] > 0:
            print(f"   Oldest: {stats['oldest_entry']}")
            print(f"   Newest: {stats['newest_entry']}")
        print(f"   Database: {stats['db_path']}")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"⚠️  Cache initialization: {e}\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
