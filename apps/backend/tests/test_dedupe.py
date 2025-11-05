"""Tests for URL deduplication."""

import pytest
from src.utils.dedupe import normalize_url, dedupe_urls


def test_normalize_url():
    """Test URL normalization."""
    url1 = "https://example.com/article?utm_source=test"
    url2 = "https://example.com/article"
    
    norm1 = normalize_url(url1)
    norm2 = normalize_url(url2)
    
    # Should remove tracking params
    assert "utm_source" not in norm1
    assert norm1 == norm2


def test_dedupe_urls():
    """Test URL deduplication."""
    urls = [
        "https://example.com/article",
        "https://example.com/article?utm_source=test",
        "https://example.com/article?ref=home",
        "https://example.com/other",
    ]
    
    unique = dedupe_urls(urls)
    
    # Should have 2 unique URLs
    assert len(unique) == 2
    assert "https://example.com/article" in unique or "https://example.com/article?utm_source=test" in unique
    assert "https://example.com/other" in unique

