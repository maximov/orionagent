from __future__ import annotations
import json
import requests
from typing import Dict, List, Optional
from .base import BaseLLM


class OpenAICompatLLM(BaseLLM):
    """
    Клиент для OpenAI-совместимых API:
    - OpenRouter (https://openrouter.ai/api/v1)
    - Groq (https://api.groq.com/openai/v1)
    - OpenAI (https://api.openai.com/v1)
    - Ollama (http://localhost:11434/v1)
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str],
        model: str,
        extra_headers: Optional[Dict[str, str]] = None,
        temperature: float = 0.7,
        top_p: float = 0.95,
        timeout: int = 60,
        return_errors: bool = False,
    ) -> None:
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.model = model
        self.extra_headers = extra_headers or {}
        self.temperature = temperature
        self.top_p = top_p
        self.timeout = timeout
        self.return_errors = return_errors

    def chat(self, messages: List[dict]) -> str:
        headers = {"Content-Type": "application/json", **self.extra_headers}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
        }

        try:
            resp = requests.post(self.url, headers=headers, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            if self.return_errors:
                return f"LLM error: {e}"
            raise

    def __repr__(self) -> str:
        return f"OpenAICompatLLM(url='{self.url}', model='{self.model}')"
