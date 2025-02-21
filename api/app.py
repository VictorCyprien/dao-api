import json

from flask import Flask, request, jsonify, g
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

import redis
from redis import StrictRedis
from rq import Queue

from . import Base
from .config import Config

from helpers.logging_file import Logger


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


def create_flask_app(config: Config) -> Flask:
    # Create the Flask App
    app = Flask(__name__)
    app.logger = Logger()

    """ Log each API/APP request
    """

    @app.before_request
    def before_request():
        """ Log every requests """
        app.logger.info(f'>-- {request.method} {request.path} from {request.remote_addr}')
        app.logger.debug(f'       Args: {request.args.to_dict()}')
        app.logger.debug(f'    Headers: {request.headers.to_wsgi_list()}')
        app.logger.debug(f'       Body: {request.get_data()}')

    @app.after_request
    def after_request(response):
        """ Log response status, after every request. """
        app.logger.info(f'--> Response status: {response.status}')
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

    # Add REST API
    rest_api = Api(app)

    # Add Blueprints
    from .views.auth import auth_blp
    rest_api.register_blueprint(auth_blp)

    from .views.users import users_blp
    rest_api.register_blueprint(users_blp)

    from .views.communities import communities_blp
    rest_api.register_blueprint(communities_blp)

    from .views.data import data_blp
    rest_api.register_blueprint(data_blp)

    app.logger.debug(f"URL Map: \n{app.url_map}")
    return app
