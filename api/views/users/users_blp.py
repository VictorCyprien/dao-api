from flask_smorest import Blueprint

users_blp = Blueprint(
    name='data',
    import_name=__name__,
    description='Manage Users',
    url_prefix='/users'
)
