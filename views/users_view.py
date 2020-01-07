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
        return json(dict(data=[user.to_dict(exclude=['password', 'google_key']) for user in users],
                         count=users.count(), code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        for f in ['name', 'email']:
            if f not in data.keys():
                return json(dict(code=-1, msg='关键参数不能为空'))
        eu = await User.filter(Q(name=data['name']) | Q(email=data['email']))
        if eu:
            return json(dict(code=-1, msg='用户名或邮箱有重复！'))
        password = '7d491c440ba46ca20fde0c5be1377aec' if not data['password'] else gen_md5(data['password'])
        mfa = base64.b32encode(bytes(
            str(shortuuid.uuid() + shortuuid.uuid())[:-9], encoding="utf-8")).decode("utf-8")
        data.update(dict(password=password, mfa=mfa))
        nu = User(**data)
        await nu.save()
        return json(dict(code=0, msg=f'如果没填写密码则新用户{nu.name}密码为：shenshuo'))
