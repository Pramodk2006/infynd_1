"""
Setup verification script.
Run this to check if all dependencies are installed correctly.
"""

import sys
from pathlib import Path

def check_imports():
    """Check if all required packages can be imported."""
    print("Checking dependencies...\n")
    
    packages = [
        ("httpx", "HTTP client for web requests"),
        ("bs4", "BeautifulSoup4 for HTML parsing"),
        ("lxml", "XML/HTML parser backend"),
        ("fitz", "PyMuPDF for PDF extraction"),
        ("pydantic", "Data validation and models"),
        ("typer", "CLI framework"),
        ("rich", "Terminal formatting"),
        ("filetype", "File type detection"),
    ]
    
    all_ok = True
    
    for package, description in packages:
        try:
            __import__(package)
            print(f"✓ {package:15} - {description}")
        except ImportError:
            print(f"✗ {package:15} - MISSING! {description}")
            all_ok = False
    
    print()
    
    if all_ok:
        print("✓ All dependencies are installed correctly!")
    else:
        print("✗ Some dependencies are missing.")
        print("\nPlease run: pip install -r requirements.txt")
        sys.exit(1)
    
    return all_ok


def check_structure():
    """Check if project structure is correct."""
    print("\nChecking project structure...\n")
    
    required_paths = [
        "src/pipeline/__init__.py",
        "src/pipeline/models/document.py",
        "src/pipeline/extractors/base.py",
        "src/pipeline/extractors/factory.py",
        "src/pipeline/extractors/pdf_extractor.py",
        "src/pipeline/extractors/html_extractor.py",
        "src/pipeline/extractors/url_extractor.py",
        "src/pipeline/extractors/text_extractor.py",
        "src/pipeline/storage/document_store.py",
        "src/pipeline/utils/text_processing.py",
        "src/pipeline/utils/url_utils.py",
        "main.py",
        "requirements.txt",
    ]
    
    all_ok = True
    base_path = Path(__file__).parent
    
    for path in required_paths:
        full_path = base_path / path
        if full_path.exists():
            print(f"✓ {path}")
        else:
            print(f"✗ {path} - MISSING!")
            all_ok = False
    
    print()
    
    if all_ok:
        print("✓ Project structure is correct!")
    else:
        print("✗ Some files are missing.")
        sys.exit(1)
    
    return all_ok


def check_imports_work():
    """Try importing the project modules."""
    print("\nChecking project modules...\n")
    
    try:
        from src.pipeline.models.document import Document
        print("✓ Document model imported")
    except Exception as e:
        print(f"✗ Failed to import Document: {e}")
        return False
    
    try:
        from src.pipeline.extractors.factory import ExtractorFactory
        print("✓ ExtractorFactory imported")
    except Exception as e:
        print(f"✗ Failed to import ExtractorFactory: {e}")
        return False
    
    try:
        from src.pipeline.storage.document_store import DocumentStore
        print("✓ DocumentStore imported")
    except Exception as e:
        print(f"✗ Failed to import DocumentStore: {e}")
        return False
    
    print("\n✓ All project modules imported successfully!")
    return True


def main():
    """Run all checks."""
    print("="*60)
    print("B2B Data Fusion Engine - Setup Verification")
    print("="*60)
    print()
    
    # Check dependencies
    if not check_imports():
        return
    
    # Check structure
    if not check_structure():
        return
    
    # Check module imports
    if not check_imports_work():
        return
    
    print("\n" + "="*60)
    print("✓ Setup verification complete!")
    print("="*60)
    print("\nYou can now:")
    print("1. Create test data: python create_test_data.py")
    print("2. Run extraction: python main.py extract [SOURCE] [COMPANY]")
    print("3. See help: python main.py --help")
    print()


if __name__ == "__main__":
    main()
