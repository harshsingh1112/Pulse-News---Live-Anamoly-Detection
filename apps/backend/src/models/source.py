"""Source configuration model."""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import TEXT

from ..core.db import Base


class Source(Base):
    """Source configuration model."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # rss, reddit_sub, reddit_user
    url_or_id = Column(TEXT, nullable=False, unique=True)
    topic = Column(String(50), nullable=True)  # environment, politics, humanity, or NULL
    enabled = Column(Boolean, nullable=False, default=True, index=True)

