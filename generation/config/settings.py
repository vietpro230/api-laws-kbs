"""Settings management"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    # API settings
    GOOGLE_API_KEY: str

    # Model settings
    DEFAULT_MODEL: str = "gemini-pro"

    class Config:
        env_file = ".env"