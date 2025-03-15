from marshmallow import Schema, fields, validate, post_load
import json
from typing import List, Dict, Any

class DiscordChannelSchema(Schema):
    """Schema for Discord channels"""
    channel_id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    pod_id = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    last_synced_at = fields.DateTime(dump_only=True)
    message_count = fields.Int(dump_only=True)

class DiscordMessageSchema(Schema):
    """Schema for Discord messages"""
    message_id = fields.Str(dump_only=True)
    channel_id = fields.Str(required=True)
    username = fields.Str(required=True)
    user_id = fields.Str(required=True)
    text = fields.Str(allow_none=True)
    has_media = fields.Bool(dump_only=True)
    media_urls = fields.Method("get_media_urls", "set_media_urls")
    created_at = fields.DateTime(required=True)
    indexed_at = fields.DateTime(dump_only=True)

    def get_media_urls(self, obj) -> List[str]:
        """Convert JSON string to list"""
        if hasattr(obj, "media_urls") and obj.media_urls:
            return json.loads(obj.media_urls)
        return []

    def set_media_urls(self, value) -> str:
        """Convert list to JSON string"""
        if isinstance(value, list):
            return json.dumps(value)
        return json.dumps([])

class CreateDiscordChannelSchema(Schema):
    """Schema for creating a Discord channel"""
    channel_id = fields.Str(required=True)
    name = fields.Str(required=True)
    pod_id = fields.Str(allow_none=True)

class UpdateDiscordChannelSchema(Schema):
    """Schema for updating a Discord channel"""
    name = fields.Str()
    pod_id = fields.Str(allow_none=True)

class CreateDiscordMessageSchema(Schema):
    """Schema for creating a Discord message"""
    message_id = fields.Str(required=True)
    channel_id = fields.Str(required=True)
    username = fields.Str(required=True)
    user_id = fields.Str(required=True)
    text = fields.Str(allow_none=True)
    media_urls = fields.List(fields.Str(), required=False)
    created_at = fields.DateTime(required=True)

    @post_load
    def process_data(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process data after loading"""
        # Set has_media based on media_urls
        if "media_urls" in data and data["media_urls"]:
            data["has_media"] = True
            data["media_urls"] = json.dumps(data["media_urls"])
        else:
            data["has_media"] = False
            data["media_urls"] = None
        return data

class DiscordChannelResponseSchema(Schema):
    """Schema for Discord channel responses"""
    action = fields.Str(required=True)
    channel = fields.Nested(DiscordChannelSchema, required=True)

class DiscordChannelsResponseSchema(Schema):
    """Schema for multiple Discord channels response"""
    action = fields.Str(required=True)
    channels = fields.List(fields.Nested(DiscordChannelSchema), required=True)

class DiscordMessageResponseSchema(Schema):
    """Schema for Discord message responses"""
    action = fields.Str(required=True)
    message = fields.Nested(DiscordMessageSchema, required=True)

class DiscordMessagesResponseSchema(Schema):
    """Schema for multiple Discord messages response"""
    action = fields.Str(required=True)
    messages = fields.List(fields.Nested(DiscordMessageSchema), required=True)

class LinkDiscordChannelSchema(Schema):
    """Schema for linking a Discord channel to a POD"""
    channel_id = fields.Str(required=True)
    pod_id = fields.Str(required=True)

class UnlinkDiscordChannelSchema(Schema):
    """Schema for unlinking a Discord channel from a POD"""
    channel_id = fields.Str(required=True) 