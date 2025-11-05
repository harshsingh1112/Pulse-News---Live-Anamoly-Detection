"""Article model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB

from ..core.db import Base


class Article(Base):
    """Article model."""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # rss, reddit_sub, reddit_user
    title = Column(Text, nullable=False)
    url = Column(String(2048), unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    topic = Column(String(50), nullable=False, index=True)  # environment, politics, humanity
    published_at_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    fetched_at_utc = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    author = Column(String(255), nullable=True)
    score = Column(Integer, nullable=True)  # Reddit score
    raw = Column(JSON, nullable=True)  # Original data (JSON for SQLite, JSONB for PostgreSQL - handled by engine)
    
    __table_args__ = (
        Index("idx_articles_topic_published", "topic", "published_at_utc"),
        Index("idx_articles_source_published", "source", "published_at_utc"),
    )

