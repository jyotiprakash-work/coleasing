from time import sleep

import pytest

from coleasing import LeaseLostError, LeaseManager, LeaseNotOwnedError, LeaseUnavailableError, MemoryBackend


@pytest.fixture
def manager():
    return LeaseManager(MemoryBackend(), default_ttl=1)


def test_acquire_and_release(manager):
    lease = manager.acquire("report", owner_id="worker-a")
    assert lease.key == "report"
    lease.release()
    assert manager.try_acquire("report", owner_id="worker-b") is not None


def test_cannot_acquire_held_lease(manager):
    manager.acquire("report", owner_id="worker-a")
    with pytest.raises(LeaseUnavailableError):
        manager.acquire("report", owner_id="worker-b")
    assert manager.try_acquire("report", owner_id="worker-b") is None


def test_only_owner_can_release(manager):
    lease = manager.acquire("report", owner_id="worker-a")
    impostor = type(lease)(manager, "report", "worker-b", lease.expires_at)
    with pytest.raises(LeaseNotOwnedError):
        impostor.release()
    lease.release()


def test_expired_lease_becomes_available():
    manager = LeaseManager(MemoryBackend(), default_ttl=0.01)
    manager.acquire("report", owner_id="worker-a")
    sleep(0.02)
    assert manager.try_acquire("report", owner_id="worker-b") is not None


def test_renew_updates_expiration(manager):
    lease = manager.acquire("report", owner_id="worker-a")
    previous = lease.expires_at
    lease.renew(ttl=2)
    assert lease.expires_at > previous


def test_renew_after_expiry_loses_ownership():
    manager = LeaseManager(MemoryBackend(), default_ttl=0.01)
    lease = manager.acquire("report", owner_id="worker-a")
    sleep(0.02)
    with pytest.raises(LeaseLostError):
        lease.renew()
