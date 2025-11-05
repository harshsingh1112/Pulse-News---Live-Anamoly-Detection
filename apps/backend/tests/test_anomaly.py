"""Tests for anomaly detection."""

import pytest
from src.analytics.anomaly import compute_baseline, is_anomaly


def test_compute_baseline():
    """Test baseline computation."""
    series = [10, 12, 11, 13, 10, 14, 11, 12, 10, 11]
    expected, mad = compute_baseline(series)
    
    assert expected > 0
    assert mad > 0
    assert isinstance(expected, float)
    assert isinstance(mad, float)


def test_compute_baseline_single_value():
    """Test baseline with single value."""
    series = [10]
    expected, mad = compute_baseline(series)
    
    assert expected == 10.0
    assert mad == 1.0


def test_is_anomaly():
    """Test anomaly detection."""
    # Normal case
    is_anom, score = is_anomaly(observed=12, expected=10, mad=2.0, threshold=4.0)
    assert not is_anom
    assert score < 4.0
    
    # Anomaly case
    is_anom, score = is_anomaly(observed=30, expected=10, mad=2.0, threshold=4.0)
    assert is_anom
    assert score >= 4.0


def test_is_anomaly_edge_cases():
    """Test edge cases."""
    # Zero MAD
    is_anom, score = is_anomaly(observed=10, expected=10, mad=0.0, threshold=4.0)
    assert not is_anom
    
    # Negative deviation
    is_anom, score = is_anomaly(observed=5, expected=10, mad=2.0, threshold=4.0)
    assert not is_anom  # Should use absolute value

