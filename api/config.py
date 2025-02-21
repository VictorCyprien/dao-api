from environs import Env


class Config:

    def __init__(self):
        env = Env()

        self.SERVICE_NAME = env.str('SERVICE_NAME', "")
        self.LOGGER_LEVEL = env.str("LOGGER_LEVEL", "DEBUG")

        # FLASK
        self.FLASK_ENV = env.str('FLASK_ENV', 'dev')
        self.JSON_SORT_KEYS = True

        # FLASK JWT
        self.JWT_SECRET_KEY = env.str('JWT_SECRET_KEY', None)
        self.JWT_ACCESS_TOKEN_EXPIRES = env.int('JWT_ACCESS_TOKEN_EXPIRES', None)

        # POSTGRESQL
        self.POSTGRESQL_URI = env.str('POSTGRESQL_URI', 'localhost')
        self.POSTGRESQL_USERNAME = env.str("POSTGRESQL_USERNAME", "root")
        self.POSTGRESQL_PASSWORD = env.str("POSTGRESQL_PASSWORD", "example")
        self.POSTGRESQL_DB = env.str("POSTGRESQL_DB", "dao")

        # REDIS
        self.REDIS_URI = env.str('REDIS_URI', "localhost")
        self.REDIS_PORT = env.int('REDIS_PORT', 6379)

        # SMTP
        self.SMTP_SERVER = env.str('SMTP_SERVER', "localhost")
        self.SMTP_PORT = env.int('SMTP_PORT', 1025)
        self.SMTP_USERNAME = env.str('SMTP_USERNAME', "noreply@dao.io")
        self.SMTP_PASSWORD = env.str('SMTP_PASSWORD', "example")

        # PASSWORD CUSTOM SALT
        self.SECURITY_PASSWORD_SALT = env.str('SECURITY_PASSWORD_SALT', "672B2BB59D2E432E8F3FB10E23B8AECC")

        # OPENAPI
        self.API_TITLE = self.SERVICE_NAME
        self.API_VERSION = env.str('CI_COMMIT_REF_NAME', "dev")
        self.OPENAPI_VERSION = "3.0.2"


    @property
    def mongodb_settings(self):
        return {
            'host': f'{self.MONGODB_URI}/{self.MONGODB_DATABASE}',
            'db': self.MONGODB_DATABASE,
            'connect': self.MONGODB_CONNECT,
        }

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

    def validate(self):
        if not self.POSTGRESQL_URI:
            raise ValueError("POSTGRESQL URI is not defined")


config = Config()
