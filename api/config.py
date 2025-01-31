from environs import Env


class Config:

    def __init__(self):
        env = Env()

        self.SERVICE_NAME = env.str('SERVICE_NAME', "")
        self.LOGGER_LEVEL = env.str("LOGGER_LEVEL", "DEBUG")

        # FLASK
        self.FLASK_ENV = env.str('FLASK_ENV', 'dev')
        self.JSON_SORT_KEYS = True

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
