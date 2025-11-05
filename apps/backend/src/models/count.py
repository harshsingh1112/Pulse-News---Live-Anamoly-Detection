"""Count aggregation model."""

from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.dialects.postgresql import TIMESTAMP

from ..core.db import Base


class Count(Base):
    """Count bucket model for time-series aggregation."""
    
    __tablename__ = "counts"
    
    bucket_start_utc = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    bucket_size = Column(String(10), primary_key=True, nullable=False)  # 1m, 5m, 60m
    topic = Column(String(50), primary_key=True, nullable=False, index=True)
    source = Column(String(255), primary_key=True, nullable=True, default="")  # Empty string for aggregate
    count = Column(Integer, nullable=False, default=0)
    
    __table_args__ = (
        Index("idx_counts_topic_bucket", "topic", "bucket_start_utc", "bucket_size"),
        Index("idx_counts_source_bucket", "source", "bucket_start_utc", "bucket_size"),
    )

