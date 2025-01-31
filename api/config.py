from environs import Env


class Config:

    def __init__(self):
        env = Env()

        self.SERVICE_NAME = env.str('SERVICE_NAME', "")
        self.LOGGER_LEVEL = env.str("LOGGER_LEVEL", "DEBUG")

        # FLASK
        self.FLASK_ENV = env.str('FLASK_ENV', 'dev')
        self.JSON_SORT_KEYS = True

        # MONGODB
        self.MONGODB_URI = env.str('MONGODB_URI', 'mongodb://localhost:27017')
        self.MONGODB_DATABASE = env.str('MONGODB_DATABASE', 'dao-users')
        self.MONGODB_CONNECT = False
        self.MONGODB_USERNAME = env.str("MONGODB_USERNAME", "root")
        self.MONGODB_PASSWORD = env.str("MONGODB_PASSWORD", "example")

        # REDIS
        self.REDIS_URI = env.str('REDIS_URI', "localhost")
        self.REDIS_PORT = env.int('REDIS_PORT', 6379)

        # PASSWORD CUSTOM SALT
        self.SECURITY_PASSWORD_SALT = env.str('SECURITY_PASSWORD_SALT', "672B2BB59D2E432E8F3FB10E23B8AECC")

        # OPENAPI
        self.API_TITLE = self.SERVICE_NAME
        self.API_VERSION = env.str('CI_COMMIT_REF_NAME', "dev")
        self.OPENAPI_VERSION = "3.0.2"

    @property
    def logger_config(self):
        return {
            'version': 1,
            'formatters': {
                'color_formatter': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': "%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s"
                }
            },
            'handlers': {
                'console': {
                    'class': 'colorlog.StreamHandler',
                    'level': self.LOGGER_LEVEL,
                    'formatter': 'color_formatter'
                },
            },
            'loggers': {
                'console': {
                    'level': self.LOGGER_LEVEL,
                    'propagate': False,
                    'handlers': ['console']
                }
            }
        }

    @property
    def json(self):
        return {key: self.__getattribute__(key) for key in self.__dir__() if not key.startswith('_') and key.isupper()}


config = Config()
