"""
B2B Data Fusion Engine - Multi-format Data Extraction Pipeline

Main CLI interface for extracting company data from multiple sources.
"""

import sys
from pathlib import Path
from typing import List, Optional
from enum import Enum

try:
    import typer
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich import print as rprint
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline.extractors.factory import ExtractorFactory
from src.pipeline.storage.document_store import DocumentStore


app = typer.Typer(help="B2B Data Fusion Engine - Extract company data from multiple sources")
console = Console()


class CrawlMode(str, Enum):
    """Web crawling modes."""
    SUMMARY = "summary"
    FULL = "full"


@app.command()
def extract(
    source: str = typer.Argument(..., help="Source to extract from (URL, PDF, HTML, or text file)"),
    company: str = typer.Argument(..., help="Company name"),
    crawl_mode: CrawlMode = typer.Option(
        CrawlMode.SUMMARY,
        "--crawl-mode",
        "-m",
        help="Web crawl mode: 'summary' (2 pages) or 'full' (entire site)"
    ),
    max_pages: int = typer.Option(50, "--max-pages", "-p", help="Maximum pages to crawl in full mode"),
    chunk_size: int = typer.Option(512, "--chunk-size", "-c", help="Text chunk size for vector DB"),
    output_dir: str = typer.Option("data/outputs", "--output", "-o", help="Output directory"),
):
    """
    Extract content from a single source (URL, PDF, HTML, or text file).
    
    Examples:
        
        # Extract from website (summary mode - 2 pages)
        python main.py extract "https://example.com" "Example Corp"
        
        # Extract from website (full crawl)
        python main.py extract "https://example.com" "Example Corp" --crawl-mode full
        
        # Extract from PDF
        python main.py extract "./brochure.pdf" "Example Corp"
        
        # Extract from HTML file
        python main.py extract "./about.html" "Example Corp"
    """
    console.print(f"\n[bold blue]B2B Data Fusion Engine[/bold blue]")
    console.print(f"[cyan]Company:[/cyan] {company}")
    console.print(f"[cyan]Source:[/cyan] {source}")
    
    # Detect source type
    source_type = ExtractorFactory.detect_source_type(source)
    console.print(f"[cyan]Type:[/cyan] {source_type}")
    
    if source_type == 'url':
        console.print(f"[cyan]Crawl mode:[/cyan] {crawl_mode.value}")
    
    # Get appropriate extractor
    extractor = ExtractorFactory.get_extractor(source)
    
    if extractor is None:
        console.print(f"[red]✗ Could not determine extractor for source: {source}[/red]")
        raise typer.Exit(code=1)
    
    # Extract with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting content...", total=None)
        
        try:
            document = extractor.extract(
                source,
                company,
                crawl_mode=crawl_mode.value,
                max_pages=max_pages,
                chunk_size=chunk_size
            )
        except Exception as e:
            progress.stop()
            console.print(f"\n[red]✗ Extraction failed: {e}[/red]")
            raise typer.Exit(code=1)
    
    if document is None:
        console.print(f"\n[red]✗ No content extracted from {source}[/red]")
        raise typer.Exit(code=1)
    
    # Save document
    store = DocumentStore(output_dir)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Saving document...", total=None)
        filepath = store.save(document)
    
    # Display summary
    console.print(f"\n[green]✓ Extraction complete![/green]\n")
    
    table = Table(show_header=False, box=None)
    table.add_row("[cyan]Document ID:[/cyan]", document.document_id)
    table.add_row("[cyan]Title:[/cyan]", document.metadata.title or "N/A")
    table.add_row("[cyan]Raw text length:[/cyan]", f"{len(document.content.raw_text):,} characters")
    table.add_row("[cyan]Chunks:[/cyan]", str(len(document.content.chunks)))
    
    if document.content.structured:
        table.add_row("[cyan]Headings:[/cyan]", str(len(document.content.structured.headings)))
        table.add_row("[cyan]Paragraphs:[/cyan]", str(len(document.content.structured.paragraphs)))
        table.add_row("[cyan]Lists:[/cyan]", str(len(document.content.structured.lists)))
        table.add_row("[cyan]Tables:[/cyan]", str(len(document.content.structured.tables)))
    
    table.add_row("[cyan]Saved to:[/cyan]", str(filepath))
    
    console.print(table)
    console.print()


