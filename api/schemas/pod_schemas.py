from marshmallow import Schema, fields

class PODSchema(Schema):
    pod_id = fields.Int(dump_only=True)
    community_id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class PODUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    is_active = fields.Bool() 