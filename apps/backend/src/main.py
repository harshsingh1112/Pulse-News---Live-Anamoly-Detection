"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .core.config import get_settings
from .core.logging import setup_logging
from .core.db import init_db
from .api import (
    news_router,
    aggregate_router,
    anomalies_router,
    sources_router,
    stream_router,
    admin_router,
)
from .ingest.pipeline import IngestionPipeline

settings = get_settings()
setup_logging(settings.log_level)

logger = logging.getLogger(__name__)

# Global scheduler
scheduler: AsyncIOScheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global scheduler
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Load sources from YAML if needed
    from .models import Source
    from sqlalchemy.orm import Session
    from .core.db import SessionLocal
    import yaml
    from pathlib import Path
    
    db = SessionLocal()
    try:
        existing = db.query(Source).count()
        if existing == 0:
            # Load from config
            sources_path = Path(__file__).parent.parent / "config" / "sources.yaml"
            if sources_path.exists():
                with open(sources_path, "r") as f:
                    sources_data = yaml.safe_load(f)
                    for source_data in sources_data:
                        source = Source(**source_data)
                        db.add(source)
                    db.commit()
                    logger.info(f"Loaded {len(sources_data)} sources from config")
    finally:
        db.close()
    
    # Start scheduler if enabled
    if settings.enable_scheduler:
        logger.info("Starting scheduler...")
        scheduler = AsyncIOScheduler()
        
        pipeline = IngestionPipeline()
        
        async def run_ingest():
            try:
                await pipeline.run_cycle()
            except Exception as e:
                logger.error(f"Scheduled ingestion error: {e}", exc_info=True)
        
        scheduler.add_job(
            run_ingest,
            trigger=IntervalTrigger(seconds=settings.ingest_min_interval_seconds),
            id="ingest_job",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Scheduler started")
    
    yield
    
    # Shutdown
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


app = FastAPI(
    title="Breaking News Anomaly Detection API",
    description="API for aggregating and detecting anomalies in breaking news",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(news_router)
app.include_router(aggregate_router)
app.include_router(anomalies_router)
app.include_router(sources_router)
app.include_router(stream_router)
app.include_router(admin_router)


@app.get("/healthz")
async def health():
    """Health check endpoint."""
    from .models import Article
    from .core.db import SessionLocal
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # Get last article fetch time
        last_article = db.query(func.max(Article.fetched_at_utc)).scalar()
        return {
            "status": "healthy",
            "version": "1.0.0",
            "last_ingest_utc": last_article.isoformat() if last_article else None,
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

