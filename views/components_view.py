from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import Component


class ComponentsView(HTTPMethodView):
    async def get(self, request):
        components, count = await Component.search(**request.ctx.query)
        return json(dict(data=[components.to_dict(exclude=['roles']) for components in components],
                         count=count, code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        if not data.get('name'):
            return json(dict(code=-1, msg='关键参数不能为空'))
        er = await Component.get_or_none(name=data.get('name'))
        if er:
            return json(dict(code=-1, msg='此组件已注册！'))
        nr = Component(**data)
        await nr.save()
        return json(dict(code=0, msg='组件创建成功!'))


class ComponentView(HTTPMethodView):
    async def put(self, request, cid):
        data = request.json
        if not data.get('name'):
            return json(dict(code=-1, msg='关键参数不能为空'))
        c = await Component.get_or_none(id=cid)
        if not c:
            return json(dict(code=-1, msg='组件不存在'))
        for k, v in data.items():
            if k == 'name':
                ec = await Component.get_or_none(name=v)
                if ec and c.name != v:
                    return json(dict(code=-1, msg='此组件已注册！'))
            setattr(c, k, v)
        await c.save()
        return json(dict(code=0, msg='更新成功'))

    async def delete(self, request, cid):
        c = await Component.get_or_none(id=cid)
        if not c:
            return json(dict(code=-1, msg='组件不存在'))
        await c.delete()
        return json(dict(code=0, msg='删除成功'))
