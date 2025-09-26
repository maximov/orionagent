# domain/message.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Union


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


@dataclass(frozen=True)
class Message:
    role: Role
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_chat_dict(self, include_metadata: bool = False) -> Dict[str, Any]:
        """Сериализация в dict для клиента чата; метаданные по умолчанию не включаем."""
        d: Dict[str, Any] = {"role": self.role.value, "content": self.content}
        if self.name:
            d["name"] = self.name
        if include_metadata and self.metadata:
            d["metadata"] = dict(self.metadata)
        return d


def user(text: str, **meta: Any) -> Message:
    return Message(Role.user, text, metadata=meta)

def assistant(text: str, **meta: Any) -> Message:
    return Message(Role.assistant, text, metadata=meta)

def system(text: str, **meta: Any) -> Message:
    return Message(Role.system, text, metadata=meta)

def tool(text: str, name: Optional[str] = None, **meta: Any) -> Message:
    return Message(Role.tool, text, name=name, metadata=meta)


ChatLike = Union[Message, Dict[str, Any]]

def to_chat_messages(items: Iterable[ChatLike], *, include_metadata: bool = False) -> List[Dict[str, Any]]:
    """Преобразует список сообщений в список dict с базовой валидацией."""
    out: List[Dict[str, Any]] = []
    for it in items:
        if isinstance(it, Message):
            out.append(it.as_chat_dict(include_metadata=include_metadata))
        elif isinstance(it, dict):
            # Валидация входного словаря
            role = it.get("role")
            content = it.get("content")
            if not isinstance(role, str) or role not in {r.value for r in Role}:
                raise ValueError(f"invalid role: {role!r}")
            if not isinstance(content, str):
                raise ValueError("content must be str")
            # Копируем, чтобы защититься от внешней мутации
            out.append(dict(it))
        else:
            raise TypeError(f"Unsupported chat item type: {type(it)!r}")
    return out
