"""Anomalies API routes."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..core.db import get_db
from ..core.schemas import AnomalyResponse, AnomalyListResponse, Topic
from ..models import Anomaly

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("", response_model=AnomalyListResponse)
async def get_anomalies(
    topic: Optional[Topic] = Query(None),
    since: Optional[str] = Query(None, description="ISO8601 timestamp (UTC)"),
    bucket_size: Optional[str] = Query(None, regex="^(1m|5m|60m)$"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get detected anomalies."""
    query = db.query(Anomaly)
    
    if topic:
        query = query.filter(Anomaly.topic == topic)
    
    if bucket_size:
        query = query.filter(Anomaly.bucket_size == bucket_size)
    
    if since:
        try:
            since_dt = parse_iso8601(since)
            query = query.filter(Anomaly.created_at_utc >= since_dt)
        except Exception:
            pass
    else:
        # Default to last 7 days
        since_dt = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Anomaly.created_at_utc >= since_dt)
    
    total = query.count()
    
    anomalies = query.order_by(desc(Anomaly.created_at_utc)).limit(limit).all()
    
    return AnomalyListResponse(
        items=[AnomalyResponse.from_orm(a) for a in anomalies],
        total=total
    )

