"""Redis backend placeholder.

Redis support is planned as the next backend.  It must use atomic scripts or
transactions so owner-token validation and TTL changes occur together.
"""

from __future__ import annotations

from coleasing.core.interface import LeaseBackend


class RedisBackend(LeaseBackend):
    """Reserved extension point for the production Redis implementation."""

    def __init__(self, *_: object, **__: object) -> None:
        raise NotImplementedError("RedisBackend is not implemented yet; use MemoryBackend for now")

    def acquire(self, *_: object, **__: object):
        raise NotImplementedError

    def renew(self, *_: object, **__: object):
        raise NotImplementedError

    def release(self, *_: object, **__: object):
        raise NotImplementedError

    def get(self, *_: object, **__: object):
        raise NotImplementedError
