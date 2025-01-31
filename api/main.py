from environs import Env

Env.read_env()

from .config import config

# Initialize flask app
from .app import create_flask_app
app = create_flask_app(config)
