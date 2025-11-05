"""Pydantic schemas for API requests/responses."""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, HttpUrl, Field


# Topic enum
Topic = Literal["environment", "politics", "humanity"]


# Source type enum
SourceType = Literal["rss", "reddit_sub", "reddit_user"]


class ArticleResponse(BaseModel):
    """Article response schema."""
    id: int
    source: str
    source_type: str
    title: str
    url: str
    summary: Optional[str] = None
    topic: str
    published_at_utc: datetime
    fetched_at_utc: datetime
    author: Optional[str] = None
    score: Optional[int] = None
    raw: Optional[dict] = None
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Paginated article list response."""
    items: List[ArticleResponse]
    total: int
    limit: int
    offset: int


class CountResponse(BaseModel):
    """Count bucket response."""
    bucket_start_utc: datetime
    bucket_size: str
    topic: str
    source: Optional[str] = None
    count: int


class AggregateResponse(BaseModel):
    """Aggregate time-series response."""
    buckets: List[CountResponse]
    bucket_size: str
    topic: Optional[str] = None
    source: Optional[str] = None


class AnomalyResponse(BaseModel):
    """Anomaly response schema."""
    id: int
    bucket_start_utc: datetime
    bucket_size: str
    topic: str
    observed: int
    expected: float
    deviation: float
    method: str
    created_at_utc: datetime
    
    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    """Anomaly list response."""
    items: List[AnomalyResponse]
    total: int


class SourceResponse(BaseModel):
    """Source response schema."""
    id: int
    name: str
    type: str
    url_or_id: str
    topic: Optional[str] = None
    enabled: bool
    
    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    """Source list response."""
    items: List[SourceResponse]


class StreamEvent(BaseModel):
    """SSE event schema."""
    type: Literal["count", "anomaly", "article"]
    payload: dict


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    last_ingest_utc: Optional[datetime] = None

