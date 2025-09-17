from __future__ import annotations
from typing import List, Optional

from core.config import settings
from core.history import HistoryRepository
from core.utils import chunk, sanitize
from core.logging import get_logger

from llm.factory import make_llm
from llm.base import BaseLLM

from .retriever import Retriever
from .prompts import make_context_system_message


class ChatOrchestrator:
    def __init__(
        self,
        history: HistoryRepository,
        llm: Optional[BaseLLM] = None,
        retriever: Optional[Retriever] = None,
        rag_enabled: bool = False,
        max_part_len: int = 4096 - 16,
    ) -> None:
        self.log = get_logger("orchestrator")
        self.history = history
        self.llm = llm or make_llm(settings.LLM_PROVIDER)
        self.retriever = retriever or Retriever()
        self.rag = bool(rag_enabled)
        self.max_part_len = max_part_len

    def set_rag(self, enabled: bool) -> None:
        self.rag = bool(enabled)

    def reply(self, channel: str, user_id: str, user_text: str) -> List[str]:        
        clean = sanitize(user_text or "")
        self.history.append_user(channel, user_id, clean)

        messages = self.history.messages(channel, user_id)

        if self.rag and self.retriever.available:
            try:
                rr = self.retriever.retrieve(clean)
                sys_msg = make_context_system_message(rr).as_chat_dict()
                if messages:                    
                    local = [*messages[:-1], sys_msg, messages[-1]]
                else:
                    local = [sys_msg]
                model_input = local
            except Exception as e:                
                self.log.warning("retriever failed: %s", e)
                model_input = messages
        else:
            model_input = messages

        answer = self.llm.chat(model_input) or ""

        self.history.append_assistant(channel, user_id, answer)

        return list(chunk(answer, self.max_part_len))
