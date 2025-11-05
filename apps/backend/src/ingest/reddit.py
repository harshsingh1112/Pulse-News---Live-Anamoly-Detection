"""Reddit ingestion."""

import logging
from datetime import datetime
from typing import List, Optional
import praw
from sqlalchemy.orm import Session

from ..models import Article, Source
from ..core.config import get_settings
from ..utils.time import now_utc, UTC
from ..utils.dedupe import normalize_url
from .classify import TopicClassifier

logger = logging.getLogger(__name__)


class RedditIngester:
    """Reddit ingester using PRAW."""
    
    def __init__(self, classifier: TopicClassifier):
        """Initialize Reddit ingester."""
        self.classifier = classifier
        settings = get_settings()
        
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            logger.warning("Reddit credentials not configured")
            self.reddit = None
        else:
            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent,
            )
    
    def parse_submission(
        self,
        submission: praw.models.Submission,
        source: Source,
        fetched_at: datetime
    ) -> Optional[Article]:
        """Parse Reddit submission into Article model."""
        try:
            title = submission.title.strip()
            if not title:
                return None
            
            # Use permalink as URL
            url = f"https://reddit.com{submission.permalink}"
            url = normalize_url(url)
            
            # Get selftext as summary
            summary = submission.selftext[:500] if submission.selftext else None
            
            # Parse created_utc
            published_at = datetime.fromtimestamp(submission.created_utc, tz=UTC)
            
            # Classify topic
            topic = self.classifier.classify(
                title=title,
                summary=summary,
                source_topic=source.topic
            ) or "politics"  # Default fallback
            
            # Create article
            article = Article(
                source=source.name,
                source_type="reddit_sub" if source.type == "reddit_sub" else "reddit_user",
                title=title,
                url=url,
                summary=summary,
                topic=topic,
                published_at_utc=published_at,
                fetched_at_utc=fetched_at,
                author=submission.author.name if submission.author else None,
                score=submission.score,
                raw={
                    "subreddit": submission.subreddit.display_name,
                    "num_comments": submission.num_comments,
                    "upvote_ratio": submission.upvote_ratio,
                }
            )
            
            return article
        except Exception as e:
            logger.error(f"Error parsing submission: {e}", exc_info=True)
            return None
    
    def ingest_subreddit(
        self,
        db: Session,
        source: Source,
        limit: int = 25
    ) -> int:
        """Ingest from a subreddit.
        
        Returns:
            Number of new articles inserted
        """
        if not self.reddit or source.type != "reddit_sub":
            return 0
        
        try:
            subreddit_name = source.url_or_id
            subreddit = self.reddit.subreddit(subreddit_name)
            
            fetched_at = now_utc()
            new_count = 0
            
            # Fetch hot and new posts
            for submission in subreddit.hot(limit=limit):
                article = self.parse_submission(submission, source, fetched_at)
                if not article:
                    continue
                
                try:
                    db.add(article)
                    db.commit()
                    new_count += 1
                except Exception as e:
                    db.rollback()
                    if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                        continue
                    logger.error(f"Error inserting article: {e}")
            
            logger.info(f"Ingested {new_count} new articles from r/{subreddit_name}")
            return new_count
        except Exception as e:
            logger.error(f"Error ingesting subreddit {source.name}: {e}", exc_info=True)
            return 0
    
    def ingest_user(
        self,
        db: Session,
        source: Source,
        limit: int = 10
    ) -> int:
        """Ingest from a Reddit user (recent posts/comments).
        
        Returns:
            Number of new articles inserted
        """
        if not self.reddit or source.type != "reddit_user":
            return 0
        
        try:
            username = source.url_or_id
            redditor = self.reddit.redditor(username)
            
            fetched_at = now_utc()
            new_count = 0
            
            # Fetch recent submissions
            for submission in redditor.submissions.new(limit=limit):
                article = self.parse_submission(submission, source, fetched_at)
                if not article:
                    continue
                
                try:
                    db.add(article)
                    db.commit()
                    new_count += 1
                except Exception as e:
                    db.rollback()
                    if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                        continue
                    logger.error(f"Error inserting article: {e}")
            
            logger.info(f"Ingested {new_count} new articles from u/{username}")
            return new_count
        except Exception as e:
            logger.error(f"Error ingesting user {source.name}: {e}", exc_info=True)
            return 0

