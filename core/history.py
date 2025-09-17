from __future__ import annotations
from collections import defaultdict
from threading import Lock
from typing import Dict, List

class HistoryRepository:
    def __init__(self, window: int = 20):
        self._store: Dict[str, List[dict]] = defaultdict(list)
        self._win = window
        self._lock = Lock()

    @staticmethod
    def _key(channel: str, user_id: str) -> str:
        return f"{channel}:{user_id}"

    def messages(self, channel: str, user_id: str) -> List[dict]:
        with self._lock:
            return list(self._store[self._key(channel, user_id)][-self._win:])

    def append(self, channel: str, user_id: str, role: str, content: str) -> None:
        with self._lock:
            key = self._key(channel, user_id)
            self._store[key].append({"role": role, "content": content})
            self._store[key] = self._store[key][-self._win:]

    # удобные алиасы
    def append_user(self, channel: str, user_id: str, content: str) -> None:
        self.append(channel, user_id, "user", content)

    def append_system(self, channel: str, user_id: str, content: str) -> None:
        self.append(channel, user_id, "system", content)

    def append_assistant(self, channel: str, user_id: str, content: str) -> None:
        self.append(channel, user_id, "assistant", content)

    def reset(self, channel: str, user_id: str) -> None:
        with self._lock:
            self._store.pop(self._key(channel, user_id), None)
