"""
Taxonomy loader and indexer.

Loads sub_Industry_Classification-in.csv and builds efficient lookup structures.
"""

import pandas as pd
from typing import Dict, List, Tuple
from pathlib import Path
from .models import Taxonomy


def load_taxonomy(csv_path: str) -> Taxonomy:
    """
    Load and index the taxonomy CSV.
    
    Args:
        csv_path: Path to sub_Industry_Classification-in.csv
        
    Returns:
        Taxonomy object with indexed structures and precomputed label texts
    """
    # Load CSV
    df = pd.read_csv(csv_path)
    
    # Clean column names (remove spaces)
    df.columns = df.columns.str.strip()
    
    # Extract unique values
    unique_sectors = sorted(df['sector'].dropna().unique().tolist())
    unique_industries = sorted(df['Industry'].dropna().unique().tolist())
    unique_subindustries = sorted(df['sub_industry'].dropna().unique().tolist())
    
    # Build hierarchical mappings
    industries_by_sector: Dict[str, List[str]] = {}
    for sector in unique_sectors:
        industries = df[df['sector'] == sector]['Industry'].dropna().unique().tolist()
        industries_by_sector[sector] = sorted(industries)
    
    subindustries_by_sector_industry: Dict[Tuple[str, str], List[str]] = {}
    for _, row in df.iterrows():
        sector = row['sector']
        industry = row['Industry']
        subindustry = row['sub_industry']
        
        if pd.notna(sector) and pd.notna(industry) and pd.notna(subindustry):
            key = (sector, industry)
            if key not in subindustries_by_sector_industry:
                subindustries_by_sector_industry[key] = []
            if subindustry not in subindustries_by_sector_industry[key]:
                subindustries_by_sector_industry[key].append(subindustry)
    
    # Sort sub_industries for each key
    for key in subindustries_by_sector_industry:
        subindustries_by_sector_industry[key] = sorted(subindustries_by_sector_industry[key])
    
    # Build SIC metadata lookup
    sic_by_subindustry: Dict[str, Dict[str, str]] = {}
    for _, row in df.iterrows():
        subindustry = row['sub_industry']
        if pd.notna(subindustry):
            sic_by_subindustry[subindustry] = {
                'sector': str(row['sector']) if pd.notna(row['sector']) else '',
                'industry': str(row['Industry']) if pd.notna(row['Industry']) else '',
                'sic_code': str(row['sic_code']) if pd.notna(row['sic_code']) else '',
                'sic_description': str(row['sic_description']) if pd.notna(row['sic_description']) else ''
            }
    
    # Precompute label texts for similarity
    # Enrich sectors with their industries for better TF-IDF matching
    sector_texts: Dict[str, str] = {}
    for sector in unique_sectors:
        # Get all industries in this sector
        industries = industries_by_sector.get(sector, [])
        industries_str = " ".join(industries[:10])  # Include top 10 industries
        sector_texts[sector] = f"sector: {sector}. {industries_str}"
    
    # Enrich industries with SIC descriptions from their sub-industries
    industry_texts: Dict[str, str] = {}
    for _, row in df[['sector', 'Industry']].drop_duplicates().iterrows():
        if pd.notna(row['sector']) and pd.notna(row['Industry']):
            sector = row['sector']
            industry = row['Industry']
            # Get sample sub-industries and their SIC descriptions
            key = (sector, industry)
            subinds = subindustries_by_sector_industry.get(key, [])
            subinds_str = " ".join(subinds[:10])  # Include top 10 sub-industries
            
            # Get sample SIC descriptions for this industry
            sic_descs = df[(df['sector'] == sector) & (df['Industry'] == industry)]['sic_description'].dropna().unique()
            sic_str = " ".join(sic_descs[:5])  # Top 5 SIC descriptions
            
            industry_texts[industry] = f"industry: {industry} in sector {sector}. {subinds_str}. {sic_str}"
    
    subindustry_texts: Dict[str, str] = {}
    for _, row in df.iterrows():
        if pd.notna(row['sub_industry']):
            subindustry = row['sub_industry']
            industry = row['Industry'] if pd.notna(row['Industry']) else ''
            sector = row['sector'] if pd.notna(row['sector']) else ''
            sic_desc = row['sic_description'] if pd.notna(row['sic_description']) else ''
            
            # Enhanced with repeated SIC description for better matching
            subindustry_texts[subindustry] = (
                f"sub_industry: {subindustry}. "
                f"industry: {industry}. "
                f"sector: {sector}. "
                f"{sic_desc}. "
                f"{sic_desc}"  # Repeat for weight
            )
    
    return Taxonomy(
        df=df,
        unique_sectors=unique_sectors,
        unique_industries=unique_industries,
        unique_subindustries=unique_subindustries,
        industries_by_sector=industries_by_sector,
        subindustries_by_sector_industry=subindustries_by_sector_industry,
        sic_by_subindustry=sic_by_subindustry,
        sector_texts=sector_texts,
        industry_texts=industry_texts,
        subindustry_texts=subindustry_texts
    )
