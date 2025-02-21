from flask_smorest import Blueprint

pod_blp = Blueprint(
    name='pods',
    import_name=__name__,
    url_prefix='/pods',
    description='Operations on PODs'
)
