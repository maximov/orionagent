# llm/decorators.py
from __future__ import annotations

import time
import threading
import random
from typing import List, Optional, Callable

from .base import BaseLLM

try:
    from core.logging import get_logger  # type: ignore
except ImportError:
    import logging
    get_logger = logging.getLogger


class LoggingLLM(BaseLLM):
    """
    Декоратор, который логирует вызовы LLM.
    """

    def __init__(
        self,
        inner: BaseLLM,
        name: str = "LLM",
        max_preview: int = 200,
        return_on_error: Optional[str] = "",
    ) -> None:
        self.inner = inner
        self.log = get_logger(name)
        self.max_preview = max_preview
        self.return_on_error = return_on_error

    def chat(self, messages: List[dict]) -> str:
        try:
            t0 = time.perf_counter()
            preview = ""
            if messages:
                last = messages[-1]
                preview = (last.get("content") or "")[: self.max_preview].replace("\n", " ")
            self.log.info("-> chat(%s msg) last=%r", len(messages), preview)
            out = self.inner.chat(messages)
            dt = (time.perf_counter() - t0) * 1000.0
            self.log.info("<- chat(%d chars) in %.1f ms", len(out or ""), dt)
            return out
        except Exception:
            self.log.exception("LLM error")
            if self.return_on_error is None:
                raise
            return self.return_on_error


class RetryingLLM(BaseLLM):
    """
    Декоратор, который повторяет запрос при ошибках
    """

    def __init__(
        self,
        inner: BaseLLM,
        attempts: int = 3,
        backoff: float = 0.7,
        max_backoff: float = 4.0,
        retry_if: Optional[Callable[[Exception], bool]] = None,
    ) -> None:
        self.inner = inner
        self.attempts = max(1, int(attempts))
        self.backoff = float(backoff)
        self.max_backoff = float(max_backoff)
        self.retry_if = retry_if
        self.log = get_logger("RetryingLLM")

    def chat(self, messages: List[dict]) -> str:
        delay = self.backoff
        last_exc: Optional[Exception] = None
        for i in range(1, self.attempts + 1):
            try:
                return self.inner.chat(messages)
            except Exception as e:
                last_exc = e
                # Если предикат задан и запрещает ретрай — выходим сразу
                if self.retry_if is not None and not self.retry_if(e):
                    break
                if i == self.attempts:
                    break
                self.log.warning("Retry %d/%d after error: %s", i, self.attempts, e)
                # Экспоненциальный бэкофф с лёгким джиттером
                sleep_for = min(delay, self.max_backoff) * (0.8 + 0.4 * random.random())
                time.sleep(sleep_for)
                delay *= 2.0
        # Если сюда попали все попытки исчерпаны или ретрай запрещён
        raise last_exc or RuntimeError("Unknown LLM error")


class RateLimitLLM(BaseLLM):
    def __init__(self, inner: BaseLLM, rps: float = 2.0, burst: int = 2) -> None:
        if rps <= 0:
            raise ValueError("rps must be > 0")
        self.inner = inner
        self.capacity = max(1, int(burst))  # максимальное число жетонов в бакете
        self.tokens = float(self.capacity)  # текущее число жетонов
        self.rate = float(rps)              # скорость пополнения жетонов в секунду
        self.lock = threading.Lock()
        self.last = time.monotonic()

    def _acquire(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                elapsed = now - self.last
                self.last = now
                # пополняем бакет
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                # не хватает жетонов — посчитаем, сколько ждать
                need = (1.0 - self.tokens) / self.rate
            # небольшой джиттер, чтобы потоки не просыпались синхронно
            time.sleep(max(need, 0.01) * (0.9 + 0.2 * random.random()))

    def chat(self, messages: List[dict]) -> str:
        self._acquire()
        return self.inner.chat(messages)
