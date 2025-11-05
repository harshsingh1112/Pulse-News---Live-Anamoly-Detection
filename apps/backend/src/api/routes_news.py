"""News API routes."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..core.db import get_db
from ..core.schemas import ArticleResponse, ArticleListResponse, Topic
from ..models import Article
from ..utils.time import parse_iso8601, UTC

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("", response_model=ArticleListResponse)
async def get_news(
    topic: Optional[Topic] = Query(None, description="Filter by topic"),
    source: Optional[str] = Query(None, description="Filter by source name"),
    since: Optional[str] = Query(None, description="ISO8601 timestamp (UTC)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get latest news articles."""
    query = db.query(Article)
    
    if topic:
        query = query.filter(Article.topic == topic)
    
    if source:
        query = query.filter(Article.source == source)
    
    if since:
        try:
            since_dt = parse_iso8601(since)
            query = query.filter(Article.published_at_utc >= since_dt)
        except Exception:
            pass
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    articles = query.order_by(desc(Article.published_at_utc)).offset(offset).limit(limit).all()
    
    return ArticleListResponse(
        items=[ArticleResponse.from_orm(a) for a in articles],
        total=total,
        limit=limit,
        offset=offset
    )

