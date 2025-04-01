from environs import Env
import os
from cryptography.fernet import Fernet


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

        # FLASK CORS
        self.CORS_ALLOWED_ORIGINS = env.str('CORS_ALLOWED_ORIGINS', "*")

        # POSTGRESQL
        self.POSTGRESQL_URI = env.str('POSTGRESQL_URI', 'localhost')
        self.POSTGRESQL_USERNAME = env.str("POSTGRESQL_USERNAME", "root")
        self.POSTGRESQL_PASSWORD = env.str("POSTGRESQL_PASSWORD", "example")
        self.POSTGRESQL_DB = env.str("POSTGRESQL_DB", "dao")

        # REDIS
        self.REDIS_URI = env.str('REDIS_URI', "localhost")
        self.REDIS_PORT = env.int('REDIS_PORT', 6379)

        # MINIO (S3-compatible object storage)
        self.MINIO_ENDPOINT = env.str('MINIO_ENDPOINT', 'localhost:9000')
        self.MINIO_ACCESS_KEY = env.str('MINIO_ACCESS_KEY', 'minio')
        self.MINIO_SECRET_KEY = env.str('MINIO_SECRET_KEY', 'minio123')
        self.MINIO_SECURE = env.bool('MINIO_SECURE', False)
        self.MINIO_BUCKET_DAOS = env.str('MINIO_BUCKET_DAOS', 'daos')
        self.MINIO_BUCKET_USERS = env.str('MINIO_BUCKET_USERS', 'users')
        self.MINIO_REGION = env.str('MINIO_REGION', 'us-east-1')

        # SMTP
        self.SMTP_SERVER = env.str('SMTP_SERVER', "localhost")
        self.SMTP_PORT = env.int('SMTP_PORT', 1025)
        self.SMTP_USERNAME = env.str('SMTP_USERNAME', "noreply@dao.io")
        self.SMTP_PASSWORD = env.str('SMTP_PASSWORD', "example")

        # PASSWORD CUSTOM SALT
        self.SECURITY_PASSWORD_SALT = env.str('SECURITY_PASSWORD_SALT', "672B2BB59D2E432E8F3FB10E23B8AECC")

        # CACHE CONFIGURATION
        self.CACHE_TYPE = env.str('CACHE_TYPE', 'redis')
        self.CACHE_REDIS_HOST = env.str('CACHE_REDIS_HOST', self.REDIS_URI)
        self.CACHE_REDIS_PORT = env.int('CACHE_REDIS_PORT', self.REDIS_PORT)
        self.CACHE_DEFAULT_TIMEOUT = env.int('CACHE_DEFAULT_TIMEOUT', 300)  # Default cache timeout in seconds (5 minutes)
        self.CACHE_KEY_PREFIX = env.str('CACHE_KEY_PREFIX', 'dao_api_cache:')
        
        # CACHE TIMEOUTS FOR SPECIFIC ENDPOINTS (in seconds)
        self.CACHE_TIMEOUT_TOKEN_LIST = env.int('CACHE_TIMEOUT_TOKEN_LIST', 300)  # 5 minutes for token lists
        self.CACHE_TIMEOUT_DAO_LIST = env.int('CACHE_TIMEOUT_DAO_LIST', 600)  # 10 minutes for DAO lists
        self.CACHE_TIMEOUT_TREASURY = env.int('CACHE_TIMEOUT_TREASURY', 1800)  # 30 minutes for treasury data

        # OPENAPI
        self.API_TITLE = self.SERVICE_NAME
        self.API_VERSION = env.str('CI_COMMIT_REF_NAME', "dev")
        self.OPENAPI_VERSION = "3.0.2"

        # API Secret Key for encrypting the user auth tokens (Defaults to 'super-secret')
        self.SECRET_KEY = os.getenv('SECRET_KEY', "super-secret")

        # API configuration
        self.API_SPEC_URL = env.str('API_SPEC_URL', '/api/swagger.json')
        self.OPENAPI_URL_PREFIX = env.str('OPENAPI_URL_PREFIX', '/')
        self.OPENAPI_SWAGGER_UI_PATH = env.str('OPENAPI_SWAGGER_UI_PATH', '/api/swagger')
        self.OPENAPI_SWAGGER_UI_URL = env.str('OPENAPI_SWAGGER_UI_URL', 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/')

        # OAuth configuration
        self.DISCORD_CLIENT_ID = env.str('DISCORD_CLIENT_ID', "")
        self.DISCORD_CLIENT_SECRET = env.str('DISCORD_CLIENT_SECRET', "")
        self.DISCORD_REDIRECT_URI = env.str('DISCORD_REDIRECT_URI', "http://localhost:5000/auth/discord/callback")
        
        self.TWITTER_CLIENT_ID = env.str('TWITTER_CLIENT_ID', "")
        self.TWITTER_CLIENT_SECRET = env.str('TWITTER_CLIENT_SECRET', "")
        self.TWITTER_REDIRECT_URI = env.str('TWITTER_REDIRECT_URI', "http://localhost:5000/auth/twitter/callback")
        
        self.TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_BOT_TOKEN', "")
        
        # OAuth token encryption key (generate one if not provided)
        self.OAUTH_ENCRYPTION_KEY = env.str('OAUTH_ENCRYPTION_KEY', Fernet.generate_key().decode())
        
        # Frontend URL for redirects after OAuth
        self.FRONTEND_URL = env.str('FRONTEND_URL', "http://localhost:5173")

    @property
    def mongodb_settings(self):
        return {
            'host': f'{self.MONGODB_URI}/{self.MONGODB_DATABASE}',
            'db': self.MONGODB_DATABASE,
            'connect': self.MONGODB_CONNECT,
        }
        
    @property
    def cache_config(self):
        """Get the Flask-Caching configuration dictionary"""
        return {
            'CACHE_TYPE': self.CACHE_TYPE,
            'CACHE_REDIS_HOST': self.CACHE_REDIS_HOST,
            'CACHE_REDIS_PORT': self.CACHE_REDIS_PORT,
            'CACHE_DEFAULT_TIMEOUT': self.CACHE_DEFAULT_TIMEOUT,
            'CACHE_KEY_PREFIX': self.CACHE_KEY_PREFIX,
        }
    
    @property
    def minio_config(self):
        """Get the Minio configuration dictionary"""
        return {
            'endpoint': self.MINIO_ENDPOINT,
            'access_key': self.MINIO_ACCESS_KEY,
            'secret_key': self.MINIO_SECRET_KEY,
            'secure': self.MINIO_SECURE,
            'region': self.MINIO_REGION,
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
