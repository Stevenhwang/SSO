from sanic import Sanic
import logging
from tortoise.contrib.sanic import register_tortoise
from settings import server_settings, db_settings
from routers import routers

logging.basicConfig(level=logging.DEBUG)
app = Sanic(name='admin')
app.config.update(server_settings, db_settings)


@app.middleware('request')
async def add_key(request):
    request.ctx.foo = 'bar'


@app.middleware('request')
async def parse_query(request):
    request.ctx.query = eval(str(request.args).replace('[', '').replace(']', ''))


for router in routers:
    app.add_route(*router, version=2)

register_tortoise(
    app,
    db_url=f"mysql://{app.config.DB_USER}:{app.config.DB_PASS}@{app.config.DB_HOST}:{app.config.DB_PORT}/{app.config.DB_NAME}",
    modules={"models": ["models.admin"]},
    generate_schemas=True
)

if __name__ == "__main__":
    app.run(host=app.config.SERVER_HOST,
            port=app.config.SERVER_PORT,
            debug=app.config.SERVER_DEBUG
            )
