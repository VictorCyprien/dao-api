from typing import Dict

from flask import current_app, jsonify
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from flask_pydantic import validate


from api.models.dao import DAO
from api.models.user import User
from api.schemas.pydantic_schemas import DAO as DAOModel, InputCreateDAO, PagingError
from api.views.daos.daos_blp import blp as daos_blp
from helpers.errors_file import ErrorHandler, NotFound


@daos_blp.route("/")
class RootDAOsView(MethodView):
    @daos_blp.doc(operationId='GetAllDAOs')
    def get(self):
        """List all DAOs"""
        db: SQLAlchemy = current_app.db
        daos = DAO.get_all(db.session)
        
        # Convert to list of Pydantic models using DAO's serialization method
        dao_models = [DAOModel.parse_obj(dao.to_dict()) for dao in daos]
        return [dao_model.model_dump() for dao_model in dao_models]


    @daos_blp.doc(operationId='CreateDAO')
    @jwt_required(fresh=True)
    @validate(body=InputCreateDAO)
    def post(self, body: InputCreateDAO):
        """Create a new DAO"""
        db: SQLAlchemy = current_app.db

        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)

        try:
            dao = DAO.create(body.model_dump(exclude_unset=True))
            dao.admins.append(auth_user)
            dao.members.append(auth_user)
            db.session.add(dao)
            db.session.commit()
            
            # Convert to Pydantic model using DAO's serialization method
            dao_model = DAOModel.model_validate(dao.to_dict())
            return jsonify(dao_model.model_dump()), 201
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))
