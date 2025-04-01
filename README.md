# DAO API

This project is a REST API built with Flask, MongoDB and Redis that provides user management functionality with email verification and authentication.
It also provides data about ai-news project.

## Features

- Auth route with JWT tokens
- User route registration
- Data route about ai-news project
- Email verification
- MongoDB database integration
- Redis for task queueing
- Redis Insight dashboard for monitoring
- OpenAPI documentation
- Optional authentication disabling for development/testing

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- pip

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dao-api.git
cd dao-api
```

2. Install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Start the services:

```bash
docker-compose up -d
```

4. Access the API:

```bash
gunicorn wsgi:app
```

## Configuration Options

The following environment variables can be set to configure the API:

| Variable | Description | Default |
|----------|-------------|---------|
| SERVICE_NAME | The name of the service | "" |
| CORS_ALLOWED_ORIGINS | CORS allowed origins | "*" |
| POSTGRESQL_URI | PostgreSQL URI | "localhost" |
| POSTGRESQL_USERNAME | PostgreSQL username | "root" |
| POSTGRESQL_PASSWORD | PostgreSQL password | "example" |
| POSTGRESQL_DB | PostgreSQL database name | "dao" |
| REDIS_URI | Redis URI | "localhost" |
| REDIS_PORT | Redis port | 6379 |
| JWT_SECRET_KEY | Secret key for JWT tokens | None |
| JWT_ACCESS_TOKEN_EXPIRES | Expiration time for JWT tokens in seconds | None |
| DISCORD_CLIENT_ID | Discord OAuth client ID | "" |
| DISCORD_CLIENT_SECRET | Discord OAuth client secret | "" |
| DISCORD_REDIRECT_URI | Discord OAuth redirect URI | "http://localhost:5000/auth/discord/callback" |
| TWITTER_CLIENT_ID | Twitter OAuth client ID | "" |
| TWITTER_CLIENT_SECRET | Twitter OAuth client secret | "" |
| TWITTER_REDIRECT_URI | Twitter OAuth redirect URI | "http://localhost:5000/auth/twitter/callback" |
| TELEGRAM_BOT_TOKEN | Telegram bot token for authentication | "" |
| OAUTH_ENCRYPTION_KEY | Fernet encryption key for OAuth tokens (auto-generated if not provided) | "" |
| FRONTEND_URL | Frontend application URL for redirects | "http://localhost:5173" |
| FLASK_ENV | Flask environment (dev, prod) | "dev" |
| LOGGER_LEVEL | Logging level | "DEBUG" |
| MINIO_ENDPOINT | MinIO endpoint | "localhost:9000" |
| MINIO_ACCESS_KEY | MinIO access key | "minio" |
| MINIO_SECRET_KEY | MinIO secret key | "minio123" |
| MINIO_SECURE | Use HTTPS for MinIO | false |
| MINIO_BUCKET_DAOS | MinIO bucket for DAOs | "daos" |
| MINIO_BUCKET_USERS | MinIO bucket for users | "users" |
| MINIO_REGION | MinIO region | "us-east-1" |
| SMTP_SERVER | SMTP server address | "localhost" |
| SMTP_PORT | SMTP server port | 1025 |
| SMTP_USERNAME | SMTP username | "noreply@dao.io" |
| SMTP_PASSWORD | SMTP password | "example" |
| CACHE_TYPE | Cache type | "redis" |
| CACHE_REDIS_HOST | Redis cache host | Value of REDIS_URI |
| CACHE_REDIS_PORT | Redis cache port | Value of REDIS_PORT |
| CACHE_DEFAULT_TIMEOUT | Default cache timeout in seconds | 300 |
| CACHE_KEY_PREFIX | Cache key prefix | "dao_api_cache:" |

## API Documentation

You can find the API documentation in the `specs` folder.

Copy the file `dao-api-spec.yaml` and paste it in this website : https://editor.swagger.io/

## Tests

To run the tests, you can use the following command :

```bash
make tests (with coverage)
make testsx (without coverage)
```

## Project Structure

```bash
.
├── .coveragerc
├── .env.example
├── .gitignore
├── .scripts
│   └── update_structure.sh
├── DAO-APP.excalidraw
├── README.md
├── api
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── dao.py
│   │   ├── discord_channel.py
│   │   ├── discord_message.py
│   │   ├── pod.py
│   │   ├── proposal.py
│   │   ├── social_connection.py
│   │   ├── treasury.py
│   │   ├── user.py
│   │   └── wallet_monitor.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── auth_schemas.py
│   │   ├── community_schemas.py
│   │   ├── communs_schemas.py
│   │   ├── dao_schemas.py
│   │   ├── data_schemas.py
│   │   ├── discord_schemas.py
│   │   ├── pod_schemas.py
│   │   ├── proposal_schemas.py
│   │   ├── pydantic_schemas.py
│   │   ├── treasury_schemas.py
│   │   └── users_schemas.py
│   └── views
│       ├── auth
│       │   ├── __init__.py
│       │   ├── auth_blp.py
│       │   ├── discord_oauth.py
│       │   ├── logout_view.py
│       │   ├── oauth_view_handler.py
│       │   ├── social_connections_view.py
│       │   ├── telegram_auth.py
│       │   ├── twitter_oauth.py
│       │   └── wallet_auth_view.py
│       ├── daos
│       │   ├── __init__.py
│       │   ├── dao_membership_view.py
│       │   ├── dao_pods_view.py
│       │   ├── dao_view_handler.py
│       │   ├── daos_blp.py
│       │   ├── one_dao_view.py
│       │   ├── pod_discord_feed_view.py
│       │   └── root_daos_view.py
│       ├── proposals
│       │   ├── __init__.py
│       │   ├── dao_proposals_view.py
│       │   ├── pod_proposals_view.py
│       │   └── proposals_blp.py
│       ├── treasury
│       │   ├── __init__.py
│       │   ├── dao_treasury_view.py
│       │   ├── token_view.py
│       │   ├── transfer_view.py
│       │   └── treasury_blp.py
│       └── users
│           ├── __init__.py
│           ├── one_user_view.py
│           ├── root_users_view.py
│           ├── user_view_handler.py
│           └── users_blp.py
├── cov.xml
├── demo.http
├── docker-compose.yml
├── helpers
│   ├── build_cache_key.py
│   ├── cache_decorator.py
│   ├── errors_file.py
│   ├── logging_file.py
│   ├── minio_file.py
│   ├── redis_file.py
│   ├── schemas_file.py
│   └── smtp_file.py
├── makefile
├── report.xml
├── requirements.txt
├── run.py
├── setup.py
├── specs
│   ├── dao-api-spec.json
│   └── dao-api-spec.yaml
├── tests
│   ├── api
│   │   ├── auth
│   │   │   ├── test_api_login.py
│   │   │   ├── test_api_logout.py
│   │   │   └── test_wallet_auth.py
│   │   ├── daos
│   │   │   ├── delete
│   │   │   │   ├── test_delete_dao.py
│   │   │   │   ├── test_remove_admin.py
│   │   │   │   └── test_remove_members.py
│   │   │   ├── get
│   │   │   │   ├── test_get_dao.py
│   │   │   │   └── test_get_daos.py
│   │   │   ├── post
│   │   │   │   ├── test_add_admin.py
│   │   │   │   ├── test_add_member.py
│   │   │   │   └── test_create_dao.py
│   │   │   └── put
│   │   │       └── test_update_dao.py
│   │   ├── data
│   │   │   ├── _test_api_get_items.py
│   │   │   └── _test_api_get_summary.py
│   │   ├── discord
│   │   │   ├── delete
│   │   │   │   └── test_unlink_discord_channel.py
│   │   │   ├── get
│   │   │   │   ├── test_cache_behavior.py
│   │   │   │   ├── test_get_discord_channels.py
│   │   │   │   └── test_get_feed.py
│   │   │   └── post
│   │   │       └── test_link_discord_channel.py
│   │   ├── pods
│   │   │   ├── delete
│   │   │   │   ├── test_delete_pod.py
│   │   │   │   └── test_delete_pod_errors.py
│   │   │   ├── get
│   │   │   │   ├── test_get_pods.py
│   │   │   │   └── test_get_pods_errors.py
│   │   │   ├── post
│   │   │   │   ├── test_create_pod.py
│   │   │   │   └── test_create_pod_errors.py
│   │   │   └── put
│   │   │       ├── test_update_pod.py
│   │   │       └── test_update_pod_errors.py
│   │   ├── proposals
│   │   │   ├── delete
│   │   │   │   ├── test_delete_dao_proposal.py
│   │   │   │   └── test_delete_pod_proposals.py
│   │   │   ├── get
│   │   │   │   ├── test_get_dao_proposals.py
│   │   │   │   ├── test_get_pod_proposals.py
│   │   │   │   └── test_get_proposal_vote.py
│   │   │   ├── post
│   │   │   │   ├── test_create_dao_proposal.py
│   │   │   │   └── test_create_pod_proposals.py
│   │   │   └── put
│   │   │       ├── test_update_dao_proposal.py
│   │   │       └── test_update_pod_proposals.py
│   │   ├── treasury
│   │   │   ├── get
│   │   │   │   ├── _test_get_dao_transfers.py
│   │   │   │   ├── test_get_dao_tokens.py
│   │   │   │   └── test_get_dao_treasury.py
│   │   │   ├── post
│   │   │   │   └── _test_create_transfer.py
│   │   │   └── put
│   │   │       └── _test_dao_treasury_view.py
│   │   └── users
│   │       ├── get
│   │       │   └── test_api_get_users.py
│   │       ├── post
│   │       │   └── test_api_create_user.py
│   │       └── put
│   │           └── test_api_put_user.py
│   ├── conftest.py
│   ├── email
│   │   └── test_send_email.py
│   ├── models
│   │   ├── daos
│   │   │   ├── test_create_community_model.py
│   │   │   └── test_create_dao_model.py
│   │   ├── pods
│   │   │   ├── test_create_pod_model.py
│   │   │   └── test_update_pod_model.py
│   │   ├── proposals
│   │   │   ├── test_proposal_model.py
│   │   │   ├── test_proposal_pod_model.py
│   │   │   ├── test_proposal_relationships.py
│   │   │   └── test_proposal_validations.py
│   │   ├── treasury
│   │   │   ├── _test_transfer_model.py
│   │   │   ├── test_token_model.py
│   │   │   └── test_wallet_monitor_model.py
│   │   └── users
│   │       ├── test_create_user.py
│   │       ├── test_get_user.py
│   │       ├── test_send_email_user.py
│   │       └── test_update_user.py
│   ├── schemas
│   │   └── test_schemas.py
│   └── test_config.py
└── wsgi.py
```
