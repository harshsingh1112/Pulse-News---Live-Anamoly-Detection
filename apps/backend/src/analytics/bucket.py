"""Time-series bucket aggregation."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from ..models import Article, Count
from ..utils.time import bucket_start, bucket_size_to_minutes, now_utc, UTC

logger = logging.getLogger(__name__)


def aggregate_counts(
    db: Session,
    bucket_size: str = "1m",
    since: Optional[datetime] = None
) -> int:
    """Aggregate article counts into time buckets.
    
    Args:
        db: Database session
        bucket_size: Bucket size string (1m, 5m, 60m)
        since: Only aggregate articles since this time (default: last hour)
    
    Returns:
        Number of buckets created/updated
    """
    bucket_minutes = bucket_size_to_minutes(bucket_size)
    
    # Default to last hour if since not specified
    if since is None:
        since = now_utc() - timedelta(hours=1)
    
    # Query articles since the given time
    articles = db.query(Article).filter(
        Article.published_at_utc >= since
    ).all()
    
    if not articles:
        return 0
    
    # Group by bucket, topic, and source
    buckets = {}
    for article in articles:
        bucket_dt = bucket_start(article.published_at_utc, bucket_minutes)
        key = (bucket_dt, article.topic, article.source)
        
        if key not in buckets:
            buckets[key] = 0
        buckets[key] += 1
    
    # Insert or update counts
    created = 0
    for (bucket_dt, topic, source), count in buckets.items():
        # Check if exists
        existing = db.query(Count).filter(
            and_(
                Count.bucket_start_utc == bucket_dt,
                Count.bucket_size == bucket_size,
                Count.topic == topic,
                Count.source == (source or "")
            )
        ).first()
        
        if existing:
            existing.count = count
        else:
            count_obj = Count(
                bucket_start_utc=bucket_dt,
                bucket_size=bucket_size,
                topic=topic,
                source=source or "",
                count=count
            )
            db.add(count_obj)
            created += 1
    
    # Also create aggregate buckets (source=None)
    aggregate_buckets = {}
    for (bucket_dt, topic, _), count in buckets.items():
        key = (bucket_dt, topic)
        if key not in aggregate_buckets:
            aggregate_buckets[key] = 0
        aggregate_buckets[key] += count
    
    for (bucket_dt, topic), count in aggregate_buckets.items():
        existing = db.query(Count).filter(
            and_(
                Count.bucket_start_utc == bucket_dt,
                Count.bucket_size == bucket_size,
                Count.topic == topic,
                Count.source.is_(None)
            )
        ).first()
        
        if existing:
            existing.count = count
        else:
            count_obj = Count(
                bucket_start_utc=bucket_dt,
                bucket_size=bucket_size,
                topic=topic,
                source="",  # Use empty string instead of None for SQLite compatibility
                count=count
            )
            db.add(count_obj)
    
    try:
        db.commit()
        logger.info(f"Created/updated {created} count buckets for {bucket_size}")
        return created
    except Exception as e:
        db.rollback()
        logger.error(f"Error aggregating counts: {e}", exc_info=True)
        raise

