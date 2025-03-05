from flask_smorest import Blueprint

blp = Blueprint(
    "daos", 
    __name__, 
    description="Operations on DAOs",
    url_prefix="/daos"
)
