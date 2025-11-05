"""Ingestion package."""

from .pipeline import IngestionPipeline
from .classify import TopicClassifier

__all__ = ["IngestionPipeline", "TopicClassifier"]

