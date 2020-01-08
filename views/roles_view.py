from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import Role, User, Component, Function, Menu


class RolesView(HTTPMethodView):
    async def get(self, request):
        roles = await Role.search(**request.ctx.query)
        return json(dict(data=[role.to_dict(exclude=['users', 'components', 'menus', 'functions']) for role in roles],
                         count=len(roles), code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        if not data.get('name'):
            return json(dict(code=-1, msg='关键参数不能为空'))
        er = await Role.get_or_none(name=data.get('name'))
        if er:
            return json(dict(code=-1, msg='此角色已注册！'))
        nr = Role(**data)
        await nr.save()
        return json(dict(code=0, msg='角色创建成功!'))


class RoleView(HTTPMethodView):
    async def post(self, request, rid):
        # 给角色分配资源
        data = request.json
        user_list = data.get('user_list')
        comp_list = data.get('comp_list')
        menu_list = data.get('menu_list')
        func_list = data.get('func_list')

        r = await Role.get_or_none(id=rid)
        if not r:
            return json(dict(code=-1, msg='角色不存在'))
        if user_list or user_list == []:
            await r.users.clear()
            for uid in user_list:
                await r.users.add(User.get(id=uid))
        if comp_list or comp_list == []:
            await r.components.clear()
            for cid in comp_list:
                await r.components.add(Component.get(id=cid))
        if menu_list or menu_list == []:
            await r.menus.clear()
            for mid in menu_list:
                await r.menus.add(User.get(id=mid))
        if func_list or func_list == []:
            await r.functions.clear()
            for fid in func_list:
                await r.functions.add(Function.get(id=fid))

    async def put(self, request, rid):
        data = request.json
        r = await Role.get_or_none(id=rid)
        if not r:
            return json(dict(code=-1, msg='角色不存在'))
        for k, v in data.items():
            setattr(r, k, v)
        await r.save()
        return json(dict(code=0, msg='编辑成功'))

    async def delete(self, request, rid):
        r = await Role.get_or_none(id=rid)
        if not r:
            return json(dict(code=-1, msg='角色不存在'))
        await r.delete()
        return json(dict(code=0, msg='删除成功'))

    async def patch(self, request, rid):
        # 角色启用禁用
        r = await Role.get_or_none(id=rid)
        if not r:
            return json(dict(code=-1, msg='角色不存在'))
        status = r.status
        if status:
            r.status = False
            await r.save()
            return json(dict(code=0, msg='角色禁用成功'))
        else:
            r.status = True
            await r.save()
            return json(dict(code=0, msg='角色启用成功'))
