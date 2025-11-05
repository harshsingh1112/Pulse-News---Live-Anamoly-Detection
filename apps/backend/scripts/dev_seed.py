"""Development seed script to generate synthetic data with controlled spikes."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.core.db import SessionLocal, init_db
from src.models import Article, Count, Anomaly
from src.utils.time import bucket_start, UTC
import random

# Topics
TOPICS = ["environment", "politics", "humanity"]
SOURCES = ["Reuters", "AP News", "BBC", "The Guardian", "Al Jazeera"]


def generate_articles(db: Session, start_time: datetime, hours: int = 48):
    """Generate synthetic articles over time period."""
    print(f"Generating articles for {hours} hours...")
    
    current = start_time
    article_id = 1
    
    while current < datetime.now(UTC):
        # Base rate: 5-15 articles per hour
        base_rate = random.randint(5, 15)
        
        # Create spikes at specific times
        hour_of_day = current.hour
        if hour_of_day in [8, 14, 20]:  # Spike times
            base_rate *= random.randint(3, 6)
        
        articles_per_hour = base_rate
        interval_seconds = 3600 / articles_per_hour
        
        hour_end = current + timedelta(hours=1)
        
        while current < hour_end and current < datetime.now(UTC):
            # Random topic
            topic = random.choice(TOPICS)
            source = random.choice(SOURCES)
            
            article = Article(
                source=source,
                source_type="rss",
                title=f"Breaking: {topic.title()} News Event #{article_id}",
                url=f"https://example.com/news/{article_id}",
                summary=f"Summary of {topic} news event",
                topic=topic,
                published_at_utc=current,
                fetched_at_utc=current,
                author=f"Author {article_id % 10}",
            )
            
            try:
                db.add(article)
                db.commit()
                article_id += 1
            except Exception:
                db.rollback()
                article_id += 1
            
            current += timedelta(seconds=interval_seconds)
    
    print(f"Generated {article_id - 1} articles")


def generate_counts(db: Session):
    """Aggregate counts from articles."""
    print("Generating count buckets...")
    
    # Get all articles
    articles = db.query(Article).order_by(Article.published_at_utc).all()
    
    # Group by 5-minute buckets
    buckets = {}
    for article in articles:
        bucket_dt = bucket_start(article.published_at_utc, 5)
        key = (bucket_dt, article.topic, article.source)
        
        if key not in buckets:
            buckets[key] = 0
        buckets[key] += 1
    
    # Insert counts
    from src.models import Count
    for (bucket_dt, topic, source), count in buckets.items():
        count_obj = Count(
            bucket_start_utc=bucket_dt,
            bucket_size="5m",
            topic=topic,
            source=source,
            count=count,
        )
        try:
            db.add(count_obj)
            db.commit()
        except Exception:
            db.rollback()
    
    # Aggregate buckets (source=None)
    aggregate_buckets = {}
    for (bucket_dt, topic, _), count in buckets.items():
        key = (bucket_dt, topic)
        if key not in aggregate_buckets:
            aggregate_buckets[key] = 0
        aggregate_buckets[key] += count
    
    for (bucket_dt, topic), count in aggregate_buckets.items():
        count_obj = Count(
            bucket_start_utc=bucket_dt,
            bucket_size="5m",
            topic=topic,
            source=None,
            count=count,
        )
        try:
            db.add(count_obj)
            db.commit()
        except Exception:
            db.rollback()
    
    print(f"Generated {len(buckets)} count buckets")


def main():
    """Main seed function."""
    print("Starting seed script...")
    
    # Initialize DB
    init_db()
    
    db = SessionLocal()
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Anomaly).delete()
        db.query(Count).delete()
        db.query(Article).delete()
        db.commit()
        
        # Generate data
        start_time = datetime.now(UTC) - timedelta(hours=48)
        generate_articles(db, start_time, hours=48)
        generate_counts(db)
        
        print("Seed complete!")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

