from sanic import Blueprint
from sanic.response import json
from routers import routers
from utils.jwt_token import AuthToken
from utils.redis_conn import redis_conn

common_bp = Blueprint('common', url_prefix='/', version=2)

for router in routers:
    common_bp.add_route(*router)


@common_bp.middleware('request')
async def use_auth(request):
    # auth middleware
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
    # parse query args middleware
    request.ctx.query = eval(str(request.args).replace('[', '').replace(']', ''))
