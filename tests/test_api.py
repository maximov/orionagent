from __future__ import annotations
from typing import List, Optional

from fastapi.testclient import TestClient
from api.app import app
from api.app import create_app


app = create_app()
client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

# Привет! 😊 Чем могу помочь?

def test_chat():
    class FakeOrchestrator:
        def reply(self, channel: str, user_id: str, user_text: str) -> List[str]:  
            assert channel in ["web", "telegram"]
            assert isinstance(user_id, str)
            assert user_text
            return [f"echo: {user_text}"]

    app.state.orch = FakeOrchestrator()

    r = client.post(
        "/v1/chat",
        json={
            "channel": "web",
            "user_id": "u-123",
            "text": "ку",
        },
    )
    assert r.status_code == 200
    assert r.json() == {"parts": ["echo: ку"], "provider": "openrouter"}
    

