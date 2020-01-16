from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import Function


class FunctionsView(HTTPMethodView):
    async def get(self, request):
        functions, count = await Function.search(**request.ctx.query)
        return json(dict(data=[function.to_dict(exclude=['roles']) for function in functions],
                         count=count, code=0, msg="成功"))

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
        f = await Function.get_or_none(id=fid)
        if not f:
            return json(dict(code=-1, msg='权限不存在'))
        for i in ['name', 'uri', 'method_type']:
            if i not in data.keys():
                return json(dict(code=-1, msg='关键参数不能为空'))
        for k, v in data.items():
            if k == 'name':
                ef = await Function.get_or_none(name=v)
                if ef and f.name != v:
                    return json(dict(code=-1, msg='权限名称有重复！'))
            setattr(f, k, v)
        await f.save()
        return json(dict(code=0, msg='更新成功'))

    async def delete(self, request, fid):
        m = await Function.get_or_none(id=fid)
        if not m:
            return json(dict(code=-1, msg='权限不存在'))
        await m.delete()
        return json(dict(code=0, msg='删除成功'))