@app.command()
def batch(
    company: str = typer.Argument(..., help="Company name"),
    sources: List[str] = typer.Argument(..., help="List of sources to extract from"),
    crawl_mode: CrawlMode = typer.Option(
        CrawlMode.SUMMARY,
        "--crawl-mode",
        "-m",
        help="Web crawl mode for URLs"
    ),
    max_pages: int = typer.Option(50, "--max-pages", "-p", help="Maximum pages to crawl per URL"),
    chunk_size: int = typer.Option(512, "--chunk-size", "-c", help="Text chunk size"),
    output_dir: str = typer.Option("data/outputs", "--output", "-o", help="Output directory"),
):
    """
    Extract content from multiple sources for a single company.
    
    Example:
        python main.py batch "Example Corp" source1.pdf https://example.com source3.html
    """
    console.print(f"\n[bold blue]B2B Data Fusion Engine - Batch Processing[/bold blue]")
    console.print(f"[cyan]Company:[/cyan] {company}")
    console.print(f"[cyan]Sources:[/cyan] {len(sources)}\n")
    
    store = DocumentStore(output_dir)
    success_count = 0
    failed_sources = []
    
    for i, source in enumerate(sources, 1):
        console.print(f"[bold]Processing {i}/{len(sources)}:[/bold] {source}")
        
        # Detect source type
        source_type = ExtractorFactory.detect_source_type(source)
        console.print(f"  Type: {source_type}")
        
        # Get extractor
        extractor = ExtractorFactory.get_extractor(source)
        
        if extractor is None:
            console.print(f"  [red]✗ Could not determine extractor[/red]\n")
            failed_sources.append(source)
            continue
        
        # Extract
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("  Extracting...", total=None)
                
                document = extractor.extract(
                    source,
                    company,
                    crawl_mode=crawl_mode.value,
                    max_pages=max_pages,
                    chunk_size=chunk_size
                )
            
            if document is None:
                console.print(f"  [red]✗ No content extracted[/red]\n")
                failed_sources.append(source)
                continue
            
            # Save
            filepath = store.save(document)
            console.print(f"  [green]✓ Saved to {filepath.name}[/green]\n")
            success_count += 1
            
        except Exception as e:
            console.print(f"  [red]✗ Error: {e}[/red]\n")
            failed_sources.append(source)
    
    # Summary
    console.print(f"[bold]Batch processing complete![/bold]")
    console.print(f"[green]Successful:[/green] {success_count}/{len(sources)}")
    
    if failed_sources:
        console.print(f"[red]Failed:[/red] {len(failed_sources)}")
        for source in failed_sources:
            console.print(f"  - {source}")
    
    console.print()


@app.command()
def list_companies(
    output_dir: str = typer.Option("data/outputs", "--output", "-o", help="Output directory"),
):
    """List all companies in the data store."""
    store = DocumentStore(output_dir)
    companies = store.list_companies()
    
    if not companies:
        console.print("[yellow]No companies found in data store.[/yellow]")
        return
    
    console.print(f"\n[bold]Companies in data store:[/bold] {len(companies)}\n")
    
    table = Table(show_header=True)
    table.add_column("Company", style="cyan")
    table.add_column("Sources", justify="right")
    table.add_column("Last Updated", style="dim")
    
    for company in companies:
        metadata = store.get_company_metadata(company)
        if metadata:
            table.add_row(
                metadata.get('company', company),
                str(metadata.get('total_sources', 0)),
                metadata.get('last_updated', 'N/A')[:19]
            )
    
    console.print(table)
    console.print()


@app.command()
def info(
    company: str = typer.Argument(..., help="Company name"),
    output_dir: str = typer.Option("data/outputs", "--output", "-o", help="Output directory"),
):
    """Show information about a company's extracted data."""
    store = DocumentStore(output_dir)
    
    metadata = store.get_company_metadata(company)
    if not metadata:
        console.print(f"[red]Company '{company}' not found in data store.[/red]")
        raise typer.Exit(code=1)
    
    sources = store.list_sources(company)
    
    console.print(f"\n[bold blue]Company Information[/bold blue]")
    console.print(f"[cyan]Name:[/cyan] {metadata.get('company', company)}")
    console.print(f"[cyan]Total sources:[/cyan] {metadata.get('total_sources', 0)}")
    console.print(f"[cyan]Created:[/cyan] {metadata.get('created', 'N/A')[:19]}")
    console.print(f"[cyan]Last updated:[/cyan] {metadata.get('last_updated', 'N/A')[:19]}\n")
    
    if sources:
        console.print(f"[bold]Sources:[/bold]\n")
        
        table = Table(show_header=True)
        table.add_column("Type", style="cyan")
        table.add_column("Title")
        table.add_column("URI", style="dim", overflow="fold")
        table.add_column("Extracted", style="dim")
        
        for source in sources:
            table.add_row(
                source.get('type', 'N/A'),
                source.get('title', 'N/A')[:50],
                source.get('uri', 'N/A')[:60],
                source.get('extracted_at', 'N/A')[:19]
            )
        
        console.print(table)
    
    console.print()


@app.command()
def version():
    """Show version information."""
    console.print("\n[bold blue]B2B Data Fusion Engine[/bold blue]")
    console.print("[cyan]Version:[/cyan] 0.1.0")
    console.print("[cyan]Description:[/cyan] Multi-format data extraction pipeline")
    console.print()


if __name__ == "__main__":
    app()
