from fastapi.testclient import TestClient

def test_chat_endpoint_with_fake_orchestrator(monkeypatch):
    import api.app as app_module

    class FakeOrchestrator:
        def reply(self, channel, user_id, text):
            assert channel in ("web", "telegram")
            assert isinstance(user_id, str)
            assert text
            return [f"echo: {text}"]

    monkeypatch.setattr(app_module, "_orch", FakeOrchestrator(), raising=True)

    client = TestClient(app_module.app)
    resp = client.post(
        "/v1/chat",
        json={"channel": "web", "user_id": "u1", "text": "привет"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["parts"] == ["echo: привет"]
    assert "provider" in data  

def test_healthz(monkeypatch):
    import api.app as app_module
    client = TestClient(app_module.app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
