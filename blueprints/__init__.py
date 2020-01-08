from sanic import Blueprint
from .common import common_bp
from .login import login_bp

api = Blueprint.group(common_bp, login_bp)
