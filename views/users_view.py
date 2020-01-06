from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import User


class UsersView(HTTPMethodView):
    async def get(self, request):
        users = await User.search(**request.ctx.query)
        return json(dict(data=[user.to_dict() for user in users], code=0, msg="成功"))

    async def post(self, request):
        data = request.json
        u = User(**data)
        await u.save()
        return json(dict(code=0, msg="成功"))
