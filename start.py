from sanic import Sanic
from sanic.response import json
import logging
from tortoise.contrib.sanic import register_tortoise
from settings import server_settings, db_settings
from routers import routers
from utils.jwt_token import AuthToken
from utils.redis_conn import redis_conn

logging.basicConfig(level=logging.DEBUG)
app = Sanic(name='admin')
app.config.update(server_settings)
app.config.update(db_settings)


@app.middleware('request')
async def use_auth(request):
    token = request.headers.get('Auth-Token')
    user_info = AuthToken().decode_token(token)
    if not token:
        return json(dict(code=-1, msg="请登录！"), status=401)
    if not user_info:
        return json(dict(code=-1, msg="Token失效!"), status=401)
    temp_token = await redis_conn('get', f"uid_{user_info.get('user_id')}_auth_token")
    if not temp_token or temp_token.decode("utf-8") != token:
        return json(dict(code=-1, msg="Token失效!"), status=401)
    request.ctx.user_id = user_info.get('user_id')
    request.ctx.username = user_info.get('username')
    request.ctx.is_super = user_info.get('is_super')


@app.middleware('request')
async def user_parse_query(request):
    request.ctx.query = eval(str(request.args).replace('[', '').replace(']', ''))


for router in routers:
    app.add_route(*router, version=2)

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

if __name__ == "__main__":
    app.run(host=app.config.SERVER_HOST,
            port=app.config.SERVER_PORT,
            debug=app.config.SERVER_DEBUG
            )
