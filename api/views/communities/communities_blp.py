from flask_smorest import Blueprint

communities_blp = Blueprint(
    name='communities',
    import_name=__name__,
    url_prefix='/communities',
    description='Operations on communities'
)
