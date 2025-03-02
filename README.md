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
├── .coveragerc
├── .gitignore
├── .scripts
│   └── update_structure.sh
├── DAO-APP.excalidraw
├── README.md
├── TODO
├── api
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── community.py
│   │   ├── pod.py
│   │   └── user.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── auth_schemas.py
│   │   ├── community_schemas.py
│   │   ├── communs_schemas.py
│   │   ├── data_schemas.py
│   │   ├── pod_schemas.py
│   │   └── users_schemas.py
│   └── views
│       ├── __init__.py
│       ├── auth
│       │   ├── __init__.py
│       │   ├── auth_blp.py
│       │   ├── login_view.py
│       │   └── logout_view.py
│       ├── communities
│       │   ├── __init__.py
│       │   ├── communities_blp.py
│       │   ├── community_membership_view.py
│       │   ├── community_pods_view.py
│       │   ├── one_community_view.py
│       │   └── root_communities_view.py
│       ├── data
│       │   ├── __init__.py
│       │   ├── data_blp.py
│       │   └── data_view.py
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
│   ├── errors_file.py
│   ├── logging_file.py
│   ├── redis_file.py
│   ├── smtp_file.py
│   └── sqlite_file.py
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
│   │   │   └── test_api_logout.py
│   │   ├── communities
│   │   │   ├── delete
│   │   │   │   ├── test_delete_community.py
│   │   │   │   ├── test_remove_admin.py
│   │   │   │   └── test_remove_members.py
│   │   │   ├── get
│   │   │   │   ├── test_get_communities.py
│   │   │   │   └── test_get_community.py
│   │   │   ├── post
│   │   │   │   ├── test_add_admin.py
│   │   │   │   ├── test_add_member.py
│   │   │   │   └── test_create_community.py
│   │   │   └── put
│   │   │       └── test_update_community.py
│   │   ├── data
│   │   │   ├── test_api_get_items.py
│   │   │   └── test_api_get_summary.py
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
│   │   ├── communities
│   │   │   └── test_create_community_model.py
│   │   ├── pods
│   │   │   ├── test_create_pod_model.py
│   │   │   └── test_update_pod_model.py
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
