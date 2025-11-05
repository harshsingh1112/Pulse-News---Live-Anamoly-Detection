"""Tests for topic classification."""

import pytest
from src.ingest.classify import TopicClassifier


def test_classify_environment():
    """Test environment classification."""
    classifier = TopicClassifier()
    
    topic = classifier.classify(
        title="Climate change threatens global ecosystems",
        summary="Rising temperatures and extreme weather events"
    )
    
    assert topic == "environment"


def test_classify_politics():
    """Test politics classification."""
    classifier = TopicClassifier()
    
    topic = classifier.classify(
        title="Election results show major shift",
        summary="New government formed after democratic vote"
    )
    
    assert topic == "politics"


def test_classify_humanity():
    """Test humanity classification."""
    classifier = TopicClassifier()
    
    topic = classifier.classify(
        title="Refugee crisis escalates in region",
        summary="Humanitarian aid needed for displaced families"
    )
    
    assert topic == "humanity"


def test_classify_source_hint():
    """Test source topic hint."""
    classifier = TopicClassifier()
    
    topic = classifier.classify(
        title="Generic news article",
        summary="Some content",
        source_topic="environment"
    )
    
    assert topic == "environment"

