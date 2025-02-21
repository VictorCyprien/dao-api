from flask_smorest import Blueprint

communities_blp = Blueprint(
    'Communities', 
    'communities', 
    url_prefix='/communities',
    description='Operations on communities'
)
