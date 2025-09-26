from __future__ import annotations
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Literal, TypedDict
import time
import copy

Role = Literal["user", "assistant", "system"]

class Message(TypedDict):
    role: Role
    content: str
    ts: float  # метка времени (секунды с эпохи)

class HistoryRepository:
    def __init__(self, window: int = 20, max_keys: int | None = None):
        # window — длина окна в сообщениях на один ключ (channel:user_id)
        # max_keys — необязательное ограничение на число разных ключей
        if window < 0:
            raise ValueError("window must be >= 0")
        self._store: Dict[str, List[Message]] = defaultdict(list)
        self._win = window
        self._lock = Lock()
        self._max_keys = max_keys

    @staticmethod
    def _key(channel: str, user_id: str) -> str:
        return f"{channel}:{user_id}"

    def messages(self, channel: str, user_id: str) -> List[Message]:
        # Возвращаем глубокую копию, чтобы внешние изменения не затронули хранилище
        with self._lock:
            msgs = self._store[self._key(channel, user_id)][-self._win:]
            return copy.deepcopy(msgs)

    def append(self, channel: str, user_id: str, role: Role, content: str) -> None:
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"invalid role: {role}")
        if content is None:
            content = ""
        key = self._key(channel, user_id)
        with self._lock:
            # Простая защита от бесконтрольного роста количества ключей
            if self._max_keys is not None and key not in self._store and len(self._store) >= self._max_keys:
                # удаляем самый старый ключ (наивная политика FIFO)
                oldest_key = next(iter(self._store))
                self._store.pop(oldest_key, None)

            self._store[key].append({"role": role, "content": content, "ts": time.time()})
            if self._win > 0:
                self._store[key] = self._store[key][-self._win:]
            else:
                # окно 0 — очищаем хранение (разрешено, но странно)
                self._store[key].clear()

    # Алиасы
    def append_user(self, channel: str, user_id: str, content: str) -> None:
        self.append(channel, user_id, "user", content)

    def append_system(self, channel: str, user_id: str, content: str) -> None:
        self.append(channel, user_id, "system", content)

    def append_assistant(self, channel: str, user_id: str, content: str) -> None:
        self.append(channel, user_id, "assistant", content)

    def reset(self, channel: str, user_id: str) -> None:
        with self._lock:
            self._store.pop(self._key(channel, user_id), None)
