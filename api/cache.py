import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class _Entry:
    value: Any
    expires_at: float


class InMemoryTTLCache:
    def __init__(
        self,
        *,
        max_items: int = 10_000,
        gc_every: int = 500,
    ):
        self._store: Dict[str, _Entry] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._max_items = max(1, int(max_items))
        self._gc_every = max(50, int(gc_every))
        self._ops = 0

    @staticmethod
    def _now() -> float:
        return time.monotonic()

    async def get(self, key: str) -> Any | None:
        """
        Получить значение по ключу или None, если срок действия истёк.
        """
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at <= self._now():
            self._store.pop(key, None)
            return None
        return entry.value

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """
        Установить значение с ограничением по времени жизни (TTL).
        """
        if ttl_seconds <= 0:
            self._store.pop(key, None)
            return

        self._store[key] = _Entry(
            value=value, expires_at=self._now() + float(ttl_seconds)
        )
        self._ops += 1

        if self._ops % self._gc_every == 0:
            self._gc()

        if len(self._store) > self._max_items:
            self._evict_some()

    async def delete(self, key: str) -> None:
        """
        Удалить значение по ключу, если оно существует.
        """
        self._store.pop(key, None)

    async def clear(self) -> None:
        """
        Очистить кэш и все связанные блокировки.
        """
        self._store.clear()
        self._locks.clear()

    def lock_for(self, key: str) -> asyncio.Lock:
        """
        Получить или создать асинхронный lock для указанного ключа.
        """
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    def _gc(self) -> None:
        """
        Удалить все устаревшие записи из кэша.
        """
        now = self._now()
        expired_keys = [
            cache_key
            for cache_key, entry in self._store.items()
            if entry.expires_at <= now
        ]
        for cache_key in expired_keys:
            self._store.pop(cache_key, None)

    def _evict_some(self) -> None:
        """
        Удалить часть старых записей при превышении лимита кэша.
        """
        self._gc()
        excess_items_count = len(self._store) - self._max_items
        if excess_items_count <= 0:
            return

        sorted_items = sorted(self._store.items(), key=lambda item: item[1].expires_at)
        items_to_delete = min(excess_items_count, max(1, int(self._max_items * 0.1)))
        for index in range(items_to_delete):
            cache_key = sorted_items[index][0]
            self._store.pop(cache_key, None)
