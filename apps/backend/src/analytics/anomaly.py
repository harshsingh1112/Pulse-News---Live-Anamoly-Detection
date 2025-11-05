"""Anomaly detection using MAD and Z-score."""

import logging
from typing import List, Tuple, Optional
import numpy as np
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from ..models import Count, Anomaly
from ..utils.time import bucket_size_to_minutes, now_utc
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def compute_baseline(series: List[int]) -> Tuple[float, float]:
    """Compute baseline (expected value) and MAD.
    
    Args:
        series: List of count values
    
    Returns:
        Tuple of (expected, mad)
    """
    if not series:
        return 0.0, 1.0
    
    if len(series) == 1:
        return float(series[0]), 1.0
    
    arr = np.array(series, dtype=float)
    median = np.median(arr)
    
    # Compute MAD (Median Absolute Deviation)
    deviations = np.abs(arr - median)
    mad = np.median(deviations)
    
    # Fallback to stddev if MAD is too small
    if mad < 0.1:
        stddev = np.std(arr)
        return float(median), float(stddev)
    
    return float(median), float(mad)


def is_anomaly(
    observed: int,
    expected: float,
    mad: float,
    threshold: float = 4.0
) -> Tuple[bool, float]:
    """Check if observed value is an anomaly.
    
    Args:
        observed: Observed count value
        expected: Expected baseline value
        mad: Median Absolute Deviation (or stddev fallback)
        threshold: Deviation threshold (default 4.0)
    
    Returns:
        Tuple of (is_anomaly, deviation_score)
    """
    if mad < 0.1:
        # Fallback to Z-score
        deviation = (observed - expected) / mad if mad > 0 else 0.0
        method = "zscore"
    else:
        # MAD-based deviation
        deviation = abs(observed - expected) / mad if mad > 0 else 0.0
        method = "mad"
    
    is_anom = deviation >= threshold
    return is_anom, deviation


def detect_anomalies(
    db: Session,
    bucket_size: str = "1m",
    topic: Optional[str] = None,
    window_buckets: int = 288,  # 24h for 5m buckets, 60 for 1m
    threshold: float = 4.0
) -> int:
    """Detect anomalies in time-series counts.
    
    Args:
        db: Database session
        bucket_size: Bucket size to analyze
        topic: Optional topic filter
        window_buckets: Number of historical buckets to use for baseline
        threshold: Deviation threshold
    
    Returns:
        Number of new anomalies detected
    """
    bucket_minutes = bucket_size_to_minutes(bucket_size)
    
    # Calculate time window
    now = now_utc()
    window_start = now - timedelta(minutes=bucket_minutes * window_buckets)
    
    # Get all topics if not specified
    if topic:
        topics = [topic]
    else:
        topics = db.query(Count.topic).distinct().all()
        topics = [t[0] for t in topics]
    
    new_anomalies = 0
    
    for topic_val in topics:
        # Get historical counts for this topic (aggregate, source=None)
        historical = db.query(Count).filter(
            and_(
                Count.bucket_size == bucket_size,
                Count.topic == topic_val,
                Count.source.is_(None),
                Count.bucket_start_utc >= window_start,
                Count.bucket_start_utc < now
            )
        ).order_by(Count.bucket_start_utc).all()
        
        if len(historical) < 10:  # Need at least 10 points
            continue
        
        # Extract counts as list
        counts = [c.count for c in historical]
        
        # Compute baseline from all historical data
        expected, mad = compute_baseline(counts)
        
        # Check the most recent bucket
        latest = historical[-1]
        
        # Skip if anomaly already exists
        existing = db.query(Anomaly).filter(
            and_(
                Anomaly.bucket_start_utc == latest.bucket_start_utc,
                Anomaly.bucket_size == bucket_size,
                Anomaly.topic == topic_val
            )
        ).first()
        
        if existing:
            continue
        
        # Check if anomaly
        is_anom, deviation = is_anomaly(
            latest.count,
            expected,
            mad,
            threshold
        )
        
        if is_anom:
            anomaly = Anomaly(
                bucket_start_utc=latest.bucket_start_utc,
                bucket_size=bucket_size,
                topic=topic_val,
                observed=latest.count,
                expected=expected,
                deviation=deviation,
                method="mad" if mad >= 0.1 else "zscore"
            )
            db.add(anomaly)
            new_anomalies += 1
            
            logger.info(
                f"Anomaly detected: {topic_val} at {latest.bucket_start_utc}, "
                f"observed={latest.count}, expected={expected:.1f}, deviation={deviation:.2f}"
            )
    
    try:
        db.commit()
        return new_anomalies
    except Exception as e:
        db.rollback()
        logger.error(f"Error detecting anomalies: {e}", exc_info=True)
        raise

