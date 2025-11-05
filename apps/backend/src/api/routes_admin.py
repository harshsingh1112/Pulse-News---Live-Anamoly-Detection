"""Admin API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..ingest.pipeline import IngestionPipeline

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/run-ingest")
async def run_ingest():
    """Manually trigger ingestion cycle."""
    pipeline = IngestionPipeline()
    stats = await pipeline.run_cycle()
    return {"status": "success", "stats": stats}

