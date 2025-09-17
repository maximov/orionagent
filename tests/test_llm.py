import json
import types
from llm.openai_compat import OpenAICompatLLM

class DummyResp:
    def __init__(self, status=200, payload=None):
        self._status = status
        self._payload = payload or {"choices": [{"message": {"content": "OK"}}]}

    def raise_for_status(self):
        if self._status >= 400:
            raise RuntimeError(f"http {self._status}")

    def json(self):
        return self._payload

def test_openai_compat_success(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=60):
        assert url.endswith("/chat/completions")
        assert "Authorization" in headers or True 
        assert "model" in json and "messages" in json
        return DummyResp(status=200, payload={"choices": [{"message": {"content": "hello"}}]})

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    llm = OpenAICompatLLM(
        base_url="",
        api_key="key",
        model="unit-test-model",
        return_errors=False,
    )
    out = llm.chat([{"role": "user", "content": "ping"}])
    assert out == "hello"

def test_openai_compat_error_returns_text_when_flag_enabled(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=60):
        return DummyResp(status=500)

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    llm = OpenAICompatLLM(
        base_url="",
        api_key=None,
        model="unit-test-model",
        return_errors=True,
    )
    out = llm.chat([{"role": "user", "content": "ping"}])
    assert "LLM error" in out or "error" in out.lower()
