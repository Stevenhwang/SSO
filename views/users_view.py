from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import User
from utils.tools import gen_md5
from utils.redis_conn import redis_conn
from tortoise.query_utils import Q
import base64
import shortuuid


class UsersView(HTTPMethodView):
    async def get(self, request):
        users = await User.search(**request.ctx.query)
        return json(dict(data=[user.to_dict(exclude=['password', 'google_key', 'roles']) for user in users],
                         count=len(users), code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        for f in ['name', 'email']:
            if f not in data.keys():
                return json(dict(code=-1, msg='关键参数不能为空'))
        eu = await User.filter(Q(name=data['name']) | Q(email=data['email']))
        if eu:
            return json(dict(code=-1, msg='用户名或邮箱有重复！'))
        password = '7d491c440ba46ca20fde0c5be1377aec' if not data.get('password') else gen_md5(data['password'])
        mfa = base64.b32encode(bytes(
            str(shortuuid.uuid() + shortuuid.uuid())[:-9], encoding="utf-8")).decode("utf-8")
        data.update(dict(password=password, mfa=mfa))
        nu = User(**data)
        await nu.save()
        return json(dict(code=0, msg=f'如果没填写密码则新用户{nu.name}密码为：shenshuo'))


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
            await redis_conn('delete', f"uid_{u.id}_auth_token")  # 禁用用户的同时清除掉他的token
            return json(dict(code=0, msg='用户禁用成功'))
        else:
            u.status = True
            await u.save()
            return json(dict(code=0, msg='用户启用成功'))
