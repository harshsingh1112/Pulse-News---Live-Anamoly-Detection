"""Ingestion pipeline orchestration."""

import logging
import asyncio
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from ..models import Source
from ..core.db import SessionLocal
from ..analytics.bucket import aggregate_counts
from ..analytics.anomaly import detect_anomalies
from .rss import RSSIngester
from .reddit import RedditIngester
from .classify import TopicClassifier

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Main ingestion pipeline."""
    
    def __init__(self):
        """Initialize pipeline."""
        self.classifier = TopicClassifier()
        self.last_ingest_utc: Optional[datetime] = None
    
    async def run_cycle(self) -> dict:
        """Run one ingestion cycle.
        
        Returns:
            Dict with stats about the cycle
        """
        db = next(SessionLocal())
        stats = {
            "rss_count": 0,
            "reddit_count": 0,
            "total_new": 0,
            "errors": []
        }
        
        try:
            # Fetch enabled sources
            sources = db.query(Source).filter(Source.enabled == True).all()
            
            if not sources:
                logger.warning("No enabled sources found")
                return stats
            
            # Separate RSS and Reddit sources
            rss_sources = [s for s in sources if s.type == "rss"]
            reddit_sources = [s for s in sources if s.type in ["reddit_sub", "reddit_user"]]
            
            # Ingest RSS feeds (parallel)
            async with RSSIngester(self.classifier) as rss_ingester:
                rss_tasks = [
                    rss_ingester.ingest_source(db, source)
                    for source in rss_sources
                ]
                rss_results = await asyncio.gather(*rss_tasks, return_exceptions=True)
                
                for result in rss_results:
                    if isinstance(result, Exception):
                        logger.error(f"RSS ingestion error: {result}", exc_info=result)
                        stats["errors"].append(str(result))
                    else:
                        stats["rss_count"] += result
                        stats["total_new"] += result
            
            # Ingest Reddit (sequential to avoid rate limits)
            reddit_ingester = RedditIngester(self.classifier)
            for source in reddit_sources:
                try:
                    if source.type == "reddit_sub":
                        count = reddit_ingester.ingest_subreddit(db, source)
                    else:  # reddit_user
                        count = reddit_ingester.ingest_user(db, source)
                    
                    stats["reddit_count"] += count
                    stats["total_new"] += count
                except Exception as e:
                    logger.error(f"Reddit ingestion error for {source.name}: {e}", exc_info=True)
                    stats["errors"].append(f"{source.name}: {str(e)}")
            
            # Aggregate counts
            try:
                aggregate_counts(db, bucket_size="1m")
                logger.info("Aggregated counts for 1m buckets")
            except Exception as e:
                logger.error(f"Error aggregating counts: {e}", exc_info=True)
                stats["errors"].append(f"aggregation: {str(e)}")
            
            # Detect anomalies
            try:
                anomaly_count = detect_anomalies(db, bucket_size="1m")
                logger.info(f"Detected {anomaly_count} new anomalies")
                stats["anomalies_detected"] = anomaly_count
                
                # Publish anomaly events (avoid circular import)
                if anomaly_count > 0:
                    try:
                        from ..api.routes_stream import publish_event
                        from ..models import Anomaly
                        recent_anomalies = db.query(Anomaly).order_by(
                            Anomaly.created_at_utc.desc()
                        ).limit(anomaly_count).all()
                        for anomaly in recent_anomalies:
                            publish_event("anomaly", {
                                "id": anomaly.id,
                                "topic": anomaly.topic,
                                "bucket_start_utc": anomaly.bucket_start_utc.isoformat(),
                                "observed": anomaly.observed,
                                "expected": anomaly.expected,
                                "deviation": anomaly.deviation,
                            })
                    except ImportError:
                        pass  # Skip if circular import
            except Exception as e:
                logger.error(f"Error detecting anomalies: {e}", exc_info=True)
                stats["errors"].append(f"anomaly_detection: {str(e)}")
            
            # Publish article events for new articles (avoid circular import)
            if stats["total_new"] > 0:
                try:
                    from ..api.routes_stream import publish_event
                    from ..models import Article
                    recent_articles = db.query(Article).order_by(
                        Article.fetched_at_utc.desc()
                    ).limit(min(10, stats["total_new"])).all()
                    for article in recent_articles:
                        publish_event("article", {
                            "id": article.id,
                            "title": article.title,
                            "source": article.source,
                            "topic": article.topic,
                            "url": article.url,
                            "published_at_utc": article.published_at_utc.isoformat(),
                        })
                except ImportError:
                    pass  # Skip if circular import
            
            self.last_ingest_utc = datetime.utcnow()
            logger.info(f"Ingestion cycle complete: {stats}")
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            stats["errors"].append(f"pipeline: {str(e)}")
        finally:
            db.close()
        
        return stats

