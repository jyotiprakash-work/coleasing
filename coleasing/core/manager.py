"""Backend-independent lease acquisition API."""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from coleasing.exceptions import LeaseLostError, LeaseNotOwnedError, LeaseUnavailableError

from .interface import LeaseBackend
from .lease import Lease


class LeaseManager:
    """Coordinates lease lifecycle operations using one configured backend."""

    def __init__(self, backend: LeaseBackend, *, default_ttl: float = 30.0) -> None:
        if default_ttl <= 0:
            raise ValueError("default_ttl must be greater than zero")
        self.backend = backend
        self.default_ttl = default_ttl

    def acquire(self, key: str, *, ttl: float | None = None, owner_id: str | None = None) -> Lease:
        """Acquire ``key`` or raise :class:`LeaseUnavailableError`."""
        duration = self._duration(ttl)
        owner = owner_id or uuid4().hex
        record = self.backend.acquire(key, owner, duration)
        if record is None:
            raise LeaseUnavailableError(f"lease {key!r} is already held")
        return Lease(self, record.key, record.owner_id, record.expires_at)

    def try_acquire(self, key: str, *, ttl: float | None = None, owner_id: str | None = None) -> Lease | None:
        """Acquire ``key`` if possible; return ``None`` when it is held."""
        try:
            return self.acquire(key, ttl=ttl, owner_id=owner_id)
        except LeaseUnavailableError:
            return None

    def renew(self, lease: Lease, ttl: float | None = None) -> Lease:
        """Renew an existing handle, requiring the same owner token."""
        if lease.released:
            raise LeaseLostError(f"lease {lease.key!r} has already been released")
        record = self.backend.renew(lease.key, lease.owner_id, self._duration(ttl))
        if record is None:
            lease._released = True
            raise LeaseLostError(f"lease {lease.key!r} is no longer owned")
        lease.expires_at = record.expires_at
        return lease

    def release(self, lease: Lease) -> None:
        """Release an existing handle, requiring the same owner token."""
        if not self.backend.release(lease.key, lease.owner_id):
            raise LeaseNotOwnedError(f"lease {lease.key!r} is not owned by this handle")

    def _duration(self, ttl: float | None) -> timedelta:
        seconds = self.default_ttl if ttl is None else ttl
        if seconds <= 0:
            raise ValueError("ttl must be greater than zero")
        return timedelta(seconds=seconds)
