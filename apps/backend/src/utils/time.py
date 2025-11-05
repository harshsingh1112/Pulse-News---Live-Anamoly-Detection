"""Time utility functions."""

from datetime import datetime, timedelta
from typing import Optional
import pytz


UTC = pytz.UTC


def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def parse_iso8601(iso_str: str) -> datetime:
    """Parse ISO8601 string to UTC datetime."""
    iso_str = iso_str.replace("Z", "+00:00")
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    return dt


def to_ist(utc_dt: datetime) -> datetime:
    """Convert UTC datetime to IST."""
    if utc_dt.tzinfo is None:
        utc_dt = UTC.localize(utc_dt)
    ist = pytz.timezone("Asia/Kolkata")
    return utc_dt.astimezone(ist)


def bucket_start(dt: datetime, bucket_minutes: int) -> datetime:
    """Get bucket start time for a given datetime."""
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    
    # Round down to bucket boundary
    minutes = dt.minute - (dt.minute % bucket_minutes)
    return dt.replace(minute=minutes, second=0, microsecond=0)


def bucket_size_to_minutes(bucket_size: str) -> int:
    """Convert bucket size string to minutes."""
    if bucket_size.endswith("m"):
        return int(bucket_size[:-1])
    elif bucket_size.endswith("h"):
        return int(bucket_size[:-1]) * 60
    else:
        raise ValueError(f"Invalid bucket size: {bucket_size}")


def minutes_to_bucket_size(minutes: int) -> str:
    """Convert minutes to bucket size string."""
    if minutes < 60:
        return f"{minutes}m"
    else:
        return f"{minutes // 60}h"

