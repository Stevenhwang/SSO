from sanic import Sanic
import logging
from tortoise.contrib.sanic import register_tortoise
from settings import server_settings, db_settings
from blueprints.common import common_bp
from blueprints.login import login_bp

logging.basicConfig(level=logging.DEBUG)
app = Sanic(name='admin')
app.config.update(server_settings)
app.config.update(db_settings)

app.blueprint(common_bp)
app.blueprint(login_bp)

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
