from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded securely from environment variables / .env file."""

    SUPABASE_URL: str = Field(default="https://placeholder-project.supabase.co", description="Supabase project API URL")
    SUPABASE_KEY: str = Field(default="placeholder-anon-key", description="Supabase API key")
    SUPABASE_JWT_SECRET: str | None = Field(default=None, description="Supabase JWT secret for token verification")
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
