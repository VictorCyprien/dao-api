import json

from flask import Flask, request, jsonify, g
from flask_smorest import Api

from .config import Config
from helpers.logging_file import Logger


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
    

    rest_api = Api(app)

    from .views.data import data_blp
    rest_api.register_blueprint(data_blp)

    app.logger.debug(f"URL Map: \n{app.url_map}")
    return app
