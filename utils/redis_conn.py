import aioredis
from settings import redis_settings


async def redis_conn(*args):
    redis = await aioredis.create_connection(
        f"redis://{redis_settings.get('REDIS_HOST')}:{redis_settings.get('REDIS_PORT')}",
        password=redis_settings.get('REDIS_PASS'),
        db=redis_settings.get('REDIS_DB')
    )
    val = await redis.execute(*args)
    redis.close()
    await redis.wait_closed()
    return val
