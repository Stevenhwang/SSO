from sanic.response import json
from sanic.views import HTTPMethodView
from models.admin import SysLog


class LogsView(HTTPMethodView):
    async def get(self, request):
        logs = await SysLog.search(**request.ctx.query)
        return json(dict(data=[log.to_dict(exclude=['updated_at']) for log in logs],
                         count=len(logs), code=0, msg="成功"))
