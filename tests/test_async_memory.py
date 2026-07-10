import asyncio

import pytest

from coleasing import AsyncLeaseManager, AsyncMemoryBackend, LeaseLostError


def test_async_acquire_release_and_contention():
    async def scenario():
        manager = AsyncLeaseManager(AsyncMemoryBackend(), default_ttl=1)
        first = await manager.acquire("report", owner_id="worker-a")
        assert await manager.try_acquire("report", owner_id="worker-b") is None
        await first.release()
        assert await manager.try_acquire("report", owner_id="worker-b") is not None

    asyncio.run(scenario())


def test_async_expiry_prevents_renewal():
    async def scenario():
        manager = AsyncLeaseManager(AsyncMemoryBackend(), default_ttl=0.01)
        lease = await manager.acquire("report")
        await asyncio.sleep(0.02)
        with pytest.raises(LeaseLostError):
            await lease.renew()

    asyncio.run(scenario())
