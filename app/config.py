"""
Configuration management for the Unit Converter API
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    API_TITLE: str = "Unit Converter API"
    API_VERSION: str = "1.1.0"
    API_DESCRIPTION: str = "REST API for unit conversions"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # External API
    CURRENCY_API_URL: str = "https://api.exchangerate-api.com/v4/latest"
    CURRENCY_API_TIMEOUT: int = 5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()