from flask_smorest import Blueprint

users_blp = Blueprint(
    name='users',
    import_name=__name__,
    description='Manage Users',
    url_prefix='/users'
)
