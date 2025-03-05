from marshmallow import Schema, fields, validate

class UserBasicSchema(Schema):
    """Basic user information for nested relationships"""
    user_id = fields.Int()
    username = fields.Str()

class DAOSchema(Schema):
    """Schema for DAO model"""
    dao_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    owner_id = fields.Int(required=True)
    is_active = fields.Bool(dump_default=True)
    admins = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    members = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    user_who_made_request = fields.Int(required=True)

class DAOUpdateSchema(Schema):
    """Schema for updating a DAO"""
    name = fields.Str(validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(min=1))
    is_active = fields.Bool()
    user_who_made_request = fields.Int(required=True)

class DAOMembershipSchema(Schema):
    """Schema for DAO membership operations"""
    user_id = fields.Int(required=True)

