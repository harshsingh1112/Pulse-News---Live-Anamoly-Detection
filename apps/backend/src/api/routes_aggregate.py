"""Aggregate API routes."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..core.db import get_db
from ..core.schemas import AggregateResponse, CountResponse, Topic
from ..models import Count
from ..utils.time import parse_iso8601, bucket_size_to_minutes

router = APIRouter(prefix="/api/aggregate", tags=["aggregate"])


@router.get("", response_model=AggregateResponse)
async def get_aggregate(
    bucket_size: str = Query("5m", regex="^(1m|5m|60m)$"),
    topic: Optional[Topic] = Query(None),
    source: Optional[str] = Query(None),
    since: Optional[str] = Query(None, description="ISO8601 timestamp (UTC)"),
    db: Session = Depends(get_db)
):
    """Get time-series aggregate counts."""
    # Default to last 24 hours if since not provided
    if since:
        try:
            since_dt = parse_iso8601(since)
        except Exception:
            since_dt = datetime.utcnow() - timedelta(hours=24)
    else:
        bucket_minutes = bucket_size_to_minutes(bucket_size)
        # Default to last 24 hours worth of buckets
        since_dt = datetime.utcnow() - timedelta(minutes=bucket_minutes * 288)
    
    query = db.query(Count).filter(
        and_(
            Count.bucket_size == bucket_size,
            Count.bucket_start_utc >= since_dt
        )
    )
    
    if topic:
        query = query.filter(Count.topic == topic)
    
    if source:
        query = query.filter(Count.source == source)
    else:
        # Default to aggregate (source='' for SQLite compatibility)
        query = query.filter(
            (Count.source == "") | (Count.source.is_(None))
        )
    
    counts = query.order_by(Count.bucket_start_utc).all()
    
    return AggregateResponse(
        buckets=[CountResponse(
            bucket_start_utc=c.bucket_start_utc,
            bucket_size=c.bucket_size,
            topic=c.topic,
            source=c.source,
            count=c.count
        ) for c in counts],
        bucket_size=bucket_size,
        topic=topic,
        source=source
    )

