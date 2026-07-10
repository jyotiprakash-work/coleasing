# Architecture

`LeaseManager` owns the public API; each backend implements the same four
atomic operations: `acquire`, `renew`, `release`, and `get`. A `Lease` is an
owner-token-bound handle, so one worker cannot renew or release another
worker's lease.

The memory backend is thread-safe and suitable for tests or one-process
development. It is not distributed. Redis, SQL, and MongoDB implementations
will preserve the same contract while providing storage-specific atomicity.

The async API has parallel `AsyncLeaseManager`, `AsyncLease`, and
`AsyncLeaseBackend` types. `AsyncMemoryBackend` uses `asyncio.Lock`, so FastAPI
handlers can acquire and release leases without blocking the event loop.
