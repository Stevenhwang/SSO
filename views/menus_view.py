from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import Menu


class MenusView(HTTPMethodView):
    async def get(self, request):
        menus = await Menu.search(**request.ctx.query)
        return json(dict(data=[menu.to_dict() for menu in menus],
                         count=len(menus), code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        if not data.get('name'):
            return json(dict(code=-1, msg='关键参数不能为空'))
        er = await Menu.get_or_none(name=data.get('name'))
        if er:
            return json(dict(code=-1, msg='此菜单已注册！'))
        nr = Menu(**data)
        await nr.save()
        return json(dict(code=0, msg='菜单创建成功!'))


class MenuView(HTTPMethodView):
    async def put(self, request, mid):
        data = request.json
        m = await Menu.get_or_none(id=mid)
        if not m:
            return json(dict(code=-1, msg='菜单不存在'))
        for k, v in data.items():
            setattr(m, k, v)
        await m.save()
        return json(dict(code=0, msg='编辑成功'))

    async def delete(self, request, mid):
        m = await Menu.get_or_none(id=mid)
        if not m:
            return json(dict(code=-1, msg='菜单不存在'))
        await m.delete()
        return json(dict(code=0, msg='删除成功'))

    async def patch(self, request, mid):
        # 菜单启用禁用
        m = await Menu.get_or_none(id=mid)
        if not m:
            return json(dict(code=-1, msg='菜单不存在'))
        status = m.status
        if status:
            m.status = False
            await m.save()
            return json(dict(code=0, msg='菜单禁用成功'))
        else:
            m.status = True
            await m.save()
            return json(dict(code=0, msg='菜单启用成功'))
