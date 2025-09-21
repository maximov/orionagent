from __future__ import annotations
from pathlib import Path
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.config import settings
from core.history import HistoryRepository
from core.logging import setup_logging, get_logger
from services.orchestrator import ChatOrchestrator

# Логи
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
    # Инициализация при старте
    app.state.hist = HistoryRepository()
    app.state.orch = ChatOrchestrator(
        history=app.state.hist,
        rag_enabled=settings.RAG_ENABLED,
    )
    log.info("HistoryRepository и ChatOrchestrator инициализированы")

    yield  

    
    app.state.orch = None
    app.state.hist = None
    log.info("Сервисы OrionAgent остановлены")


# Фабрика приложения
def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Agent Core API",
        version="1.0.0",
        lifespan=lifespan, 
    )

    # CORS
    allow_origins = settings.CORS_ORIGINS or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Маршруты API
    @app.post("/v1/chat", response_model=ChatResponse)
    def chat(req: ChatRequest):
        if app.state.orch is None:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")

        try:
            parts = app.state.orch.reply(req.channel, req.user_id, req.text)
            return ChatResponse(parts=parts)
        except Exception as e:
            log.exception("Error in /v1/chat")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    # Статика
    STATIC_DIR = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def index():
        index_file = STATIC_DIR / "index.html"
        return FileResponse(index_file)

    return app


app = create_app()
