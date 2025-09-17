from __future__ import annotations
import time
import threading
from typing import List, Optional
from .base import BaseLLM

try:
    from core.logging import get_logger
except Exception:
    import logging
    get_logger = logging.getLogger


class LoggingLLM(BaseLLM):
    def __init__(self, inner: BaseLLM, name: str = "LLM", max_preview: int = 200) -> None:
        self.inner = inner
        self.log = get_logger(f"{name}")
        self.max_preview = max_preview

    def chat(self, messages: List[dict]) -> str:
        try:
            t0 = time.perf_counter()
            preview = ""
            if messages:
                last = messages[-1]
                preview = (last.get("content") or "")[: self.max_preview].replace("\n", " ")
            self.log.info("-> chat(%s msg) last=%r", len(messages), preview)
            out = self.inner.chat(messages)
            dt = (time.perf_counter() - t0) * 1000
            self.log.info("<- chat(%d chars) in %.1f ms", len(out or ""), dt)
            return out
        except Exception as e:
            self.log.exception("LLM error")
            return f"LLM error: {e}"


class RetryingLLM(BaseLLM):

    def __init__(self, inner: BaseLLM, attempts: int = 3, backoff: float = 0.7, max_backoff: float = 4.0) -> None:
        self.inner = inner
        self.attempts = max(1, attempts)
        self.backoff = backoff
        self.max_backoff = max_backoff
        self.log = get_logger("RetryingLLM")

    def chat(self, messages: List[dict]) -> str:
        delay = self.backoff
        last_exc: Optional[Exception] = None
        for i in range(1, self.attempts + 1):
            try:
                return self.inner.chat(messages)
            except Exception as e:
                last_exc = e
                if i == self.attempts:
                    break
                self.log.warning("Retry %d/%d after error: %s", i, self.attempts, e)
                time.sleep(min(delay, self.max_backoff))
                delay *= 2
        raise last_exc or RuntimeError("Unknown LLM error")


class RateLimitLLM(BaseLLM):
    def __init__(self, inner: BaseLLM, rps: float = 2.0, burst: int = 2) -> None:
        self.inner = inner
        self.capacity = max(1, int(burst))
        self.tokens = float(self.capacity)
        self.rate = float(rps)  # токенов в секунду
        self.lock = threading.Lock()
        self.last = time.monotonic()

    def _acquire(self) -> None:
        while True:
            with self.lock:
                now = time.monotonic()
                elapsed = now - self.last
                self.last = now
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return
                # не хватает токенов — ждём
                need = (1.0 - self.tokens) / self.rate
            time.sleep(max(need, 0.01))

    def chat(self, messages: List[dict]) -> str:
        self._acquire()
        return self.inner.chat(messages)
