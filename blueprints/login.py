from sanic.response import json
from sanic import Blueprint
from models.admin import User
from utils.tools import gen_md5
from utils.jwt_token import AuthToken
import pyotp
from datetime import datetime

login_bp = Blueprint('login', url_prefix='/login', version=2)


@login_bp.route('/', methods=['POST'])
async def login(request):
    data = request.json
    username = data.get('username')
    password = data.get('password')
    dynamic = data.get('dynamic')
    # token 过期时间1天
    exp = 1

    if not username or not password:
        return json(dict(code=1, msg='账号密码不能为空'))
    user = await User.get_or_none(name=username)
    if not user:
        return json(dict(code=2, msg='账号不存在'))
    if user.password != gen_md5(password):
        return json(dict(code=3, msg='密码错误'))
    if not user.status:
        return json(dict(code=4, msg='账号被禁用'))
    # 如果被标记为必须动态验证切没有输入动态密钥，则跳转到输入密钥的地方
    if user.google_key:
        if not dynamic:
            # 第一次不带MFA的认证
            return json(dict(code=5, msg='跳转二次认证'))
        else:
            # 二次认证
            t_otp = pyotp.TOTP(user.google_key)
            if t_otp.now() != str(dynamic):
                return json(dict(code=6, msg='MFA错误'))
    # 生成token
    token_info = dict(user_id=user.id, username=user.name,
                      email=user.email, is_super=user.is_super)
    gen_token = AuthToken()
    auth_token = gen_token.encode_token(**token_info)
    auth_token.decode()
    # 将token写入redis
    await request.app.redis.execute('set', f"uid_{user.id}_auth_token", auth_token)
    # 设置过期时间
    await request.app.redis.execute('expire', f"uid_{user.id}_auth_token", 86400 * exp)
    login_ip_list = request.headers.get("X-Forwarded-For")
    if login_ip_list:
        user.last_login_ip = login_ip_list.split(",")[0]
    user.last_login_time = datetime.now()
    await user.save()
    return json(dict(code=0, auth_token=auth_token.decode(), username=user.name, msg='登录成功'))
