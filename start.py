from sanic import Sanic
from sanic.response import text
from sanic.exceptions import NotFound
import logging
from tortoise.contrib.sanic import register_tortoise
from settings import server_settings, db_settings
from blueprints import api
import aioredis
from settings import redis_settings
# from tasks.log_sub import log_sub

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

# 初始化数据库连接
register_tortoise(
    app,
    config=db_config,
    generate_schemas=True
)


# 初始化redis连接池
@app.listener('before_server_start')
async def init_redis_pool(app, loop):
    redis = await aioredis.create_redis_pool(
        f"redis://{redis_settings.get('REDIS_HOST')}:{redis_settings.get('REDIS_PORT')}",
        password=redis_settings.get('REDIS_PASS'),
        db=redis_settings.get('REDIS_DB')
    )
    app.redis = redis


# 订阅redis日志任务(是否废弃？)
# FIXME
# @app.listener('after_server_start')
# async def sub_redis_log(app, loop):
#     channel, = await app.redis.subscribe('ops_log')
#     app.add_task(log_sub(channel))


# 关闭redis连接池
@app.listener('before_server_stop')
async def close_redis_pool(app, loop):
    app.redis.close()
    await app.redis.wait_closed()


# 捕捉404路由
@app.exception(NotFound)
async def ignore_404s(request, exception):
    return text(f"Too naive!!! {request.path} is not allowed, baby!")

if __name__ == "__main__":
    app.run(host=app.config.SERVER_HOST,
            port=app.config.SERVER_PORT,
            debug=app.config.SERVER_DEBUG
            )
