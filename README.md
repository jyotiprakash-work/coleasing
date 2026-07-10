# Coleasing

A backend-agnostic Python library for renewable lease coordination. The first
release provides a thread-safe in-memory backend; Redis, SQL, and MongoDB
backends are planned behind the same API.

## Quick start

```python
from coleasing import LeaseManager, MemoryBackend

manager = LeaseManager(MemoryBackend(), default_ttl=30)

with manager.acquire("daily-report"):
    # Exactly one in-process worker holds this lease at a time.
    generate_report()
```

`acquire()` raises `LeaseUnavailableError` when the key is held. Use
`try_acquire()` when normal contention should return `None`, and call
`lease.renew()` for long-running work.

## Async / FastAPI

The async API is native asyncio code, with its own manager, lease handle, and
backend contract. It does not run synchronous backend work in a thread pool.

```python
from coleasing import AsyncLeaseManager, AsyncMemoryBackend

leases = AsyncLeaseManager(AsyncMemoryBackend(), default_ttl=30)

async def create_report():
    lease = await leases.try_acquire("daily-report")
    if lease is None:
        return {"status": "already running"}
    async with lease:
        await generate_report()
```

For a FastAPI route, see `examples/fastapi_usage.py`. Use `LeaseManager` and
`MemoryBackend` in synchronous applications such as Flask; use
`AsyncLeaseManager` and `AsyncMemoryBackend` in FastAPI or any asyncio app.

## Status

Implemented: synchronous and native-async lease APIs, ownership validation,
expiration, renewal, release, and in-memory backends. Redis is an explicit
placeholder; the remaining distributed backends are roadmap work.
