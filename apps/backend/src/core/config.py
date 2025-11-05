"""Configuration management using Pydantic settings."""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql+psycopg2://pulsewatch:pulsewatch@localhost:5432/pulsewatch"
    
    # Reddit
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "pulsewatch/1.0"
    
    # CORS
    allowed_origins: str = "http://localhost:3000"
    
    # Ingestion
    ingest_min_interval_seconds: int = 60
    default_timezone: str = "Asia/Kolkata"
    
    # Experimental
    enable_experimental_scrape: bool = False
    enable_scheduler: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

