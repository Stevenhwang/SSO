from sanic import Blueprint
from .common import common_bp
from .login import login_bp
from .auth_check import auth_check_bp

api = Blueprint.group(common_bp, login_bp, auth_check_bp)
