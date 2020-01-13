from sanic.views import HTTPMethodView
from sanic.response import json


class LogoutView(HTTPMethodView):
    async def post(self, request):
        # 登出
        uid = request.ctx.user_id
        await request.app.redis.execute('delete', f"uid_{uid}_auth_token")
        return json(dict(code=0, msg='注销成功'))
