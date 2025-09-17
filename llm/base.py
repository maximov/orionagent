from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List


class BaseLLM(ABC):

    @abstractmethod
    def chat(self, messages: List[dict]) -> str:
        ...
