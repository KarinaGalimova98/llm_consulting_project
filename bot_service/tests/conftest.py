import fakeredis.aioredis
import pytest

from app.bot import handlers


@pytest.fixture
async def fake_redis(mocker):
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    mocker.patch.object(handlers, "get_redis", return_value=redis)
    return redis