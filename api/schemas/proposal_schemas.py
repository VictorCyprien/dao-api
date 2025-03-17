from marshmallow import Schema, fields, validate
from datetime import datetime

class UserBasicSchema(Schema):
    """Basic user information for nested relationships"""
    user_id = fields.Str()
    username = fields.Str()

class ProposalActionSchema(Schema):
    """Schema for proposal actions"""
    action_type = fields.Str(validate=validate.OneOf(["add_wallet", "remove_wallet", "withdraw_tokens"]))
    target_address = fields.Str(required=False)  # For wallet or withdrawal address
    token_id = fields.Str(required=False)        # For token transfer
    amount = fields.Float(required=False)        # For token transfer amount

class ProposalSchema(Schema):
    """Schema for Proposal model"""
    proposal_id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    dao_id = fields.Str(required=True)
    created_by = fields.Str(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    actions = fields.Dict(required=False, allow_none=True)
    for_votes_count = fields.Int(dump_only=True)
    against_votes_count = fields.Int(dump_only=True)
    for_voters = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    against_voters = fields.Nested(UserBasicSchema, many=True, dump_only=True)
    is_active = fields.Method("get_is_active", dump_only=True)
    has_passed = fields.Method("get_has_passed", dump_only=True)

    def get_is_active(self, obj):
        """Return whether the proposal is currently active"""
        now = datetime.now()
        return obj.start_time <= now <= obj.end_time

    def get_has_passed(self, obj):
        """Return whether the proposal has passed"""
        return obj.for_votes_count > obj.against_votes_count

class InputCreateProposalSchema(Schema):
    """Schema for creating a Proposal"""
    name = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(required=True, validate=validate.Length(min=1))
    dao_id = fields.Str(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    actions = fields.Dict(required=False, allow_none=True)

class ProposalUpdateSchema(Schema):
    """Schema for updating a Proposal"""
    name = fields.Str(validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(min=1))
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    actions = fields.Dict(allow_none=True)

class ProposalVoteSchema(Schema):
    """Schema for voting on a Proposal"""
    vote = fields.Str(required=True, validate=validate.OneOf(["for", "against"]))

class ProposalSchemaResponse(Schema):
    """Schema for Proposal response"""
    action = fields.Str(required=True)
    proposal = fields.Nested(ProposalSchema, required=True)

class ProposalVoteResponse(Schema):
    """Schema for Proposal vote response"""
    action = fields.Str(required=True)
    vote_status = fields.Str(required=True, validate=validate.OneOf(["none", "for", "against"]))
    proposal = fields.Nested(ProposalSchema, required=True)
    for_votes_count = fields.Int(required=True)
    against_votes_count = fields.Int(required=True) 