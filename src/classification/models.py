"""
Data models for the classification system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class ClassificationResult:
    """Result of a single-level classification (sector, industry, or sub_industry)."""
    
    label: str
    score: float
    margin: float  # score - second_best_score
    candidates: List[Dict[str, float]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "label": self.label,
            "score": round(self.score, 4),
            "margin": round(self.margin, 4),
            "candidates": [
                {"label": c["label"], "score": round(c["score"], 4)}
                for c in self.candidates
            ]
        }


@dataclass
class CompanyClassification:
    """Complete classification result for a company."""
    
    company: str
    sector: ClassificationResult
    industry: ClassificationResult
    sub_industry: ClassificationResult
    sic_code: Optional[str] = None
    sic_description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "company": self.company,
            "sector": self.sector.to_dict(),
            "industry": self.industry.to_dict(),
            "sub_industry": self.sub_industry.to_dict()
        }
        
        if self.sic_code:
            result["sic_code"] = self.sic_code
        if self.sic_description:
            result["sic_description"] = self.sic_description
            
        return result


@dataclass
class Taxonomy:
    """Indexed taxonomy structure for efficient classification."""
    
    # Raw DataFrame
    df: 'pd.DataFrame'
    
    # Unique values
    unique_sectors: List[str]
    unique_industries: List[str]
    unique_subindustries: List[str]
    
    # Hierarchical mappings
    industries_by_sector: Dict[str, List[str]]
    subindustries_by_sector_industry: Dict[Tuple[str, str], List[str]]
    
    # Lookup metadata
    sic_by_subindustry: Dict[str, Dict[str, str]]
    
    # Precomputed label texts for similarity
    sector_texts: Dict[str, str]
    industry_texts: Dict[str, str]
    subindustry_texts: Dict[str, str]
    
    def get_industries_for_sector(self, sector: str) -> List[str]:
        """Get all industries within a sector."""
        return self.industries_by_sector.get(sector, [])
    
    def get_subindustries_for_sector_industry(self, sector: str, industry: str) -> List[str]:
        """Get all sub_industries within a sector and industry."""
        return self.subindustries_by_sector_industry.get((sector, industry), [])
    
    def get_sic_metadata(self, subindustry: str) -> Optional[Dict[str, str]]:
        """Get SIC code and description for a sub_industry."""
        return self.sic_by_subindustry.get(subindustry)
