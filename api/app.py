from __future__ import annotations
from pathlib import Path
from typing import List

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

# Инициализация ядра
_hist = HistoryRepository()
_orch = ChatOrchestrator(history=_hist, rag_enabled=settings.RAG_ENABLED)

app = FastAPI(title="AI Agent Core API", version="1.0.0")

# CORS (для внешних фронтов)
allow_origins = settings.CORS_ORIGINS or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели 
class ChatRequest(BaseModel):
    channel: str = Field(..., examples=["web", "telegram"])
    user_id: str = Field(..., examples=["u-123"])
    text: str

class ChatResponse(BaseModel):
    parts: List[str]
    provider: str = settings.LLM_PROVIDER

# Маршруты API
@app.post("/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        parts = _orch.reply(req.channel, req.user_id, req.text)
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

