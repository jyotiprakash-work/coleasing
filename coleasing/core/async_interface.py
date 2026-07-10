"""Native asynchronous backend contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta

from coleasing.models import LeaseRecord


class AsyncLeaseBackend(ABC):
    """Async storage contract for event-loop based applications."""

    @abstractmethod
    async def acquire(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        """Acquire an available lease, returning its record or ``None``."""

    @abstractmethod
    async def renew(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        """Renew an owned, unexpired lease, returning its record or ``None``."""

    @abstractmethod
    async def release(self, key: str, owner_id: str) -> bool:
        """Release an owned lease and return whether it was released."""

    @abstractmethod
    async def get(self, key: str) -> LeaseRecord | None:
        """Return the current unexpired record, if any."""
