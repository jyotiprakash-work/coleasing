"""Native asynchronous lease-management API."""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from coleasing.exceptions import LeaseLostError, LeaseNotOwnedError, LeaseUnavailableError

from .async_interface import AsyncLeaseBackend
from .async_lease import AsyncLease


class AsyncLeaseManager:
    """Coordinates leases in asyncio applications such as FastAPI."""

    def __init__(self, backend: AsyncLeaseBackend, *, default_ttl: float = 30.0) -> None:
        if default_ttl <= 0:
            raise ValueError("default_ttl must be greater than zero")
        self.backend = backend
        self.default_ttl = default_ttl

    async def acquire(self, key: str, *, ttl: float | None = None, owner_id: str | None = None) -> AsyncLease:
        """Acquire ``key`` or raise :class:`LeaseUnavailableError`."""
        record = await self.backend.acquire(key, owner_id or uuid4().hex, self._duration(ttl))
        if record is None:
            raise LeaseUnavailableError(f"lease {key!r} is already held")
        return AsyncLease(self, record.key, record.owner_id, record.expires_at)

    async def try_acquire(self, key: str, *, ttl: float | None = None, owner_id: str | None = None) -> AsyncLease | None:
        """Acquire ``key`` when available, otherwise return ``None``."""
        try:
            return await self.acquire(key, ttl=ttl, owner_id=owner_id)
        except LeaseUnavailableError:
            return None

    async def renew(self, lease: AsyncLease, ttl: float | None = None) -> AsyncLease:
        if lease.released:
            raise LeaseLostError(f"lease {lease.key!r} has already been released")
        record = await self.backend.renew(lease.key, lease.owner_id, self._duration(ttl))
        if record is None:
            lease._released = True
            raise LeaseLostError(f"lease {lease.key!r} is no longer owned")
        lease.expires_at = record.expires_at
        return lease

    async def release(self, lease: AsyncLease) -> None:
        if not await self.backend.release(lease.key, lease.owner_id):
            raise LeaseNotOwnedError(f"lease {lease.key!r} is not owned by this handle")

    def _duration(self, ttl: float | None) -> timedelta:
        seconds = self.default_ttl if ttl is None else ttl
        if seconds <= 0:
            raise ValueError("ttl must be greater than zero")
        return timedelta(seconds=seconds)
