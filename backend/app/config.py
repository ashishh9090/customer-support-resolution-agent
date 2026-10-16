import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Production-Style AI Customer Support Resolution Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./support_agent.db"
    
    # Security & Auth
    SECRET_KEY: str = "dev-insecure-secret-key-change-in-production-support-agent-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "mock", "openai", "anthropic", "gemini"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    
    # Policy Thresholds
    AUTO_REFUND_LIMIT_USD: float = 50.00
    MAX_REFUNDS_PER_90_DAYS: int = 2
    REFUND_WINDOW_DAYS: int = 30
    DAMAGED_REPORT_WINDOW_DAYS: int = 14
    
    # Knowledge Base / RAG
    KNOWLEDGE_BASE_DIR: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../knowledge_base")
    )
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
