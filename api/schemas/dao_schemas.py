from marshmallow import Schema, fields, validate

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
    admins = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    members = fields.Nested(UserBasicSchema, many=True, dump_only=True)

class DAOUpdateSchema(Schema):
    """Schema for updating a DAO"""
    name = fields.Str(validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(min=1))
    is_active = fields.Bool()

class DAOMembershipSchema(Schema):
    """Schema for DAO membership operations"""
    user_id = fields.Str(required=True)

