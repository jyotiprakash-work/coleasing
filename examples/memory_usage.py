"""Run with: python examples/memory_usage.py"""

from coleasing import LeaseManager, MemoryBackend

manager = LeaseManager(MemoryBackend(), default_ttl=30)

with manager.acquire("daily-report") as lease:
    print(f"Processing {lease.key} as {lease.owner_id}")
