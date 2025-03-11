from flask_smorest import Blueprint

blp = Blueprint(
    name="daos", 
    import_name=__name__, 
    description="Operations on DAOs",
    url_prefix="/daos"
)
