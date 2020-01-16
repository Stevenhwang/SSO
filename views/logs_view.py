from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import SysLog


class LogsView(HTTPMethodView):
    # 系统日志查询接口
    async def get(self, request):
        logs, count = await SysLog.search(**request.ctx.query)
        return json(dict(data=[log.to_dict(exclude=['updated_at']) for log in logs],
                         count=count, code=0, msg="成功"))
