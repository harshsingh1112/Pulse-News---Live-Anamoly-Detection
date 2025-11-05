"""SSE stream API route."""

import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from datetime import datetime

from ..core.schemas import StreamEvent

router = APIRouter(prefix="/api/stream", tags=["stream"])

# In-memory queue for SSE events (in production, use Redis or similar)
_event_queue: asyncio.Queue = asyncio.Queue()


def publish_event(event_type: str, payload: dict) -> None:
    """Publish event to SSE stream."""
    try:
        event = StreamEvent(type=event_type, payload=payload)
        _event_queue.put_nowait(event)
    except Exception:
        pass  # Queue full, drop event


async def event_generator() -> AsyncGenerator[str, None]:
    """Generate SSE events."""
    while True:
        try:
            # Wait for event with timeout
            event = await asyncio.wait_for(_event_queue.get(), timeout=30.0)
            
            # Format as SSE
            data = json.dumps(event.dict())
            yield f"data: {data}\n\n"
        except asyncio.TimeoutError:
            # Send heartbeat
            yield ": heartbeat\n\n"
        except Exception as e:
            break


@router.get("")
async def stream_events():
    """Server-Sent Events stream for live updates."""
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

