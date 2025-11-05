"""Sources API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.schemas import SourceResponse, SourceListResponse
from ..models import Source

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=SourceListResponse)
async def get_sources(
    db: Session = Depends(get_db)
):
    """Get list of configured sources."""
    sources = db.query(Source).order_by(Source.name).all()
    
    return SourceListResponse(
        items=[SourceResponse.from_orm(s) for s in sources]
    )

