from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import User
from utils.tools import gen_md5
from tortoise.query_utils import Q
import base64
import shortuuid


class UsersView(HTTPMethodView):
    async def get(self, request):
        users, count = await User.search(**request.ctx.query)
        return json(dict(data=[user.to_dict(exclude=['password', 'roles']) for user in users],
                         count=count, code=0, msg="成功"))

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
        return json(dict(code=0, msg=f'如果没填写密码则新用户{nu.name}默认密码为：12345678'))


class UserView(HTTPMethodView):
    async def put(self, request, uid):
        data = request.json
        u = await User.get_or_none(id=uid)
        if not u:
            return json(dict(code=-1, msg='用户不存在'))
        for f in ['name', 'email']:
            if f not in data.keys():
                return json(dict(code=-1, msg='关键参数不能为空'))
        for k, v in data.items():
            if k == 'name':
                eu = await User.get_or_none(name=v)
                if eu and u.name != v:
                    return json(dict(code=-1, msg='用户名有重复！'))
            if k == 'email':
                eu = await User.get_or_none(email=v)
                if eu and u.email != v:
                    return json(dict(code=-1, msg='邮箱有重复！'))
            if k == 'status' and not v:
                await request.app.redis.execute('del', f"uid_{u.id}_auth_token")  # 清除token
            if k == 'google_key':
                v = base64.b32encode(bytes(str(shortuuid.uuid() + shortuuid.uuid())[:-9],
                                           encoding="utf-8")).decode("utf-8") if v else ''
            if k == 'password':
                v = gen_md5(v) if v else u.password
                await request.app.redis.execute('del', f"uid_{u.id}_auth_token")  # 清除token
            setattr(u, k, v)
        await u.save()
        return json(dict(code=0, msg='更新成功'))

    async def delete(self, request, uid):
        u = await User.get_or_none(id=uid)
        if not u:
            return json(dict(code=-1, msg='用户不存在'))
        await request.app.redis.execute('del', f"uid_{u.id}_auth_token")  # 清除token
        await u.delete()
        return json(dict(code=0, msg='删除成功'))
