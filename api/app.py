import json

from flask import Flask, request, jsonify, g
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import redis
from redis import StrictRedis
from rq import Queue
from flask_caching import Cache
from pydantic import ValidationError

from . import Base
from .config import Config

from helpers.logging_file import Logger

# Create a cache instance that can be imported and used across the app
cache = Cache()


def setup_db(app: Flask, config: Config):
    db = SQLAlchemy(model_class=Base)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{config.POSTGRESQL_USERNAME}:{config.POSTGRESQL_PASSWORD}@{config.POSTGRESQL_URI}/{config.POSTGRESQL_DB}"
    app.db = db
    db.init_app(app)

    from .models.user import User
    with app.app_context():
        db.create_all()


def setup_redis(config: Config):
    return redis.StrictRedis(
        host=config.REDIS_URI, 
        port=config.REDIS_PORT, 
        db=0, 
        decode_responses=True
    )


def setup_cache(app: Flask, config: Config):
    """
    Configure Flask-Caching for the application.
    
    Args:
        app: Flask application instance
        config: Application configuration
        
    Returns:
        Initialized Cache instance
    """
    app.logger.info("Setting up caching...")
    cache_config = config.cache_config
    app.config.update(cache_config)
    # Initialize the cache with the app
    cache.init_app(app)
    app.logger.info(f"Cache initialized with type: {cache_config['CACHE_TYPE']}")
    return cache


def setup_pydantic(app: Flask):
    """
    Configure Pydantic for request validation.
    This enables automatic validation of request data using Pydantic models.
    """
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Pydantic validation errors and return appropriate response"""
        return jsonify({
            "code": 422,
            "message": "Validation error",
            "status": "Unprocessable Entity", 
            "errors": error.errors()
        }), 422
    
    return app


def setup_jwt(app: Flask, redis_client: StrictRedis):
    jwt = JWTManager(app)
    jwt_redis_blocklist = redis_client

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        token_in_redis = jwt_redis_blocklist.get(jti)
        return token_in_redis is not None

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify(code=401, message="Token expired", status="Unauthorized"), 401

    @jwt.unauthorized_loader
    def my_missing_token_callback(callback):
        return jsonify(code=401, message="Not Authenticated", status="Unauthorized"), 401
    
    @jwt.invalid_token_loader
    def my_invalid_token(callback):
        return jsonify(code=401, message="Invalid token", status="Unauthorized"), 401
    
    @jwt.revoked_token_loader
    def my_missing_token_callback(jwt_header, jwt_payload):
        return jsonify(code=401, message="Not Authenticated", status="Unauthorized"), 401
    
    return jwt_redis_blocklist


def setup_cors(app: Flask, config: Config, allowed_origins: str):
    # Setup CORS with specific configuration
    if allowed_origins == "*":
        resources = {r"/*": {"origins": "*"}}
    else:
        allowed_list = [origin.strip() for origin in allowed_origins.split(',')]
        resources = {r"/*": {"origins": allowed_list}}
        
    cors = CORS(
        app,
        resources=resources,
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    return cors


def create_flask_app(config: Config) -> Flask:
    # Create the Flask App
    app = Flask(__name__)
    # If we don't set this, there will be a redirection and the access token will go away
    app.url_map.strict_slashes = False
    app.logger = Logger()

    # Initialize CORS
    allowed_origins = config.CORS_ALLOWED_ORIGINS if hasattr(config, 'CORS_ALLOWED_ORIGINS') else "*"
    setup_cors(app, config, allowed_origins)

    # Initialize Pydantic
    setup_pydantic(app)

    """ Log each API/APP request
    """
    @app.before_request
    def before_request():
        """ Log every requests """
        app.logger.info(f'>-- {request.method} {request.path} from {request.remote_addr}')
        app.logger.debug(f'       Args: {request.args.to_dict()}')
        #app.logger.debug(f'    Headers: {request.headers.to_wsgi_list()}')
        app.logger.debug(f'       Body: {request.get_data()}')

    @app.after_request
    def after_request(response):
        """ Log response status, after every request. """
        app.logger.info(f'--> Response status: {response.status}')
        cors_origin = request.headers.get('Origin')
        if allowed_origins == "*":
            response.headers.add('Access-Control-Allow-Origin', cors_origin)
        elif cors_origin:
            allowed_list = [origin.strip() for origin in allowed_origins.split(',')]
            if cors_origin in allowed_list:
                response.headers.add('Access-Control-Allow-Origin', cors_origin)

        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        #app.logger.debug(f'      Body: {response.json}')
        return response

    app.logger.info('.------------------.')
    app.logger.info('|     DAO - API    |')
    app.logger.info('.------------------.')

    # Update config from given one
    app.config.update(**config.json)
    app.logger.info(f"Config: {json.dumps(config.json, indent=4)}")
    app.debug = config.FLASK_ENV

    # Index routes
    @app.route('/')
    def index():
        res = {
            'name': config.SERVICE_NAME,
        }
        return jsonify(res)
    
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    # Add Redis
    redis_client = setup_redis(config)
    
    # Set token auth and redis blacklist
    jwt_redis_blocklist = setup_jwt(app, redis_client)
    app.extensions['jwt_redis_blocklist'] = jwt_redis_blocklist

    # Add Redis Queue
    app.queue = Queue(connection=redis_client)
    
    # Initialize caching
    setup_cache(app, config)

    # Add REST API
    rest_api = Api(app)

    # Add Blueprints
    from .views.auth import auth_blp
    rest_api.register_blueprint(auth_blp)

    from .views.users import users_blp
    rest_api.register_blueprint(users_blp)

    from .views.daos import daos_blp
    rest_api.register_blueprint(daos_blp)

    from .views.treasury import treasury_blp
    rest_api.register_blueprint(treasury_blp)

    # Import OAuth blueprints from their respective files
    from .views.auth.discord_oauth import discord_oauth_blp
    rest_api.register_blueprint(discord_oauth_blp)

    from .views.auth.twitter_oauth import twitter_oauth_blp
    rest_api.register_blueprint(twitter_oauth_blp)

    from .views.auth.telegram_auth import telegram_auth_blp
    rest_api.register_blueprint(telegram_auth_blp)
    
    from .views.auth.social_connections_view import social_connections_blp
    rest_api.register_blueprint(social_connections_blp)
    
    from .views.proposals import proposals_blp
    rest_api.register_blueprint(proposals_blp)
    
    # from .views.data import data_blp
    # rest_api.register_blueprint(data_blp)

    app.logger.debug(f"URL Map: \n{app.url_map}")
    return app
