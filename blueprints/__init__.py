from sanic import Blueprint
from .common import common_bp
from .login import login_bp
from .gateway import gateway_bp

api = Blueprint.group(common_bp, login_bp, gateway_bp)
