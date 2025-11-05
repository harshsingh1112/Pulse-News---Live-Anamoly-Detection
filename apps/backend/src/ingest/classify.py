"""Topic classification based on keywords and source hints."""

import json
import os
from pathlib import Path
from typing import Optional, Literal
import re

Topic = Literal["environment", "politics", "humanity"]


class TopicClassifier:
    """Classify articles into topics using keyword matching."""
    
    def __init__(self, rules_path: Optional[str] = None):
        """Initialize classifier with rules."""
        if rules_path is None:
            # Default to config/topic_rules.json
            rules_path = Path(__file__).parent.parent.parent / "config" / "topic_rules.json"
        
        with open(rules_path, "r") as f:
            self.rules = json.load(f)
        
        # Precompile regex patterns for performance
        self.patterns = {}
        for topic, config in self.rules.items():
            keywords = config.get("keywords", [])
            phrases = config.get("phrases", [])
            
            # Create case-insensitive patterns
            all_patterns = keywords + phrases
            pattern_str = "|".join([re.escape(p) for p in all_patterns])
            self.patterns[topic] = re.compile(pattern_str, re.IGNORECASE)
    
    def classify(
        self,
        title: str,
        summary: Optional[str] = None,
        source_topic: Optional[str] = None
    ) -> Optional[Topic]:
        """Classify article into topic.
        
        Args:
            title: Article title
            summary: Optional article summary
            source_topic: Optional topic hint from source configuration
            
        Returns:
            Topic or None if no match
        """
        # If source has a topic hint, use it
        if source_topic and source_topic in ["environment", "politics", "humanity"]:
            return source_topic
        
        # Combine title and summary for matching
        text = title
        if summary:
            text += " " + summary
        
        text = text.lower()
        
        # Score each topic
        scores = {}
        for topic in ["environment", "politics", "humanity"]:
            matches = len(self.patterns[topic].findall(text))
            if matches > 0:
                scores[topic] = matches
        
        if not scores:
            return None
        
        # Return topic with highest score
        return max(scores.items(), key=lambda x: x[1])[0]  # type: ignore

