"""Create a simple test PDF for testing PDF extraction."""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from pathlib import Path
    
    # Create test_data directory if it doesn't exist
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Create PDF
    pdf_path = test_dir / "company_brochure.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    
    # Page 1
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "TechVision Inc.")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Leading Provider of AI Solutions")
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 680, "Company Overview")
    
    c.setFont("Helvetica", 11)
    text = [
        "TechVision Inc. is a cutting-edge technology company specializing in",
        "artificial intelligence and machine learning solutions for enterprises.",
        "",
        "Founded: 2015",
        "Headquarters: Austin, Texas",
        "Employees: 250+",
        "Annual Revenue: $50M+",
        "",
        "Our Mission:",
        "To democratize AI technology and make it accessible to businesses of all sizes.",
    ]
    
    y = 650
    for line in text:
        c.drawString(100, y, line)
        y -= 15
    
    c.showPage()
    
    # Page 2
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Products & Services")
    
    c.setFont("Helvetica", 11)
    products = [
        "",
        "1. AI Analytics Platform",
        "   - Real-time data processing",
        "   - Predictive modeling",
        "   - Custom dashboards",
        "",
        "2. Machine Learning API",
        "   - Pre-trained models",
        "   - Easy integration",
        "   - Scalable infrastructure",
        "",
        "3. Enterprise AI Consulting",
        "   - Strategy development",
        "   - Implementation support",
        "   - Training programs",
    ]
    
    y = 720
    for line in products:
        c.drawString(100, y, line)
        y -= 15
    
    c.save()
    
    print(f"✓ Created test PDF: {pdf_path}")
    print("\nYou can now test PDF extraction:")
    print(f'python main.py extract "{pdf_path}" "TechVision Inc"')
    
except ImportError:
    print("reportlab is not installed. Creating a text-based alternative test...")
    print("\nTo test PDF extraction, you need a PDF file.")
    print("Install reportlab: pip install reportlab")
    print("Or use any existing PDF file you have.")
