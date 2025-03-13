from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from api.models.user import User
from api.models.discord_channel import DiscordChannel

from api.schemas.discord_schemas import (
    DiscordChannelSchema,
    CreateDiscordChannelSchema,
    UpdateDiscordChannelSchema,
    DiscordChannelResponseSchema,
    DiscordChannelsResponseSchema
)
from api.schemas.communs_schemas import PagingError

from helpers.errors_file import BadRequest, ErrorHandler, NotFound, Unauthorized
from helpers.logging_file import Logger

logger = Logger()

blp = Blueprint(
    "discord", 
    "discord", 
    description="Operations on Discord channels and messages",
    url_prefix="/discord"
)

@blp.route("/channels")
class DiscordChannelsView(MethodView):
    """View for managing Discord channels"""

    @blp.doc(operationId='GetAllDiscordChannels')
    @blp.response(404, PagingError, description="User not found")
    @blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @blp.response(200, DiscordChannelsResponseSchema, description="Discord channels retrieved successfully")
    @jwt_required(fresh=True)
    def get(self):
        """Get all Discord channels"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Get all channels from database
        channels = db.session.query(DiscordChannel).all()
        
        return {
            "action": "get_all_discord_channels",
            "channels": channels
        }
    
    @blp.arguments(CreateDiscordChannelSchema)
    @blp.doc(operationId='CreateDiscordChannel')
    @blp.response(404, PagingError, description="User not found")
    @blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @blp.response(400, PagingError, description="Bad Request - Invalid data")
    @blp.response(201, DiscordChannelResponseSchema, description="Discord channel created successfully")
    @jwt_required(fresh=True)
    def post(self, input_data: Dict):
        """Create a new Discord channel in the system"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Check if channel already exists
        channel = DiscordChannel.get_by_id(input_data["channel_id"], db.session)
        if channel:
            raise BadRequest("Discord channel already exists")
        
        # Create new channel
        channel = DiscordChannel(
            channel_id=input_data["channel_id"],
            name=input_data["name"],
            pod_id=input_data.get("pod_id", None),
        )
        
        try:
            db.session.add(channel)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise BadRequest(f"Error creating Discord channel: {str(e)}")
        
        return {
            "action": "create_discord_channel",
            "channel": channel
        }


@blp.route("/channels/unlinked")
class UnlinkedDiscordChannelsView(MethodView):
    """View for retrieving unlinked Discord channels"""

    @blp.doc(operationId='GetUnlinkedDiscordChannels')
    @blp.response(404, PagingError, description="User not found")
    @blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @blp.response(200, DiscordChannelsResponseSchema, description="Unlinked Discord channels retrieved successfully")
    @jwt_required(fresh=True)
    def get(self):
        """Get all Discord channels that are not linked to any POD"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Get all unlinked channels
        channels = db.session.query(DiscordChannel).filter(DiscordChannel.pod_id == None).all()
        
        return {
            "action": "get_unlinked_discord_channels",
            "channels": channels
        }


@blp.route("/channels/<string:channel_id>")
class DiscordChannelView(MethodView):
    """View for managing a specific Discord channel"""

    @blp.doc(operationId='GetDiscordChannel')
    @blp.response(404, PagingError, description="User or Discord channel not found")
    @blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @blp.response(200, DiscordChannelResponseSchema, description="Discord channel retrieved successfully")
    @jwt_required(fresh=True)
    def get(self, channel_id: str):
        """Get a specific Discord channel"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Get the channel
        channel = DiscordChannel.get_by_id(channel_id, db.session)
        if not channel:
            raise NotFound("Discord channel not found")
        
        return {
            "action": "get_discord_channel",
            "channel": channel
        }
    
    @blp.arguments(UpdateDiscordChannelSchema)
    @blp.doc(operationId='UpdateDiscordChannel')
    @blp.response(404, PagingError, description="User or Discord channel not found")
    @blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @blp.response(400, PagingError, description="Bad Request - Invalid data")
    @blp.response(200, DiscordChannelResponseSchema, description="Discord channel updated successfully")
    @jwt_required(fresh=True)
    def put(self, input_data: Dict, channel_id: str):
        """Update a Discord channel"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Get the channel
        channel = DiscordChannel.get_by_id(channel_id, db.session)
        if not channel:
            raise NotFound("Discord channel not found")
        
        # Update channel fields
        if "name" in input_data:
            channel.name = input_data["name"]
        if "pod_id" in input_data:
            channel.pod_id = input_data["pod_id"]
        
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise BadRequest(f"Error updating Discord channel: {str(e)}")
        
        return {
            "action": "update_discord_channel",
            "channel": channel
        }
    
    @blp.doc(operationId='DeleteDiscordChannel')
    @blp.response(404, PagingError, description="User or Discord channel not found")
    @blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @blp.response(400, PagingError, description="Bad Request - Error deleting channel")
    @blp.response(200, DiscordChannelResponseSchema, description="Discord channel deleted successfully")
    @jwt_required(fresh=True)
    def delete(self, channel_id: str):
        """Delete a Discord channel"""
        db: SQLAlchemy = current_app.db
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        if not auth_user:
            raise NotFound(ErrorHandler.USER_NOT_FOUND)
        
        # Get the channel
        channel = DiscordChannel.get_by_id(channel_id, db.session)
        if not channel:
            raise NotFound("Discord channel not found")
        
        # Store channel data for response
        channel_data = channel.to_dict()
        
        try:
            db.session.delete(channel)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise BadRequest(f"Error deleting Discord channel: {str(e)}")
        
        return {
            "action": "delete_discord_channel",
            "channel": channel_data
        } 