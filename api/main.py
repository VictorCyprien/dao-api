from environs import Env

Env.read_env()

from .config import config

# Validate config
config.validate()

# Initialize flask app
from .app import create_flask_app, connect_to_mongo
app = create_flask_app(config)

# Connect to mongo
connect_to_mongo(config, app)
