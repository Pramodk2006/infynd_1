"""
Frontend Integration Test
Run this to verify the API server is working correctly
"""

import requests
import json
from rich.console import Console
from rich.table import Table

console = Console()

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test health check endpoint"""
    console.print("\n[bold blue]Testing Health Check...[/bold blue]")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            console.print(f"✅ Health check: {data['status']}")
            console.print(f"   Version: {data['version']}")
            console.print(f"   Timestamp: {data['timestamp']}")
            return True
        else:
            console.print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        console.print("❌ Cannot connect to API server")
        console.print("   Make sure to run: python api_server.py")
        return False

def test_companies():
    """Test companies list endpoint"""
    console.print("\n[bold blue]Testing Companies List...[/bold blue]")
    try:
        response = requests.get(f"{BASE_URL}/companies")
        if response.status_code == 200:
            companies = response.json()
            console.print(f"✅ Found {len(companies)} companies")
            
            if companies:
                table = Table(title="Companies")
                table.add_column("Name", style="cyan")
                table.add_column("Sources", style="magenta")
                table.add_column("Last Updated", style="green")
                
                for company in companies:
                    table.add_row(
                        company['name'],
                        str(company['totalSources']),
                        company.get('lastUpdated', 'N/A')
                    )
                
                console.print(table)
            else:
                console.print("   No companies found yet")
                console.print("   Try running: python main.py extract test_data/acme_about.html \"Acme Corporation\"")
            return True
        else:
            console.print(f"❌ Companies list failed: {response.status_code}")
            return False
    except Exception as e:
        console.print(f"❌ Error: {e}")
        return False

def test_company_detail():
    """Test company detail endpoint"""
    console.print("\n[bold blue]Testing Company Detail...[/bold blue]")
    try:
        # First get list of companies
        response = requests.get(f"{BASE_URL}/companies")
        companies = response.json()
        
        if not companies:
            console.print("⚠️  No companies to test detail view")
            console.print("   Create a company first using the CLI")
            return True
        
        # Get detail of first company
        company_name = companies[0]['name']
        response = requests.get(f"{BASE_URL}/companies/{company_name}")
        
        if response.status_code == 200:
            data = response.json()
            console.print(f"✅ Company detail for: {data['name']}")
            console.print(f"   Total sources: {data['totalSources']}")
            console.print(f"   Created: {data.get('created', 'N/A')}")
            
            if data.get('sources'):
                console.print(f"\n   Sources:")
                for i, source in enumerate(data['sources'][:3], 1):
                    console.print(f"   {i}. [{source['type'].upper()}] {source['title']}")
                
                if len(data['sources']) > 3:
                    console.print(f"   ... and {len(data['sources']) - 3} more")
            
            return True
        else:
            console.print(f"❌ Company detail failed: {response.status_code}")
            return False
    except Exception as e:
        console.print(f"❌ Error: {e}")
        return False

def main():
    console.print("[bold green]╔══════════════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║  Frontend Integration Test                  ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════════════╝[/bold green]")
    
    console.print("\n[yellow]This will test the Flask API endpoints[/yellow]")
    console.print("[yellow]Make sure api_server.py is running![/yellow]")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Companies List", test_companies()))
    results.append(("Company Detail", test_company_detail()))
    
    # Summary
    console.print("\n[bold]Test Summary:[/bold]")
    console.print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        console.print(f"{status} - {test_name}")
    
    console.print("=" * 50)
    console.print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        console.print("\n[bold green]🎉 All tests passed! API is working correctly.[/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Start the frontend: cd frontend && npm start")
        console.print("2. Open http://localhost:3000 in your browser")
        console.print("3. Start extracting company data!")
    else:
        console.print("\n[bold red]⚠️  Some tests failed. Check the API server.[/bold red]")
        console.print("\nMake sure:")
        console.print("- api_server.py is running")
        console.print("- Port 5000 is not blocked")
        console.print("- You have some extracted data in data/outputs/")

if __name__ == "__main__":
    main()
