"""A handle for a lease acquired through a manager."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from coleasing.exceptions import LeaseLostError

if TYPE_CHECKING:
    from .manager import LeaseManager


class Lease:
    """An acquired lease that can be renewed, released, or used as a context manager."""

    def __init__(self, manager: LeaseManager, key: str, owner_id: str, expires_at: datetime) -> None:
        self._manager = manager
        self.key = key
        self.owner_id = owner_id
        self.expires_at = expires_at
        self._released = False

    @property
    def released(self) -> bool:
        """Whether this handle has been released or has lost ownership."""
        return self._released

    def renew(self, ttl: float | None = None) -> Lease:
        """Extend the lease, raising :class:`LeaseLostError` if ownership was lost."""
        self.expires_at = self._manager.renew(self, ttl).expires_at
        return self

    def release(self) -> None:
        """Release this lease. Releasing an already released handle is harmless."""
        if not self._released:
            self._manager.release(self)
            self._released = True

    def __enter__(self) -> Lease:
        return self

    def __exit__(self, *_: object) -> None:
        self.release()

    def __repr__(self) -> str:
        return f"Lease(key={self.key!r}, owner_id={self.owner_id!r}, expires_at={self.expires_at!r})"
