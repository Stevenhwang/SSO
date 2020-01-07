from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import Role, Component, Menu


class AuthView(HTTPMethodView):
    async def get(self, request):
        # 前端携带token查询用户的菜单和组件，如果是superuser，给出所有菜单和组件
        uid = request.ctx.user_id  # user_id
        if request.ctx.is_super:
            page = {"all": True}
            component = {"all": True}
            menus = await Menu.all()
            components = await Component.all()
            for m in menus:
                page.update({m.name: True})
            for c in components:
                component.update({c.name: True})
            rules = dict(component=component, page=page)
        else:
            page = {"all": False}
            component = {"all": False}
            roles = await Role.filter(users=uid).values_list('id', flat=True)
            if roles:
                menus = await Menu.filter(roles__in=roles)
                components = await Component.filter(roles__in=roles)
                for m in menus:
                    page.update({m.name: m.status})
                for c in components:
                    component.update({c.name: c.status})
            rules = dict(component=component, page=page)
        return json(dict(code=0, msg='获取成功', data=dict(rules=rules)))
