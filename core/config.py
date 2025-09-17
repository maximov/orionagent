from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# грузим .env из корня репозитория
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

def _csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]

def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

class Settings:
    # API / Server 
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = _bool(os.getenv("API_RELOAD"), False)
    API_LOG_LEVEL: str = os.getenv("API_LOG_LEVEL", "info")
    CORS_ORIGINS: list[str] = _csv(os.getenv("CORS_ORIGINS", ""))

    # Features
    RAG_ENABLED: bool = _bool(os.getenv("RAG_ENABLED"), False)

    # LLM (по умолчанию OpenRouter)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3.1:free")
    OPENROUTER_HTTP_REFERRER: str | None = os.getenv("OPENROUTER_HTTP_REFERRER")
    OPENROUTER_X_TITLE: str | None = os.getenv("OPENROUTER_X_TITLE")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    # Vector Stores (RAG)
    VS_PROVIDER: str = os.getenv("VS_PROVIDER", "chroma")
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", "./chroma_store")
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "ai_agent")

    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "rag_demo")

    # Telegram
    TELEGA_TOKEN: str = os.getenv("TELEGA_TOKEN", "")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # заголовки для OpenRouter
    def openrouter_headers(self) -> dict:
        h: dict[str, str] = {}
        if self.OPENROUTER_HTTP_REFERRER:
            h["HTTP-Referer"] = self.OPENROUTER_HTTP_REFERRER
        if self.OPENROUTER_X_TITLE:
            h["X-Title"] = self.OPENROUTER_X_TITLE
        return h

settings = Settings()
