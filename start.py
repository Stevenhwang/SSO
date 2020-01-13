from sanic import Sanic
from sanic.response import text
from sanic.exceptions import NotFound, MethodNotSupported
import logging
from tortoise.contrib.sanic import register_tortoise
from settings import server_settings, db_config
from blueprints import api
import aioredis
from settings import redis_settings

logging.basicConfig(level=logging.DEBUG)
app = Sanic(name='admin')
app.blueprint(api)

register_tortoise(
    app,
    config=db_config,
    generate_schemas=True
)


@app.listener('before_server_start')
async def init_redis_pool(app, loop):
    redis = await aioredis.create_redis_pool(
        f"redis://{redis_settings.get('REDIS_HOST')}:{redis_settings.get('REDIS_PORT')}",
        password=redis_settings.get('REDIS_PASS'),
        db=redis_settings.get('REDIS_DB')
    )
    app.redis = redis


@app.listener('before_server_stop')
async def close_redis_pool(app, loop):
    app.redis.close()
    await app.redis.wait_closed()


@app.exception(NotFound, MethodNotSupported)
async def ignore_404s(request, exception):
    return text(f"Too naive!!! {request.method} {request.path} is not allowed, baby!")

app.static('/api-doc', './api-doc/api-doc.html', content_type="text/html; charset=utf-8")

if __name__ == "__main__":
    app.run(**server_settings)
