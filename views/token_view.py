from sanic.response import json
from sanic.views import HTTPMethodView


class TokenView(HTTPMethodView):
    async def get(self, request):
        # 查看用户token过期时间
        args = request.ctx.query
        uid = args.get('uid')
        token = await request.app.redis.get(f"uid_{uid}_auth_token")
        if not token:
            return json(dict(code=0, msg='用户未登录!'))
        else:
            ttl = await request.app.redis.execute('ttl', f"uid_{uid}_auth_token")
            if ttl > 0:
                return json(dict(code=0, msg=f'Token: {token.decode()}, TTL: {ttl}秒!'))
            else:
                return json(dict(code=0, msg=f'Token: {token.decode()}, TTL: 长期Token!'))

    async def post(self, request):
        # 清除token
        data = request.json
        users = data.get("users")
        keys = []
        for uid in users:
            keys.append(f"uid_{uid}_auth_token")
        await request.app.redis.execute('del', *keys)
        return json(dict(code=0, msg='清除token成功!'))

    async def put(self, request):
        # 设置长期token
        data = request.json
        users = data.get("users")
        for uid in users:
            await request.app.redis.execute('persist', f"uid_{uid}_auth_token")
        return json(dict(code=0, msg='设置长期token成功!'))
