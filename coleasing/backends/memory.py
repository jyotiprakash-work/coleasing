"""Thread-safe in-process lease backend intended for development and tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import RLock

from coleasing.core.interface import LeaseBackend
from coleasing.models import LeaseRecord


class MemoryBackend(LeaseBackend):
    """Store leases in memory with atomic operations guarded by a re-entrant lock."""

    def __init__(self) -> None:
        self._leases: dict[str, LeaseRecord] = {}
        self._lock = RLock()

    def acquire(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        with self._lock:
            self._purge_expired(key)
            if key in self._leases:
                return None
            record = LeaseRecord(key, owner_id, self._expires_after(ttl))
            self._leases[key] = record
            return record

    def renew(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        with self._lock:
            record = self._valid_record(key)
            if record is None or record.owner_id != owner_id:
                return None
            renewed = LeaseRecord(key, owner_id, self._expires_after(ttl))
            self._leases[key] = renewed
            return renewed

    def release(self, key: str, owner_id: str) -> bool:
        with self._lock:
            record = self._valid_record(key)
            if record is None or record.owner_id != owner_id:
                return False
            del self._leases[key]
            return True

    def get(self, key: str) -> LeaseRecord | None:
        with self._lock:
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
