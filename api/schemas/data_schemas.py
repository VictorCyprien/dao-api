from marshmallow import Schema, fields, validates_schema, ValidationError, post_dump
from marshmallow.validate import Range



class ItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    cid = fields.String()
    type = fields.String(required=True)
    source = fields.Raw(required=True, metadata={"description": "Source field that can be either a string (for items) or a dict (for summary)"})
    title = fields.String(required=False)
    text = fields.String(required=True)
    link = fields.String()
    topics = fields.String()
    date = fields.Integer(required=True)
    metadata = fields.String()

    class Meta:
        description = "Informations about the data from SQLite"
        ordered = True



class SummarySchema(Schema):
    data = fields.Nested(ItemSchema, many=True)

    class Meta:
        description = "Informations about the summary"
        ordered = True



class QueryParamsSchema(Schema):
    date_start = fields.String(required=True)
    date_end = fields.String(required=True)
    source = fields.String(required=False)

    class Meta:
        description = "Query parameters for data filtering"
        ordered = True



class ItemsResponseSchema(Schema):
    data = fields.Nested(ItemSchema, many=True)

    class Meta:
        description = "Items response schema"
        ordered = True



class SummaryResponseSchema(Schema):
    summary = fields.List(fields.Dict(keys=fields.String(), values=fields.Nested(ItemSchema, many=True)))

    class Meta:
        description = "Summary response schema"
        ordered = True



