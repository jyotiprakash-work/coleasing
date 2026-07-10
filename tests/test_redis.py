import pytest

from coleasing.backends.redis import RedisBackend


def test_redis_backend_is_explicitly_not_implemented():
    with pytest.raises(NotImplementedError):
        RedisBackend()
