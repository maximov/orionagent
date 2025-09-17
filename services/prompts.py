from __future__ import annotations
from typing import Optional
from domain.rag import RetrievalResult, RAGContext
from domain.message import Message


def build_system_preamble() -> str:
    return (
        "Вы внимательный и лаконичный ассистент. "
        "Если дан контекст, используйте факты из него. "
        "Если уверенности нет, скажите об этом честно и попросите уточнение. "
        "Отвечайте по делу, без воды."
    )


def make_context_system_message(results: RetrievalResult, title: Optional[str] = None, max_chars: int = 2000) -> Message:
    preamble = build_system_preamble()
    ctx = RAGContext(results=results, title=title or "Контекст из базы знаний")
    text = f"{preamble}\n\n{ctx.format_text(max_chars=max_chars)}"
    return ctx.as_system_message(max_chars=max_chars).__class__(role=ctx.as_system_message().role, content=text)
