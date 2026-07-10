"""Backend contract used by :class:`coleasing.LeaseManager`."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta

from coleasing.models import LeaseRecord


class LeaseBackend(ABC):
    """Storage and atomicity boundary for lease operations.

    Backends use monotonic, backend-local time when possible.  A successful
    operation is always scoped to the supplied ``owner_id``.
    """

    @abstractmethod
    def acquire(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        """Acquire an available lease, returning its record or ``None``."""

    @abstractmethod
    def renew(self, key: str, owner_id: str, ttl: timedelta) -> LeaseRecord | None:
        """Renew an owned, unexpired lease, returning its record or ``None``."""

    @abstractmethod
    def release(self, key: str, owner_id: str) -> bool:
        """Release an owned lease and return whether it was released."""

    @abstractmethod
    def get(self, key: str) -> LeaseRecord | None:
        """Return the current unexpired record, if any."""
