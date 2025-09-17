from __future__ import annotations
import os
from typing import Optional

from .base import BaseLLM
from .openai_compat import OpenAICompatLLM
from .decorators import LoggingLLM, RetryingLLM, RateLimitLLM


try:
    from core.config import settings
except Exception:
    settings = None


def _openrouter_headers() -> dict:
    if not settings:
        return {}
    return settings.openrouter_headers()


def make_llm(
    provider: Optional[str] = None,
    *,
    with_logging: bool = True,
    with_retry: bool = True,
    with_rate_limit: bool = True,
) -> BaseLLM:
    prov = (provider or (getattr(settings, "LLM_PROVIDER", "openrouter") if settings else "openrouter")).lower()

    if prov == "openrouter":
        base_url = getattr(settings, "OPENAI_BASE_URL", "https://openrouter.ai/api/v1") if settings else "https://openrouter.ai/api/v1"
        api_key  = getattr(settings, "OPENROUTER_API_KEY", "") if settings else os.getenv("OPENROUTER_API_KEY", "")
        model    = getattr(settings, "OPENROUTER_MODEL", "gpt-4o-mini") if settings else os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
        llm: BaseLLM = OpenAICompatLLM(base_url, api_key or None, model, extra_headers=_openrouter_headers(), return_errors=False)

    elif prov == "groq":
        base_url = "https://api.groq.com/openai/v1"
        api_key  = getattr(settings, "GROQ_API_KEY", "") if settings else os.getenv("GROQ_API_KEY", "")
        model    = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        llm = OpenAICompatLLM(base_url, api_key or None, model, return_errors=False)

    elif prov == "openai":
        base_url = "https://api.openai.com/v1"
        api_key  = getattr(settings, "OPENAI_API_KEY", "") if settings else os.getenv("OPENAI_API_KEY", "")
        model    = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        llm = OpenAICompatLLM(base_url, api_key or None, model, return_errors=False)

    elif prov == "ollama":
        base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434/v1") if settings else os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        api_key  = os.getenv("OLLAMA_API_KEY", "")
        model    = os.getenv("OLLAMA_MODEL", "llama3")
        llm = OpenAICompatLLM(base_url, api_key or None, model, return_errors=False)

    else:
        raise ValueError(f"Unknown LLM provider: {prov}")

    
    if with_rate_limit:
        llm = RateLimitLLM(llm, rps=float(os.getenv("LLM_RPS", "2.0")), burst=int(os.getenv("LLM_BURST", "2")))
    if with_retry:
        llm = RetryingLLM(llm, attempts=int(os.getenv("LLM_RETRIES", "3")))
    if with_logging:
        llm = LoggingLLM(llm, name=f"LLM[{prov}]")

    return llm
