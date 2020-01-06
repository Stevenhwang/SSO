from sanic import Sanic
import logging
from tortoise.contrib.sanic import register_tortoise
from settings import server_settings, db_settings
from routers import routers
from middlewares import auth, parse_query

logging.basicConfig(level=logging.DEBUG)
app = Sanic(name='admin')
app.config.update(server_settings)
app.config.update(db_settings)


@app.middleware('request')
async def use_auth(request):
    auth(request)
    parse_query(request)


for router in routers:
    app.add_route(*router, version=2)

db_config = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'host': app.config.DB_HOST,
                'port': app.config.DB_PORT,
                'user': app.config.DB_USER,
                'password': app.config.DB_PASS,
                'database': app.config.DB_NAME
            }
        }
    },
    'apps': {
        'models': {
            'models': ["models.admin"],
            'default_connection': 'default',
        }
    }
}

register_tortoise(
    app,
    config=db_config,
    generate_schemas=True
)

if __name__ == "__main__":
    app.run(host=app.config.SERVER_HOST,
            port=app.config.SERVER_PORT,
            debug=app.config.SERVER_DEBUG
            )
