from environs import Env

Env.read_env()

from .config import config

# Validate config
config.validate()

# Initialize flask app
from .app import create_flask_app, setup_db
app = create_flask_app(config)

# Connect to postgrey
setup_db(app, config)
