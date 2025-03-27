from marshmallow import Schema, fields, validate
from datetime import datetime
import pytz

class TokenSchema(Schema):
    """Schema for Token model"""
    token_id = fields.Str(dump_only=True)
    wallet_address = fields.Str(dump_only=True)
    token_mint = fields.Str(dump_only=True)
    balance = fields.Float(dump_only=True)
    last_updated = fields.DateTime(dump_only=True)
    symbol = fields.Str(dump_only=True)
    decimals = fields.Int(dump_only=True)
    price = fields.Float(dump_only=True)
    price_change_percentage = fields.Float(dump_only=True)
    photo_url = fields.Str(dump_only=True)

    
class TokenCreateSchema(Schema):
    """Schema for creating a Token"""
    dao_id = fields.Str(required=True)
    name = fields.Str(required=True)
    symbol = fields.Str(required=True)
    contract = fields.Str(required=True)
    amount = fields.Float(required=True)
    
class TokenSchemaResponse(Schema):
    """Schema for Token response"""
    action = fields.Str(required=True)
    token = fields.Nested(TokenSchema, required=True)

class TokenUpdateSchema(Schema):
    """Schema for updating a Token"""
    name = fields.Str(validate=validate.Length(min=1))
    symbol = fields.Str(validate=validate.Length(min=1))
    contract = fields.Str()
    amount = fields.Float()
    price = fields.Float()
    percentage = fields.Int(validate=validate.Range(min=0, max=100))

class TransferSchema(Schema):
    """Schema for Transfer model"""
    transfer_id = fields.Str(dump_only=True)
    dao_id = fields.Str(required=True)
    token_id = fields.Str(required=True)
    from_address = fields.Str(required=True)
    to_address = fields.Str(required=True)
    amount = fields.Float(required=True)
    timestamp = fields.DateTime(dump_default=datetime.now(pytz.utc))
    token = fields.Nested(TokenSchema, dump_only=True)

class TransferCreateSchema(Schema):
    """Schema for creating a Transfer"""
    dao_id = fields.Str(required=True)
    token_id = fields.Str(required=True)
    from_address = fields.Str(required=True)
    to_address = fields.Str(required=True)
    amount = fields.Float(required=True)
    timestamp = fields.DateTime(dump_default=datetime.now(pytz.utc))

class TransferSchemaResponse(Schema):
    """Schema for Transfer response"""
    action = fields.Str(required=True)
    transfer = fields.Nested(TransferSchema, required=True)

class TreasurySchema(Schema):
    """Schema for the entire Treasury view"""
    total_value = fields.Method("get_total_value", dump_only=True)
    daily_change = fields.Method("get_daily_change", dump_only=True)
    daily_change_percentage = fields.Method("get_daily_change_percentage", dump_only=True)
    tokens = fields.Nested(TokenSchema, many=True)
    recent_transfers = fields.Nested(TransferSchema, many=True)

    def get_total_value(self, obj):
        """Calculate the total value of all tokens"""
        #return sum(token.amount * token.price for token in obj.get("tokens", []))
        return 0

    def get_daily_change(self, obj):
        """Calculate the daily change value (placeholder)"""
        # This would normally involve historical data - simplified for now
        return obj.get("daily_change", 0.0)

    def get_daily_change_percentage(self, obj):
        """Calculate the daily change percentage (placeholder)"""
        # This would normally involve historical data - simplified for now
        return obj.get("daily_change_percentage", 0.0)

class TreasuryUpdatePercentagesSchema(TreasurySchema):
    """Schema for the response when updating token percentages"""
    action = fields.Str(required=True, dump_default="updated_percentages")
    message = fields.Str(required=True) 