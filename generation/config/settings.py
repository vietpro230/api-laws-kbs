from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(".env")
class Settings(BaseSettings):
    APP_NAME: str = "law_KBS"
    LOG_FILE: str | None = None
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    GOOGLE_API_KEY: str | None = Field(None, env="GOOGLE_API_KEY")


# singleton settings instance
settings = Settings()