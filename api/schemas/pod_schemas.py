from marshmallow import Schema, fields, validate

class PODSchema(Schema):
    pod_id = fields.Str(dump_only=True)
    dao_id = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class InputCreatePODSchema(Schema):
    """Schema for creating a POD"""
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    dao_id = fields.Str(required=True)

class PODSchemaResponse(Schema):
    """Schema for POD response"""
    action = fields.Str(required=True)
    pod = fields.Nested(PODSchema, required=True)

class PODMembershipResponseSchema(Schema):
    """Schema for POD membership response"""
    action = fields.Str(required=True)
    pod = fields.Nested(PODSchema, required=True)

class PODUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(min=1))
    is_active = fields.Bool()

class PODMembershipSchema(Schema):
    user_id = fields.Str(required=True)
