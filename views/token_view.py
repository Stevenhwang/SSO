from sanic.response import json
from sanic.views import HTTPMethodView
from utils.redis_conn import redis_conn


class TokenView(HTTPMethodView):
    def post(self, request):
        # 清除token
        data = request.json
        users = data.get("users")
        for uid in users:
            await redis_conn('delete', f"uid_{uid}_auth_token")
        return json(dict(code=0, msg='清除token成功!'))

    def put(self, request):
        # 长期token
        data = request.json
        users = data.get("users")
        exp = 365
        for uid in users:
            await redis_conn('expire', f"uid_{uid}_auth_token", 86400 * exp)
        return json(dict(code=0, msg='设置长期token成功!'))
