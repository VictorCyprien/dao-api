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

## API Documentation

You can find the API documentation in the `specs` folder.

Copy the file `dao-api-spec.yaml` and paste it in this website : https://editor.swagger.io/

## Tests

To run the tests, you can use the following command :

```bash
make tests (with coverage)
make testsx (without coverage)
```

## Project structure

```bash
.
├── api
│   ├── app.py
│   ├── config.py
│   ├── main.py
│   ├── models
│   │   └── user.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── auth_schemas.py
│   │   ├── communs_schemas.py
│   │   ├── data_schemas.py
│   │   └── users_schemas.py
│   └── views
│       ├── __init__.py
│       ├── auth
│       │   ├── __init__.py
│       │   ├── auth_blp.py
│       │   ├── login_view.py
│       │   └── logout_view.py
│       ├── data
│       │   ├── __init__.py
│       │   ├── data_blp.py
│       │   └── data_view.py
│       └── users
│           ├── __init__.py
│           ├── one_user_view.py
│           ├── root_users_view.py
│           ├── user_view_handler.py
│           └── users_blp.py
├── helpers
│   ├── errors_file.py
│   ├── logging_file.py
│   ├── redis_file.py
│   ├── smtp_file.py
│   └── sqlite_file.py
├── run.py
├── setup.py
├── specs
└── wsgi.py
```
