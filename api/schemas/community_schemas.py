from marshmallow import Schema, fields

class UserBasicSchema(Schema):
    """Basic user information for nested relationships"""
    user_id = fields.Int()
    username = fields.Str()

class CommunitySchema(Schema):
    community_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    owner_id = fields.Int(required=True)
    is_active = fields.Bool()
    admins = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    members = fields.Nested(UserBasicSchema, many=True, dump_only=True)

class CommunityUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    is_active = fields.Bool()

class CommunityMembershipSchema(Schema):
    user_id = fields.Int(required=True)

