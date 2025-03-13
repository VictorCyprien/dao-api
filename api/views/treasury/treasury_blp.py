from flask_smorest import Blueprint

blp = Blueprint(
    name="treasury", 
    import_name=__name__, 
    description="Operations on Treasury",
    url_prefix="/treasury"
) 