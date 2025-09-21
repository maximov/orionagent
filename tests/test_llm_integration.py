
import pytest
from fastapi.testclient import TestClient
from api.app import create_app

@pytest.mark.llm
def test_chat_with_real_llm():
    app = create_app()
    with TestClient(app) as client:
        resp = client.post(
            "/v1/chat",
            json={"channel": "web", "user_id": "u-llm", "text": "Привет, кто ты?"}
        )

        assert resp.status_code == 200
        data = resp.json()

        assert isinstance(data["parts"], list)
        assert len(data["parts"]) > 0
        assert isinstance(data["parts"][0], str)

        assert "provider" in data
        assert "привет" in data["parts"][0].lower() or "hello" in data["parts"][0].lower()