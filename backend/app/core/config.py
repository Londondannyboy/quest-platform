"""
Quest Platform v2.2 - Configuration Management
Pydantic Settings for environment variables
"""

from decimal import Decimal
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================================================
    # APPLICATION
    # ========================================================================
    APP_ENV: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_PORT: int = Field(default=8000, description="API server port")
    WORKER_PORT: int = Field(default=8001, description="Worker server port")

    # ========================================================================
    # DATABASE (Neon PostgreSQL)
    # ========================================================================
    DATABASE_URL: str = Field(
        default="",
        description="PostgreSQL connection URL",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        if not v or v == "":
            raise ValueError(
                "DATABASE_URL is required. Please set it in Railway environment variables."
            )
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                f"DATABASE_URL must start with 'postgresql://' or 'postgres://', got: {v[:20]}"
            )
        return v
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool timeout in seconds")

    # ========================================================================
    # REDIS
    # ========================================================================
    REDIS_URL: str = Field(..., description="Redis connection URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Redis max connections")

    # ========================================================================
    # AI API KEYS
    # ========================================================================
    PERPLEXITY_API_KEY: str = Field(..., description="Perplexity API key")
    PERPLEXITY_MODEL: str = Field(default="sonar-pro", description="Perplexity model")

    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic Claude API key")
    ANTHROPIC_MODEL: str = Field(
        default="claude-3-5-sonnet-20241022", description="Claude model"
    )

    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-ada-002", description="OpenAI embedding model"
    )

    REPLICATE_API_KEY: str = Field(..., description="Replicate API key")
    REPLICATE_MODEL: str = Field(
        default="black-forest-labs/flux-schnell", description="Replicate image model"
    )

    # ========================================================================
    # CLOUDINARY
    # ========================================================================
    CLOUDINARY_CLOUD_NAME: str = Field(..., description="Cloudinary cloud name")
    CLOUDINARY_API_KEY: str = Field(..., description="Cloudinary API key")
    CLOUDINARY_API_SECRET: str = Field(..., description="Cloudinary API secret")

    # ========================================================================
    # COST CONTROLS
    # ========================================================================
    DAILY_COST_CAP: Decimal = Field(
        default=Decimal("30.00"), description="Daily cost cap in USD"
    )
    PER_JOB_COST_CAP: Decimal = Field(
        default=Decimal("0.75"), description="Per-job cost cap in USD"
    )
    ENABLE_COST_CIRCUIT_BREAKER: bool = Field(
        default=True, description="Enable cost circuit breaker"
    )

    # ========================================================================
    # QUEUE CONFIGURATION
    # ========================================================================
    QUEUE_NAME: str = Field(default="quest-articles", description="BullMQ queue name")
    QUEUE_CONCURRENCY: int = Field(default=5, description="Worker concurrency")
    QUEUE_MAX_JOBS_PER_MINUTE: int = Field(
        default=10, description="Max jobs per minute"
    )
    QUEUE_RETRY_ATTEMPTS: int = Field(default=5, description="Retry attempts")
    QUEUE_RETRY_BACKOFF_MS: int = Field(
        default=2000, description="Retry backoff in ms"
    )

    # ========================================================================
    # CACHE CONFIGURATION
    # ========================================================================
    RESEARCH_CACHE_ENABLED: bool = Field(
        default=True, description="Enable research cache"
    )
    RESEARCH_CACHE_SIMILARITY_THRESHOLD: float = Field(
        default=0.75, description="Cache similarity threshold"
    )
    RESEARCH_CACHE_TTL_DAYS: int = Field(
        default=30, description="Cache TTL in days"
    )

    # ========================================================================
    # CORS
    # ========================================================================
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:4321",
            "https://relocation.quest",
            "https://placement.quest",
            "https://rainmaker.quest",
        ],
        description="CORS allowed origins",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=100, description="Rate limit per minute"
    )
    RATE_LIMIT_BURST: int = Field(default=20, description="Rate limit burst")

    # ========================================================================
    # MONITORING
    # ========================================================================
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    SENTRY_ENVIRONMENT: str = Field(default="development", description="Sentry environment")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(
        default=0.1, description="Sentry traces sample rate"
    )

    PROMETHEUS_ENABLED: bool = Field(
        default=True, description="Enable Prometheus metrics"
    )
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus port")

    # ========================================================================
    # DIRECTUS
    # ========================================================================
    DIRECTUS_URL: str = Field(
        default="http://localhost:8055", description="Directus URL"
    )
    DIRECTUS_API_TOKEN: Optional[str] = Field(
        default=None, description="Directus API token"
    )

    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    ENABLE_IMAGE_GENERATION: bool = Field(
        default=True, description="Enable image generation"
    )
    ENABLE_HITL_REVIEW: bool = Field(
        default=True, description="Enable human-in-the-loop review"
    )
    ENABLE_AUTO_PUBLISH: bool = Field(
        default=False, description="Enable auto-publish for high-quality articles"
    )
    ENABLE_BATCH_API: bool = Field(
        default=True, description="Enable batch API for cost savings"
    )

    # ========================================================================
    # TESTING
    # ========================================================================
    TEST_DATABASE_URL: Optional[str] = Field(
        default=None, description="Test database URL"
    )
    MOCK_AI_APIS: bool = Field(default=False, description="Mock AI APIs for testing")


# Global settings instance
settings = Settings()
