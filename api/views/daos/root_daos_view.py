from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from api.utils import conditional_jwt_required

from api.models.dao import DAO
from api.models.user import User
from api.schemas.dao_schemas import DAOSchema, DAOUpdateSchema, DAOMembershipSchema
from api.schemas.communs_schemas import PagingError
from api.views.daos.daos_blp import blp as daos_blp
from helpers.errors_file import ErrorHandler, NotFound


@daos_blp.route("/")
class RootDAOsView(MethodView):
    @daos_blp.response(200, DAOSchema(many=True))
    def get(self):
        """List all DAOs"""
        db: SQLAlchemy = current_app.db
        return DAO.get_all(db.session)

    @conditional_jwt_required()
    @daos_blp.arguments(DAOSchema)
    @daos_blp.response(400, PagingError)
    @daos_blp.response(201, DAOSchema)
    def post(self, dao_data: Dict):
        """Create a new DAO"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
            
        try:
            dao = DAO.create(dao_data)
            dao.admins.append(auth_user)
            dao.members.append(auth_user)
            db.session.add(dao)
            db.session.commit()
            return dao
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))
