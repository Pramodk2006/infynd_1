"""
Sample test script to verify the extraction pipeline works.

This creates test data and runs extractions to verify the system.
"""

import os
from pathlib import Path

# Create test data directory
test_dir = Path("test_data")
test_dir.mkdir(exist_ok=True)

# Create sample HTML file
sample_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Acme Corporation - Innovative Solutions</title>
    <meta name="description" content="Acme Corp provides cutting-edge technology solutions for businesses worldwide.">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/products">Products</a>
        </nav>
    </header>
    
    <main>
        <h1>Welcome to Acme Corporation</h1>
        
        <section>
            <h2>About Us</h2>
            <p>Acme Corporation is a leading provider of innovative technology solutions. Founded in 2010, 
            we have been serving businesses worldwide with cutting-edge products and services.</p>
            
            <p>Our mission is to empower businesses through technology, delivering solutions that drive 
            growth and efficiency.</p>
        </section>
        
        <section>
            <h2>Our Products</h2>
            <ul>
                <li>Enterprise Software Solutions</li>
                <li>Cloud Infrastructure Services</li>
                <li>Data Analytics Platform</li>
                <li>AI-Powered Business Tools</li>
            </ul>
        </section>
        
        <section>
            <h2>Industries We Serve</h2>
            <table>
                <thead>
                    <tr>
                        <th>Industry</th>
                        <th>Solutions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Healthcare</td>
                        <td>Patient management systems, data analytics</td>
                    </tr>
                    <tr>
                        <td>Finance</td>
                        <td>Risk assessment, trading platforms</td>
                    </tr>
                    <tr>
                        <td>Retail</td>
                        <td>Inventory management, customer analytics</td>
                    </tr>
                </tbody>
            </table>
        </section>
        
        <section>
            <h2>Why Choose Acme?</h2>
            <ol>
                <li>15+ years of industry experience</li>
                <li>Award-winning technology</li>
                <li>24/7 customer support</li>
                <li>Global presence in 50+ countries</li>
            </ol>
        </section>
    </main>
    
    <footer>
        <p>© 2025 Acme Corporation. All rights reserved.</p>
    </footer>
</body>
</html>
"""

with open(test_dir / "acme_about.html", "w", encoding="utf-8") as f:
    f.write(sample_html)

print("✓ Created sample HTML file: test_data/acme_about.html")

# Create sample text file
sample_text = """
Acme Corporation - Company Overview

Acme Corporation is a global leader in enterprise technology solutions, specializing in cloud 
infrastructure, data analytics, and AI-powered business tools.

Key Facts:
- Founded: 2010
- Headquarters: San Francisco, CA
- Employees: 5,000+
- Global Offices: 50+ countries
- Annual Revenue: $500M+

Products and Services:
1. Enterprise Software Solutions - Custom software development for large organizations
2. Cloud Infrastructure Services - Scalable cloud hosting and management
3. Data Analytics Platform - Advanced analytics and business intelligence
4. AI-Powered Business Tools - Machine learning solutions for automation

Target Industries:
- Healthcare: Patient management, medical data analytics
- Finance: Risk assessment, algorithmic trading platforms
- Retail: Inventory optimization, customer behavior analytics
- Manufacturing: Supply chain management, predictive maintenance

Awards and Recognition:
- Best Enterprise Software 2024 - Tech Innovation Awards
- Top 50 Cloud Providers - Cloud Computing Magazine
- AI Excellence Award 2023 - AI Global Summit

Recent News:
- Launched new AI analytics platform in Q4 2024
- Expanded operations to Southeast Asia
- Partnership with major healthcare provider for EMR system
- Achieved ISO 27001 certification for data security

Contact Information:
Email: info@acmecorp.com
Phone: +1-800-ACME-TECH
Website: https://www.acmecorp.com
"""

with open(test_dir / "acme_overview.txt", "w", encoding="utf-8") as f:
    f.write(sample_text)

print("✓ Created sample text file: test_data/acme_overview.txt")

print("\n" + "="*60)
print("Test files created successfully!")
print("="*60)
print("\nNow you can test the extraction pipeline:")
print("\n1. Extract from HTML:")
print("   python main.py extract test_data/acme_about.html \"Acme Corporation\"")
print("\n2. Extract from text file:")
print("   python main.py extract test_data/acme_overview.txt \"Acme Corporation\"")
print("\n3. Batch processing:")
print("   python main.py batch \"Acme Corporation\" test_data/acme_about.html test_data/acme_overview.txt")
print("\n4. View company info:")
print("   python main.py info \"Acme Corporation\"")
print("\n5. List all companies:")
print("   python main.py list-companies")
print("\n" + "="*60)
