from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import User
from utils.tools import gen_md5
from tortoise.query_utils import Q
import base64
import shortuuid


class UsersView(HTTPMethodView):
    async def get(self, request):
        users = await User.search(**request.ctx.query)
        return json(dict(data=[user.to_dict(exclude=['password', 'roles']) for user in users],
                         count=len(users), code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        for f in ['name', 'email']:
            if f not in data.keys():
                return json(dict(code=-1, msg='关键参数不能为空'))
        eu = await User.filter(Q(name=data['name']) | Q(email=data['email']))
        if eu:
            return json(dict(code=-1, msg='用户名或邮箱有重复！'))
        password = '25d55ad283aa400af464c76d713c07ad' if not data.get('password') else gen_md5(data['password'])
        mfa = base64.b32encode(bytes(
            str(shortuuid.uuid() + shortuuid.uuid())[:-9], encoding="utf-8")).decode("utf-8")
        data.update(dict(password=password, google_key=mfa))
        nu = User(**data)
        await nu.save()
        return json(dict(code=0, msg=f'如果没填写密码则新用户{nu.name}密码为：12345678'))


class UserView(HTTPMethodView):
    async def put(self, request, uid):
        data = request.json
        u = await User.get_or_none(id=uid)
        if not u:
            return json(dict(code=-1, msg='用户不存在'))
        for k, v in data.items():
            setattr(u, k, v)
        await u.save()
        return json(dict(code=0, msg='编辑成功'))

    async def delete(self, request, uid):
        u = await User.get_or_none(id=uid)
        if not u:
            return json(dict(code=-1, msg='用户不存在'))
        await u.delete()
        return json(dict(code=0, msg='删除成功'))

    async def patch(self, request, uid):
        # 用户启用禁用
        u = await User.get_or_none(id=uid)
        if not u:
            return json(dict(code=-1, msg='用户不存在'))
        status = u.status
        if u.is_super:
            return json(dict(code=-2, msg='系统管理员用户无法禁用!'))
        if status:
            u.status = False
            await u.save()
            await request.app.redis.execute('delete', f"uid_{u.id}_auth_token")  # 禁用用户的同时清除掉他的token
            return json(dict(code=0, msg='用户禁用成功'))
        else:
            u.status = True
            await u.save()
            return json(dict(code=0, msg='用户启用成功'))


class LogoutView(HTTPMethodView):
    async def post(self, request):
        # 登出
        uid = request.ctx.user_id
        await request.app.redis.execute('delete', f"uid_{uid}_auth_token")
        return json(dict(code=0, msg='注销成功'))

    async def put(self, request):
        # 用户重置密码
        data = request.json
        old_password = data.get('old_password')
        new_password1 = data.get('new_password1')
        new_password2 = data.get('new_password2')
        uid = request.ctx.user_id

        if not old_password or not new_password1 or not new_password2:
            return json(dict(code=-1, msg='不能有空值'))

        if new_password1 != new_password2:
            return json(dict(code=-2, msg='两个新密码输入不一致'))

        user = await User.get(id=uid)
        if user.password != gen_md5(old_password):
            return json(dict(code=-3, msg='密码错误'))
        user.password = gen_md5(new_password1)
        await user.save()

        return json(dict(code=0, msg='修改密码成功'))
