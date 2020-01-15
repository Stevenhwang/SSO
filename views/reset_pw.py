from sanic.views import HTTPMethodView
from sanic.response import json
from models.admin import User
from utils.tools import gen_md5


class ResetPWView(HTTPMethodView):
    async def post(self, request):
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
        await request.app.redis.execute('del', f"uid_{uid}_auth_token")  # 清除token
        return json(dict(code=0, msg='修改密码成功'))
