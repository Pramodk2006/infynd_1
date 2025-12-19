"""
Domain signal detection using keyword dictionaries.

Maps domain-specific terms to sectors/industries to boost classification precision.
"""

from typing import Dict, List, Set

# Domain keyword dictionaries
# Format: {label: [keywords...]}

SECTOR_KEYWORDS = {
    "Information Technology": [
        "software", "saas", "cloud", "computing", "api", "platform", "application",
        "tech", "digital", "it services", "developer", "programming", "code",
        "data center", "hosting", "infrastructure", "enterprise software"
    ],
    "Marketing & Advertising": [
        "marketing", "advertising", "branding", "campaign", "seo", "sem", "social media",
        "content marketing", "lead generation", "conversion", "analytics",
        "digital marketing", "growth hacking", "influencer"
    ],
    "Financial Services": [
        "banking", "finance", "investment", "trading", "payment", "fintech",
        "lending", "insurance", "wealth management", "financial advisory",
        "credit", "debit", "transaction", "accounting"
    ],
    "Healthcare": [
        "healthcare", "medical", "hospital", "clinic", "patient", "diagnosis",
        "treatment", "therapy", "pharmaceutical", "biotech", "health tech",
        "telemedicine", "healthtech"
    ],
    "Real Estate": [
        "real estate", "property", "residential", "commercial", "rental",
        "lease", "landlord", "tenant", "building", "construction",
        "facilities management", "proptech"
    ],
    "Retail": [
        "retail", "ecommerce", "e-commerce", "online store", "shopping",
        "merchandise", "consumer", "checkout", "cart", "inventory"
    ],
    "Education": [
        "education", "learning", "training", "course", "student", "teacher",
        "school", "university", "edtech", "e-learning", "lms", "tutorial"
    ]
}

INDUSTRY_KEYWORDS = {
    "AI Development": [
        "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
        "neural network", "computer vision", "nlp", "natural language processing",
        "generative ai", "llm", "large language model", "transformer"
    ],
    "Software Development & Services": [
        "crm", "erp", "enterprise software", "business software", "workflow",
        "automation", "integration", "customization", "deployment"
    ],
    "Technology Hardware & Peripherals": [
        "gpu", "graphics card", "processor", "chip", "semiconductor", "cuda",
        "hardware", "device", "accelerated computing", "compute",
        "laptop", "desktop", "server", "workstation"
    ],
    "Cloud Services": [
        "cloud", "aws", "azure", "gcp", "infrastructure", "iaas", "paas", "saas",
        "serverless", "microservices", "container", "kubernetes"
    ],
    "Data Analytics": [
        "analytics", "big data", "data science", "business intelligence", "bi",
        "dashboard", "visualization", "reporting", "insights", "metrics"
    ],
    "Cybersecurity": [
        "security", "cybersecurity", "encryption", "firewall", "vulnerability",
        "threat", "compliance", "privacy", "authentication", "zero trust"
    ]
}


def compute_domain_signal(company_text: str, label: str, label_type: str = "sector") -> float:
    """
    Compute a domain signal score based on keyword matching.
    
    Args:
        company_text: Normalized company text (lowercase)
        label: Sector or industry label
        label_type: "sector" or "industry"
        
    Returns:
        Signal score (0.0 to 1.0)
    """
    keywords_dict = SECTOR_KEYWORDS if label_type == "sector" else INDUSTRY_KEYWORDS
    
    if label not in keywords_dict:
        return 0.0
    
    keywords = keywords_dict[label]
    
    # Count keyword matches
    matches = 0
    for keyword in keywords:
        if keyword.lower() in company_text:
            matches += 1
    
    # Normalize by total keywords for this label
    if len(keywords) == 0:
        return 0.0
    
    signal = matches / len(keywords)
    
    # Cap at 1.0
    return min(signal, 1.0)


def get_all_domain_signals(company_text: str, labels: List[str], label_type: str = "sector") -> Dict[str, float]:
    """
    Compute domain signals for all labels.
    
    Returns:
        {label: signal_score}
    """
    signals = {}
    for label in labels:
        signals[label] = compute_domain_signal(company_text, label, label_type)
    
    return signals
