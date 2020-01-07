from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import Function


class FunctionsView(HTTPMethodView):
    async def get(self, request):
        functions = await Function.search(**request.ctx.query)
        return json(dict(data=[function.to_dict(exclude=['roles']) for function in functions],
                         count=len(functions), code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        for f in ['name', 'uri', 'method_type']:
            if f not in data.keys():
                return json(dict(code=-1, msg='关键参数不能为空'))
        er = await Function.get_or_none(name=data.get('name'))
        if er:
            return json(dict(code=-1, msg='此权限已注册！'))
        nr = Function(**data)
        await nr.save()
        return json(dict(code=0, msg='权限创建成功!'))


class FunctionView(HTTPMethodView):
    async def put(self, request, fid):
        data = request.json
        m = await Function.get_or_none(id=fid)
        if not m:
            return json(dict(code=-1, msg='权限不存在'))
        for k, v in data.items():
            setattr(m, k, v)
        await m.save()
        return json(dict(code=0, msg='编辑成功'))

    async def delete(self, request, fid):
        m = await Function.get_or_none(id=fid)
        if not m:
            return json(dict(code=-1, msg='权限不存在'))
        await m.delete()
        return json(dict(code=0, msg='删除成功'))

    async def patch(self, request, fid):
        # 权限启用禁用
        m = await Function.get_or_none(id=fid)
        if not m:
            return json(dict(code=-1, msg='权限不存在'))
        status = m.status
        if status:
            m.status = False
            await m.save()
            return json(dict(code=0, msg='权限禁用成功'))
        else:
            m.status = True
            await m.save()
            return json(dict(code=0, msg='权限启用成功'))
