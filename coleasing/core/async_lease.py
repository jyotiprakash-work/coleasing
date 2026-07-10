"""Asynchronous lease handle."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from coleasing.exceptions import LeaseLostError

if TYPE_CHECKING:
    from .async_manager import AsyncLeaseManager


class AsyncLease:
    """A native-async lease handle for use with ``async with``."""

    def __init__(self, manager: AsyncLeaseManager, key: str, owner_id: str, expires_at: datetime) -> None:
        self._manager = manager
        self.key = key
        self.owner_id = owner_id
        self.expires_at = expires_at
        self._released = False

    @property
    def released(self) -> bool:
        return self._released

    async def renew(self, ttl: float | None = None) -> AsyncLease:
        """Extend the lease without blocking the event loop."""
        self.expires_at = (await self._manager.renew(self, ttl)).expires_at
        return self

    async def release(self) -> None:
        """Release this lease; repeated releases are harmless."""
        if not self._released:
            await self._manager.release(self)
            self._released = True

    async def __aenter__(self) -> AsyncLease:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.release()
