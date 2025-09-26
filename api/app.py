# api/app.py
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.config import settings
from core.history import HistoryRepository
from core.logging import setup_logging, get_logger
from services.orchestrator import ChatOrchestrator

setup_logging(settings.LOG_LEVEL)
log = get_logger("api")


class ChatRequest(BaseModel):
    channel: str = Field(..., examples=["web", "telegram"])
    user_id: str = Field(..., examples=["u-123"])
    text: str


class ChatResponse(BaseModel):
    parts: List[str]
    provider: str = settings.LLM_PROVIDER


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.hist = HistoryRepository()
    app.state.orch = ChatOrchestrator(
        history=app.state.hist,
        rag_enabled=settings.RAG_ENABLED,
    )
    log.info("HistoryRepository и ChatOrchestrator инициализированы")
    try:
        yield
    finally:
        app.state.orch = None
        app.state.hist = None
        log.info("Сервисы OrionAgent остановлены")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Agent Core API",
        version="1.0.0",
        lifespan=lifespan,
    )

    allow_origins = settings.CORS_ORIGINS or []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins if allow_origins else ["http://localhost:3000"],
        allow_credentials=bool(allow_origins),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/v1/chat", response_model=ChatResponse)
    def chat(req: ChatRequest):
        if not getattr(app.state, "orch", None):
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        try:
            parts = app.state.orch.reply(req.channel, req.user_id, req.text)
            return ChatResponse(parts=parts)
        except HTTPException:
            raise
        except Exception as e:
            log.exception("Ошибка в /v1/chat")
            raise HTTPException(status_code=500, detail="Internal error") from e

    @app.get("/healthz", response_model=dict)
    def healthz():
        return {
            "status": "ok",
            "orch_initialized": bool(getattr(app.state, "orch", None)),
            "hist_initialized": bool(getattr(app.state, "hist", None)),
        }

    @app.post("/v1/toggle_rag", response_model=dict)
    def toggle_rag():
        if not getattr(app.state, "orch", None):
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        try:
            enabled = app.state.orch.toggle_rag()
            return {"rag_enabled": enabled}
        except AttributeError:
            raise HTTPException(status_code=501, detail="toggle_rag is not supported")

    STATIC_DIR = Path(__file__).parent / "static"
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

        @app.get("/")
        def index():
            index_file = STATIC_DIR / "index.html"
            if not index_file.exists():
                raise HTTPException(status_code=404, detail="index.html not found")
            return FileResponse(index_file)
    else:
        log.warning("STATIC_DIR не найден: %s", STATIC_DIR)

    return app


app = create_app()
