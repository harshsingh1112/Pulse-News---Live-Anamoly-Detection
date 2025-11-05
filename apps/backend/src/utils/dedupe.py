"""URL deduplication utilities."""

from typing import Set
from urllib.parse import urlparse, parse_qs


def normalize_url(url: str) -> str:
    """Normalize URL for deduplication."""
    parsed = urlparse(url)
    
    # Remove common tracking parameters
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    filtered_params = {
        k: v for k, v in query_params.items()
        if k not in ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "ref", "fbclid"]
    }
    
    # Reconstruct URL
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if filtered_params:
        # Simple query string reconstruction
        query_parts = []
        for k, v in filtered_params.items():
            if v:
                query_parts.append(f"{k}={v[0]}")
        if query_parts:
            normalized += "?" + "&".join(query_parts)
    
    if parsed.fragment:
        normalized += f"#{parsed.fragment}"
    
    return normalized.lower().strip()


def dedupe_urls(urls: list[str]) -> list[str]:
    """Deduplicate a list of URLs."""
    seen = set()
    unique = []
    
    for url in urls:
        normalized = normalize_url(url)
        if normalized not in seen:
            seen.add(normalized)
            unique.append(url)
    
    return unique

