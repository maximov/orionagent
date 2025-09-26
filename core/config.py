# core/config.py
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Грузим .env из корня репозитория
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def _csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


class Settings:
    # API / Server
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = _int(os.getenv("API_PORT"), 8000)
    API_RELOAD: bool = _bool(os.getenv("API_RELOAD"), False)
    CORS_ORIGINS: list[str] = _csv(os.getenv("CORS_ORIGINS", ""))

    # Features
    RAG_ENABLED: bool = _bool(os.getenv("RAG_ENABLED"), False)

    # Логирование (оставляем один источник правды)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", os.getenv("API_LOG_LEVEL", "INFO"))

    # LLM (по умолчанию OpenRouter)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")

    # OpenAI-совместимые эндпоинты
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3.1:free")
    OPENROUTER_HTTP_REFERRER: str | None = os.getenv("OPENROUTER_HTTP_REFERRER")
    OPENROUTER_X_TITLE: str | None = os.getenv("OPENROUTER_X_TITLE")

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Ollama
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

    # Заголовки для OpenRouter
    def openrouter_headers(self) -> dict[str, str]:
        h: dict[str, str] = {}
        if self.OPENROUTER_HTTP_REFERRER:
            h["HTTP-Referer"] = self.OPENROUTER_HTTP_REFERRER
        if self.OPENROUTER_X_TITLE:
            h["X-Title"] = self.OPENROUTER_X_TITLE
        return h

    # Централизованный выбор base_url и api_key под провайдера
    def llm_base_url(self) -> str:
        p = self.LLM_PROVIDER.lower()
        if p == "openrouter":
            return "https://openrouter.ai/api/v1"
        if p == "openai":
            return "https://api.openai.com/v1"
        if p == "groq":
            return "https://api.groq.com/openai/v1"
        if p == "ollama":
            return self.OLLAMA_BASE_URL
        return self.OPENAI_BASE_URL  # fallback

    def llm_api_key(self) -> str:
        p = self.LLM_PROVIDER.lower()
        if p == "openrouter":
            return self.OPENROUTER_API_KEY
        if p == "openai":
            return self.OPENAI_API_KEY
        if p == "groq":
            return self.GROQ_API_KEY
        if p == "ollama":
            return ""
        return self.OPENAI_API_KEY  # fallback


settings = Settings()
