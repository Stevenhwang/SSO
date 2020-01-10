from sanic.response import json
from sanic.views import HTTPMethodView
from settings import redis_settings


class WhiteUrlView(HTTPMethodView):
    wu_key = redis_settings.get('WHITE_URL_KEY')

    async def get(self, request):
        wu_dict = await request.app.redis.hgetall(WhiteUrlView.wu_key)
        wu_list = []
        for k, v in wu_dict.items():
            wu_list.append(dict(request_uri=k.decode(), real_uri=v.decode()))
        return json(dict(code=0, msg='获取成功', data=wu_list))

    async def post(self, request):
        data = request.json
        request_uri = data.get('request_uri')
        real_uri = data.get('real_uri')
        if not request_uri or not real_uri:
            return json(dict(code=-1, msg='关键参数不能为空!'))
        await request.app.redis.hset(WhiteUrlView.wu_key, request_uri, real_uri)
        return json(dict(code=0, msg='成功'))

    async def delete(self, request):
        data = request.json
        request_uri = data.get('request_uri')
        await request.app.redis.hdel(WhiteUrlView.wu_key, request_uri)
        return json(dict(code=0, msg='删除成功'))
