from marshmallow import Schema, fields, validate

from helpers.schemas_file import OmitNoneField


# String field that will be omitted if None
class OmitNoneString(OmitNoneField, fields.String):
    pass

class UserBasicSchema(Schema):
    """Basic user information for nested relationships"""
    user_id = fields.Str()
    username = fields.Str()

class DAOSchema(Schema):
    """Schema for DAO model"""
    dao_id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    owner_id = fields.Str(required=True)
    is_active = fields.Bool(dump_default=True)
    # Social media fields
    discord_server = OmitNoneString()
    twitter = OmitNoneString()
    telegram = OmitNoneString()
    instagram = OmitNoneString()
    tiktok = OmitNoneString()
    website = OmitNoneString()
    # Media fields
    profile_picture = OmitNoneString()
    banner_picture = OmitNoneString()
    # Treasury field
    treasury = OmitNoneString()
    # Relationship fields
    admins = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    members = fields.Nested(UserBasicSchema, many=True, dump_only=True)

class InputCreateDAOSchema(Schema):
    """Schema for creating a DAO"""
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    owner_id = fields.Str(required=True)
    # Social media fields (optional)
    discord_server = fields.Str()
    twitter = fields.Str()
    telegram = fields.Str()
    instagram = fields.Str()
    tiktok = fields.Str()
    website = fields.Str()
    # Treasury field (optional)
    treasury = fields.Str()
    # File upload fields for images (optional)
    profile = fields.Raw(metadata={'type': 'string', 'format': 'binary'})  # For profile picture upload
    banner = fields.Raw(metadata={'type': 'string', 'format': 'binary'})   # For banner picture upload

class DAOSchemaResponse(Schema):
    """Schema for DAO response"""
    action = fields.Str(required=True)
    dao = fields.Nested(DAOSchema, required=True)

class DAOMembershipResponseSchema(Schema):
    """Schema for DAO membership response"""
    action = fields.Str(required=True)
    dao = fields.Nested(DAOSchema, required=True)

class DAOUpdateSchema(Schema):
    """Schema for updating a DAO"""
    name = fields.Str(validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(min=1))
    is_active = fields.Bool()
    # Social media fields (optional)
    discord_server = fields.Str()
    twitter = fields.Str()
    telegram = fields.Str()
    instagram = fields.Str()
    tiktok = fields.Str()
    website = fields.Str()
    # Treasury field (optional)
    treasury = fields.Str()
    # File upload fields for images (optional)
    profile = fields.Raw(metadata={'type': 'string', 'format': 'binary'})  # For profile picture upload
    banner = fields.Raw(metadata={'type': 'string', 'format': 'binary'})   # For banner picture upload

class DAOMembershipSchema(Schema):
    """Schema for DAO membership operations"""
    user_id = fields.Str(required=True)

