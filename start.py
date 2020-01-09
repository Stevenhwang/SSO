from sanic import Sanic
import logging
from tortoise.contrib.sanic import register_tortoise
from settings import server_settings, db_settings
from blueprints import api
import aioredis
from settings import redis_settings
from tasks.log_sub import log_sub

logging.basicConfig(level=logging.DEBUG)
app = Sanic(name='admin')
app.config.update(server_settings)
app.config.update(db_settings)

app.blueprint(api)

db_config = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'host': app.config.DB_HOST,
                'port': app.config.DB_PORT,
                'user': app.config.DB_USER,
                'password': app.config.DB_PASS,
                'database': app.config.DB_NAME
            }
        }
    },
    'apps': {
        'models': {
            'models': ["models.admin"],
            'default_connection': 'default',
        }
    }
}

register_tortoise(
    app,
    config=db_config,
    generate_schemas=True
)

# 初始化redis
redis = None


# 初始化redis连接池
@app.listener('before_server_start')
async def init_redis_pool(app, loop):
    print('before_server_start')
    global redis
    redis = await aioredis.create_redis_pool(
        f"redis://{redis_settings.get('REDIS_HOST')}:{redis_settings.get('REDIS_PORT')}",
        password=redis_settings.get('REDIS_PASS'),
        db=redis_settings.get('REDIS_DB')
    )


# 订阅redis日志
@app.listener('after_server_start')
async def sub_redis_log(app, loop):
    print('after_server_start')
    channel, = await redis.subscribe('ops_log')
    app.add_task(log_sub(channel))


# 关闭redis连接池
@app.listener('before_server_stop')
async def close_redis_pool(app, loop):
    print('before_server_stop')
    redis.close()
    await redis.wait_closed()


if __name__ == "__main__":
    app.run(host=app.config.SERVER_HOST,
            port=app.config.SERVER_PORT,
            debug=app.config.SERVER_DEBUG
            )
