from flask_smorest import Blueprint

pod_blp = Blueprint(
    'pod', 
    'pod', 
    url_prefix='/pod',
    description='Operations on POD'
)
