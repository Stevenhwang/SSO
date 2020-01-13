from sanic.response import json
from sanic.views import HTTPMethodView
from settings import redis_settings
import ujson


class BackServiceView(HTTPMethodView):
    bs_key = redis_settings.get('BACK_SERVICE_KEY')

    async def get(self, request):
        bs_dict = await request.app.redis.hgetall(BackServiceView.bs_key)
        bs_list = []
        for k in bs_dict.keys():
            bs_list.append({'end_point': k.decode(), 'name': ujson.loads(bs_dict[k].decode()).get(
                'name'), 'url': ujson.loads(bs_dict[k].decode()).get('url')})
        return json(dict(code=0, msg='获取服务成功', data=bs_list))

    async def post(self, request):
        data = request.json
        bs_name = data.get('name')
        bs_url = data.get('url')
        bs_end_point = data.get('end_point')

        if not bs_name or not bs_url or not bs_end_point:
            return json(dict(code=-1, msg='参数不能为空'))

        await request.app.redis.hset(BackServiceView.bs_key,
                                     bs_end_point, ujson.dumps(dict(name=bs_name, url=bs_url)))
        return json(dict(code=0, msg='创建成功'))

    async def delete(self, request):
        data = request.json
        bs_end_point = data.get('end_point')

        await request.app.redis.hdel(BackServiceView.bs_key, bs_end_point)
        return json(dict(code=0, msg='删除成功'))
