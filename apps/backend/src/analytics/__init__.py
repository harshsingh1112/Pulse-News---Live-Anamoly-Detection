"""Analytics package."""

from .bucket import aggregate_counts
from .anomaly import detect_anomalies, compute_baseline, is_anomaly

__all__ = ["aggregate_counts", "detect_anomalies", "compute_baseline", "is_anomaly"]

