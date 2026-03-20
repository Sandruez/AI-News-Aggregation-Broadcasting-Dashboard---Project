from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/ainews"

    # Groq LLM
    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Email broadcast (SMTP)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""

    # LinkedIn (OAuth token)
    linkedin_access_token: str = ""

    # WhatsApp (Twilio or similar)
    whatsapp_api_url: str = ""
    whatsapp_api_key: str = ""

    # Fetcher
    fetch_interval_minutes: int = 15
    max_items_per_source: int = 50

    # Production settings
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
