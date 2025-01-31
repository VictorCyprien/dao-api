from flask_smorest import Blueprint

data_blp = Blueprint(
    name='data',
    import_name=__name__,
    description='Data handler',
    url_prefix='/data'
)
