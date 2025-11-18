"""
Configuration module.

- Defines a Settings class that loads configuration from environment variables
  (and optionally from a .env file).
- Exposes a get_settings() helper that returns a cached Settings instance
  for use across the application.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, Field


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables / .env.

    Each attribute here maps to an environment variable. If the environment
    variable is not set, the default value defined here is used.
    """

    # --- General app settings ---

    APP_NAME: str = Field(
        default="Yaya AI Lab",
        description="Human-friendly name for the application.",
    )

    APP_ENV: str = Field(
        default="dev",
        description="Environment name: dev / staging / prod.",
    )

    DEBUG: bool = Field(
        default=True,
        description="If True, enable debug mode and more verbose logging.",
    )
    LOG_LVL: str = Field(
        default="DEBUG",
        description="logging level across the whole system",
    )
    # --- Deployment / proxy configuration ---

    ROOT_PATH: str = Field(
        default="",
        description="URL root path when running behind a reverse proxy (e.g. /proxy/8000).",
    )
    # --- Database configuration (primary source: POSTGRES_* variables) ---

    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5433)
    POSTGRES_USER: str = Field(default="yaya")
    POSTGRES_PASSWORD: str = Field(default="yaya_password")
    POSTGRES_DB: str = Field(default="yaya_ai_lab")

    # Optional full URL override (e.g. for managed DB in prod)
    DATABASE_URL: str | None = Field(
        default=None,
        description="Optional full DB URL. If not set, it is built from POSTGRES_*.",
    )

    # --- OpenRouter / LLM configuration ---

    OPENROUTER_API_KEY: str = Field(
        default="",
        description="API key for OpenRouter.",
        repr=False,  # do not show the key if Settings is printed
    )

    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API.",
    )

    OPENROUTER_MODEL: str = Field(
        default="openrouter/openai/gpt-4.1-mini",
        description="Default LLM model identifier to use via OpenRouter.",
    )

    # --- Storage configuration ---

    STORAGE_ROOT: str = Field(
        default="/data/storage",
        description="Root directory for document and dataset files.",
    )

    # --- Pydantic settings configuration ---

    # Pydantic v2-style configuration for BaseSettings
    model_config = SettingsConfigDict(
        env_file=".env",            # load variables from .env file if present
        env_file_encoding="utf-8",  # assume UTF-8 encoding for .env
        case_sensitive=True,        # environment variable names are case-sensitive
        extra="ignore",             # ignore unknown env vars instead of raising
    )
    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Return the SQLAlchemy database URL.

        Priority:
        1) If DATABASE_URL is set, use it as-is.
        2) Otherwise, build it from POSTGRES_* fields.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

@lru_cache
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    lru_cache ensures that Settings() is constructed only once per process.
    Subsequent calls return the same object, which is cheap and predictable.
    """
    return Settings()