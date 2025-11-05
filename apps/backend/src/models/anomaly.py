"""Anomaly detection model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, String, Index
from sqlalchemy.dialects.postgresql import TIMESTAMP

from ..core.db import Base


class Anomaly(Base):
    """Anomaly detection result model."""
    
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    bucket_start_utc = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    bucket_size = Column(String(10), nullable=False)  # 1m, 5m, 60m
    topic = Column(String(50), nullable=False, index=True)
    observed = Column(Integer, nullable=False)
    expected = Column(Float, nullable=False)
    deviation = Column(Float, nullable=False)  # Z-score or MAD score
    method = Column(String(20), nullable=False)  # mad, zscore
    created_at_utc = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_anomalies_topic_created", "topic", "created_at_utc"),
        Index("idx_anomalies_bucket", "bucket_start_utc", "bucket_size", "topic"),
    )

