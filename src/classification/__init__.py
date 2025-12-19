"""
Classification module for sector/industry/sub_industry assignment.

This module provides deterministic classification using:
- Taxonomy from sub_Industry_Classification-in.csv
- Text similarity (TF-IDF, keyword matching)
- Hierarchical classification (sector → industry → sub_industry)

No LLM APIs are used in this implementation.
"""

from .models import Taxonomy, ClassificationResult, CompanyClassification
from .taxonomy import load_taxonomy
from .text_builder import build_company_text
from .similarity import compute_label_scores
from .classifier import classify_company

__all__ = [
    'Taxonomy',
    'ClassificationResult',
    'CompanyClassification',
    'load_taxonomy',
    'build_company_text',
    'compute_label_scores',
    'classify_company',
]
