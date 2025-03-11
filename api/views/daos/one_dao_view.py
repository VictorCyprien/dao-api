from typing import Dict

from flask import current_app, jsonify
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from flask_pydantic import validate

from api.models.dao import DAO
from api.models.user import User
from api.schemas.pydantic_schemas import DAO as DAOModel, DAOUpdate, PagingError
from api.views.daos.daos_blp import blp as daos_blp
from helpers.errors_file import NotFound, ErrorHandler, Unauthorized


@daos_blp.route("/<string:dao_id>")
class OneDAOView(MethodView):
    @daos_blp.doc(operationId='GetDAOById')
    def get(self, dao_id: str):
        """Get a DAO by ID"""
        db: SQLAlchemy = current_app.db
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Convert to Pydantic model using the DAO's serialization method
        dao_model = DAOModel.model_validate(dao.to_dict())
        return dao_model.model_dump()
    

    @daos_blp.doc(operationId='UpdateDAO')
    @jwt_required(fresh=True)
    @validate(body=DAOUpdate)
    def put(self, body: DAOUpdate, dao_id: str):
        """Update a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if user is owner or admin
        if dao.owner_id != auth_user.user_id or auth_user not in dao.admins:
            raise Unauthorized(ErrorHandler.DAO_NOT_ADMIN)
        
        try:
            # Update DAO
            dao.update(body.model_dump(exclude_unset=True))
            db.session.commit()
            
            # Convert to Pydantic model using DAO's serialization method
            dao_model = DAOModel.model_validate(dao.to_dict())
            return dao_model.model_dump()
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))


    @daos_blp.doc(operationId='DeleteDAO')
    @jwt_required(fresh=True)
    def delete(self, dao_id: str):
        """Delete a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Get DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if user is owner
        if auth_user.user_id != dao.owner_id:
            raise Unauthorized(ErrorHandler.USER_NOT_OWNER)
        
        try:
            # Delete DAO
            db.session.delete(dao)
            db.session.commit()
            return {}, 200
        except Exception as e:
            db.session.rollback()
            abort(400, message=str(e))
