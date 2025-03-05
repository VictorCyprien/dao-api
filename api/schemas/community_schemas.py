from marshmallow import Schema, fields, validate

class UserBasicSchema(Schema):
    """Basic user information for nested relationships"""
    user_id = fields.Int()
    username = fields.Str()

class DAOSchema(Schema):
    dao_id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    owner_id = fields.Int(required=True)
    is_active = fields.Bool()
    admins = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    members = fields.Nested(UserBasicSchema, many=True, dump_only=True)

class DAOUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(min=1))
    is_active = fields.Bool()

class DAOMembershipSchema(Schema):
    user_id = fields.Int(required=True)

