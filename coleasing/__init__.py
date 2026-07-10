"""A backend-agnostic API for coordinating renewable leases."""

from .backends.memory import MemoryBackend
from .backends.async_memory import AsyncMemoryBackend
from .core.async_lease import AsyncLease
from .core.async_manager import AsyncLeaseManager
from .core.lease import Lease
from .core.manager import LeaseManager
from .exceptions import LeaseError, LeaseLostError, LeaseNotOwnedError, LeaseUnavailableError

__all__ = [
    "Lease",
    "AsyncLease",
    "AsyncLeaseManager",
    "AsyncMemoryBackend",
    "LeaseError",
    "LeaseLostError",
    "LeaseManager",
    "LeaseNotOwnedError",
    "LeaseUnavailableError",
    "MemoryBackend",
]

__version__ = "0.1.0"
