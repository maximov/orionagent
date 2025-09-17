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

    def as_chat_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"role": self.role.value, "content": self.content}
        if self.name:
            d["name"] = self.name
        return d


def user(text: str, **meta: Any) -> Message:
    return Message(Role.user, text, metadata=meta)

def assistant(text: str, **meta: Any) -> Message:
    return Message(Role.assistant, text, metadata=meta)

def system(text: str, **meta: Any) -> Message:
    return Message(Role.system, text, metadata=meta)


ChatLike = Union[Message, Dict[str, Any]]

def to_chat_messages(items: Iterable[ChatLike]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items:
        if isinstance(it, Message):
            out.append(it.as_chat_dict())
        elif isinstance(it, dict):
            out.append(it)
        else:
            raise TypeError(f"Unsupported chat item type: {type(it)!r}")
    return out
