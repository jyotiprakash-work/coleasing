"""Native asyncio in-memory backend for application development and tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from coleasing.core.async_interface import AsyncLeaseBackend
from coleasing.models import LeaseRecord


class AsyncMemoryBackend(AsyncLeaseBackend):
    """An event-loop-safe backend using ``asyncio.Lock`` for atomic operations."""

    def __init__(self) -> None:
        self._leases: dict[str, LeaseRecord] = {}
        self._lock = asyncio.Lock()

    async def acquire(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        async with self._lock:
            self._purge_expired(key)
            if key in self._leases:
                return None
            record = LeaseRecord(key, owner_id, self._expires_after(ttl))
            self._leases[key] = record
            return record

    async def renew(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        async with self._lock:
            record = self._valid_record(key)
            if record is None or record.owner_id != owner_id:
                return None
            renewed = LeaseRecord(key, owner_id, self._expires_after(ttl))
            self._leases[key] = renewed
            return renewed

    async def release(self, key: str, owner_id: str) -> bool:
        async with self._lock:
            record = self._valid_record(key)
            if record is None or record.owner_id != owner_id:
                return False
            del self._leases[key]
            return True

    async def get(self, key: str) -> LeaseRecord | None:
        async with self._lock:
            return self._valid_record(key)

    def _valid_record(self, key: str) -> LeaseRecord | None:
        self._purge_expired(key)
        return self._leases.get(key)

    def _purge_expired(self, key: str) -> None:
        record = self._leases.get(key)
        if record is not None and record.expires_at <= self._now():
            del self._leases[key]

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def _expires_after(cls, ttl: timedelta) -> datetime:
        return cls._now() + ttl
