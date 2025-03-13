from typing import Dict

from flask import current_app, request
from flask.views import MethodView
from flask_smorest import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from api.models.pod import POD
from api.models.dao import DAO
from api.models.user import User
from api.models.discord_channel import DiscordChannel
from api.models.discord_message import DiscordMessage

from api.schemas.discord_schemas import (
    DiscordChannelSchema,
    DiscordMessageSchema,
    CreateDiscordChannelSchema,
    UpdateDiscordChannelSchema,
    DiscordChannelResponseSchema,
    DiscordChannelsResponseSchema,
    DiscordMessageResponseSchema,
    DiscordMessagesResponseSchema,
    LinkDiscordChannelSchema
)
from api.schemas.communs_schemas import PagingError
from api.views.daos.daos_blp import blp as daos_blp

from helpers.errors_file import BadRequest, ErrorHandler, NotFound, Unauthorized
from helpers.logging_file import Logger

logger = Logger()


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>/feed")
class PodFeedView(MethodView):
    """View for managing POD discord feed"""

    @daos_blp.doc(operationId='GetPODFeed')
    @daos_blp.response(404, PagingError, description="DAO or POD not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(200, DiscordMessagesResponseSchema, description="Discord feed retrieved successfully")
    @jwt_required(fresh=True)
    def get(self, dao_id: str, pod_id: str):
        """Get Discord feed for a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Validate DAO exists and user is a member
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        # Validate POD exists and belongs to the DAO
        pod = POD.get_by_id(pod_id, db.session)
        if not pod:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        if pod.dao_id != dao_id:
            raise BadRequest(ErrorHandler.POD_NOT_IN_DAO)
        
        # Get limit from query params, default to 50
        limit = request.args.get('limit', default=50, type=int)
        
        # Get messages for this POD's Discord channels
        messages = DiscordMessage.get_by_pod(pod_id, db.session, limit=limit)
        
        return {
            "action": "get_pod_feed",
            "messages": messages
        }


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>/discord-channels")
class PodDiscordChannelsView(MethodView):
    """View for managing Discord channels associated with a POD"""

    @daos_blp.doc(operationId='GetPODDiscordChannels')
    @daos_blp.response(404, PagingError, description="DAO or POD not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(200, DiscordChannelsResponseSchema, description="Discord channels retrieved successfully")
    @jwt_required(fresh=True)
    def get(self, dao_id: str, pod_id: str):
        """Get all Discord channels for a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Validate DAO exists and user is a member
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        # Validate POD exists and belongs to the DAO
        pod = POD.get_by_id(pod_id, db.session)
        if not pod:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        if pod.dao_id != dao_id:
            raise BadRequest(ErrorHandler.POD_NOT_IN_DAO)
        
        # Get channels for this POD
        channels = DiscordChannel.get_by_pod_id(pod_id, db.session)
        
        return {
            "action": "get_pod_discord_channels",
            "channels": channels
        }
    
    @daos_blp.arguments(LinkDiscordChannelSchema)
    @daos_blp.doc(operationId='LinkDiscordChannelToPOD')
    @daos_blp.response(404, PagingError, description="DAO, POD or Discord channel not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Invalid data")
    @daos_blp.response(201, DiscordChannelResponseSchema, description="Discord channel linked successfully")
    @jwt_required(fresh=True)
    def post(self, input_data: Dict, dao_id: str, pod_id: str):
        """Link a Discord channel to a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Validate DAO exists and user is a member
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        # Validate POD exists and belongs to the DAO
        pod = POD.get_by_id(pod_id, db.session)
        if not pod:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        if pod.dao_id != dao_id:
            raise BadRequest(ErrorHandler.POD_NOT_IN_DAO)
        
        # Get the Discord channel
        channel_id = input_data["channel_id"]
        channel = DiscordChannel.get_by_id(channel_id, db.session)
        
        if not channel:
            raise NotFound("Discord channel not found")
        
        # Link the channel to the POD
        channel.pod_id = pod_id
        
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise BadRequest(f"Error linking Discord channel: {str(e)}")
        
        return {
            "action": "link_discord_channel",
            "channel": channel
        }


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>/discord-channels/<string:channel_id>")
class PodDiscordChannelView(MethodView):
    """View for managing a specific Discord channel associated with a POD"""

    @daos_blp.doc(operationId='UnlinkDiscordChannelFromPOD')
    @daos_blp.response(404, PagingError, description="DAO, POD or Discord channel not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Channel not linked to this POD")
    @daos_blp.response(200, DiscordChannelResponseSchema, description="Discord channel unlinked successfully")
    @jwt_required(fresh=True)
    def delete(self, dao_id: str, pod_id: str, channel_id: str):
        """Unlink a Discord channel from a POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Validate DAO exists and user is a member
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        # Validate POD exists and belongs to the DAO
        pod = POD.get_by_id(pod_id, db.session)
        if not pod:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        if pod.dao_id != dao_id:
            raise BadRequest(ErrorHandler.POD_NOT_IN_DAO)
        
        # Get the Discord channel
        channel = DiscordChannel.get_by_id(channel_id, db.session)
        if not channel:
            raise NotFound("Discord channel not found")
        
        # Check if channel is linked to this POD
        if channel.pod_id != pod_id:
            raise BadRequest("Channel is not linked to this POD")
        
        # Unlink the channel
        channel.pod_id = None
        
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise BadRequest(f"Error unlinking Discord channel: {str(e)}")
        
        return {
            "action": "unlink_discord_channel",
            "channel": channel
        }


@daos_blp.route("<string:dao_id>/pods/<string:pod_id>/discord-channels/<string:channel_id>/messages")
class DiscordChannelMessagesView(MethodView):
    """View for retrieving messages from a specific Discord channel"""

    @daos_blp.doc(operationId='GetChannelMessages')
    @daos_blp.response(404, PagingError, description="DAO, POD or Discord channel not found")
    @daos_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @daos_blp.response(400, PagingError, description="Bad Request - Channel not linked to this POD")
    @daos_blp.response(200, DiscordMessagesResponseSchema, description="Discord messages retrieved successfully")
    @jwt_required(fresh=True)
    def get(self, dao_id: str, pod_id: str, channel_id: str):
        """Get messages from a specific Discord channel"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Validate DAO exists and user is a member
        dao = DAO.get_by_id(dao_id, db.session)
        if not dao:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        if auth_user not in dao.members:
            raise Unauthorized(ErrorHandler.USER_NOT_MEMBER)
        
        # Validate POD exists and belongs to the DAO
        pod = POD.get_by_id(pod_id, db.session)
        if not pod:
            raise NotFound(ErrorHandler.POD_NOT_FOUND)
        if pod.dao_id != dao_id:
            raise BadRequest(ErrorHandler.POD_NOT_IN_DAO)
        
        # Get the Discord channel
        channel = DiscordChannel.get_by_id(channel_id, db.session)
        if not channel:
            raise NotFound("Discord channel not found")
        
        # Check if channel is linked to this POD
        if channel.pod_id != pod_id:
            raise BadRequest("Channel is not linked to this POD")
        
        # Get limit from query params, default to 50
        limit = request.args.get('limit', default=50, type=int)
        
        # Get messages for this channel
        messages = DiscordMessage.get_by_channel(channel_id, db.session, limit=limit)
        
        return {
            "action": "get_channel_messages",
            "messages": messages
        } 