from flask_smorest import Blueprint

proposals_blp = Blueprint(
    'proposals',
    'proposals',
    url_prefix='/proposals',
    description='Operations on DAO proposals'
)
