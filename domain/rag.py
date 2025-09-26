# domain/rag.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .message import Message, system as system_msg


@dataclass(frozen=True)
class DocumentChunk:
    content: str
    source: Optional[str] = None
    score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)  # метаданные могут быть любыми


@dataclass
class RetrievalResult:
    query: str
    chunks: List[DocumentChunk] = field(default_factory=list)
    k: int = 0
    model_name: Optional[str] = None

    def top(self, n: int) -> "RetrievalResult":
        ordered = sorted(
            self.chunks,
            key=lambda c: (
                c.score is None,
                -(c.score if isinstance(c.score, (int, float)) else 0.0),
                c.source or "",
            ),
        )[: max(0, n)]
        return RetrievalResult(query=self.query, chunks=ordered, k=n, model_name=self.model_name)


@dataclass
class RAGContext:
    results: RetrievalResult
    title: str = "Контекст из базы знаний"

    def format_text(self, max_chars: int = 2000) -> str:
        # Защита от невалидных значений
        if max_chars is None or max_chars <= 0:
            return self.title

        lines: List[str] = [self.title, ""]
        for i, ch in enumerate(self.results.chunks, start=1):
            src = f" (source: {ch.source})" if ch.source else ""
            sc = (
                f" [score: {ch.score:.3f}]"
                if isinstance(ch.score, (int, float))
                else ""
            )
            lines.append(f"{i}. {ch.content}{src}{sc}")
        text = "\n".join(lines).strip()

        if len(text) > max_chars:
            # Гарантируем длину ≤ max_chars и аккуратный суффикс
            ellipsis = "…"
            if max_chars <= len(ellipsis):
                return ellipsis[:max_chars]
            return text[: max_chars - len(ellipsis)] + ellipsis
        return text

    def as_system_message(self, max_chars: int = 2000) -> Message:
        return system_msg(self.format_text(max_chars=max_chars))

    def inject_into(self, history: List[dict], max_chars: int = 2000) -> List[dict]:
        sys = self.as_system_message(max_chars=max_chars).as_chat_dict()
        return [*history, sys]
