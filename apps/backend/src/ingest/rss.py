"""RSS feed ingestion."""

import logging
from datetime import datetime
from typing import List, Optional
import aiohttp
import feedparser
from sqlalchemy.orm import Session

from ..models import Article, Source
from ..utils.time import now_utc, UTC
from ..utils.dedupe import normalize_url
from .classify import TopicClassifier

logger = logging.getLogger(__name__)


class RSSIngester:
    """RSS feed ingester."""
    
    def __init__(self, classifier: TopicClassifier):
        """Initialize RSS ingester."""
        self.classifier = classifier
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse RSS feed."""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: status {response.status}")
                    return None
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                if feed.bozo:
                    logger.warning(f"Feed parse error for {url}: {feed.bozo_exception}")
                
                return feed
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {e}", exc_info=True)
            return None
    
    def parse_entry(
        self,
        entry: feedparser.FeedParserDict,
        source: Source,
        fetched_at: datetime
    ) -> Optional[Article]:
        """Parse feed entry into Article model."""
        try:
            # Extract fields
            title = entry.get("title", "").strip()
            if not title:
                return None
            
            url = entry.get("link", "").strip()
            if not url:
                return None
            
            # Normalize URL
            url = normalize_url(url)
            
            # Get summary/description
            summary = None
            if "summary" in entry:
                summary = entry.get("summary", "").strip()
            elif "description" in entry:
                summary = entry.get("description", "").strip()
            
            # Parse published date
            published_at = fetched_at  # Default to now
            if "published_parsed" in entry and entry.published_parsed:
                try:
                    import time
                    published_at = datetime.fromtimestamp(
                        time.mktime(entry.published_parsed),
                        tz=UTC
                    )
                except Exception:
                    pass
            elif "updated_parsed" in entry and entry.updated_parsed:
                try:
                    import time
                    published_at = datetime.fromtimestamp(
                        time.mktime(entry.updated_parsed),
                        tz=UTC
                    )
                except Exception:
                    pass
            
            # Classify topic
            topic = self.classifier.classify(
                title=title,
                summary=summary,
                source_topic=source.topic
            ) or "politics"  # Default fallback
            
            # Get author
            author = None
            if "author" in entry:
                author = entry.author
            elif "author_detail" in entry:
                author = entry.author_detail.get("name")
            
            # Create article
            article = Article(
                source=source.name,
                source_type="rss",
                title=title,
                url=url,
                summary=summary,
                topic=topic,
                published_at_utc=published_at,
                fetched_at_utc=fetched_at,
                author=author,
                raw={"feed_title": entry.get("title"), "feed_tags": [tag.get("term") for tag in entry.get("tags", [])]}
            )
            
            return article
        except Exception as e:
            logger.error(f"Error parsing entry: {e}", exc_info=True)
            return None
    
    async def ingest_source(
        self,
        db: Session,
        source: Source
    ) -> int:
        """Ingest articles from a single RSS source.
        
        Returns:
            Number of new articles inserted
        """
        if source.type != "rss":
            return 0
        
        fetched_at = now_utc()
        feed = await self.fetch_feed(source.url_or_id)
        
        if not feed or not feed.entries:
            logger.warning(f"No entries found in feed: {source.name}")
            return 0
        
        new_count = 0
        for entry in feed.entries:
            article = self.parse_entry(entry, source, fetched_at)
            if not article:
                continue
            
            # Try to insert (ignore duplicates)
            try:
                db.add(article)
                db.commit()
                new_count += 1
            except Exception as e:
                db.rollback()
                # Check if it's a duplicate URL error
                if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                    continue
                logger.error(f"Error inserting article: {e}")
        
        logger.info(f"Ingested {new_count} new articles from {source.name}")
        return new_count

