"""API routes package."""

from .routes_news import router as news_router
from .routes_aggregate import router as aggregate_router
from .routes_anomalies import router as anomalies_router
from .routes_sources import router as sources_router
from .routes_stream import router as stream_router
from .routes_admin import router as admin_router

__all__ = [
    "news_router",
    "aggregate_router",
    "anomalies_router",
    "sources_router",
    "stream_router",
    "admin_router",
]

