from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy

from api.models.proposal import Proposal
from api.models.dao import DAO
from api.models.pod import POD
from api.models.user import User
from api.schemas.proposal_schemas import (
    ProposalSchema,
    InputCreateProposalSchema,
    ProposalUpdateSchema,
    ProposalSchemaResponse,
    ProposalVoteSchema,
    ProposalVoteResponse,
    PodProposalQuerySchema,
    PodProposalListResponse
)
from api.schemas.communs_schemas import PagingError
from api.views.proposals.proposals_blp import proposals_blp
from helpers.errors_file import BadRequest, NotFound, ErrorHandler, Unauthorized
from helpers.logging_file import Logger

logger = Logger()


@proposals_blp.route("/pod/<string:pod_id>/proposals")
class PODProposalsView(MethodView):
    
    @proposals_blp.doc(operationId='GetProposalsByPOD')
    @proposals_blp.response(404, PagingError, description="POD not found")
    @proposals_blp.response(200, PodProposalListResponse, description="List of proposals for the POD")
    def get(self, pod_id: str):
        """Get all proposals for a specific POD"""
        db: SQLAlchemy = current_app.db
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Get proposals for this POD
        proposals = Proposal.get_by_pod_id(pod_id, db.session)
        
        return {
            "pod_id": pod_id,
            "proposals": proposals,
            "total_count": len(proposals)
        }
    
    @proposals_blp.arguments(InputCreateProposalSchema)
    @proposals_blp.doc(operationId='CreateProposalForPOD')
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(404, PagingError, description="POD not found")
    @proposals_blp.response(400, PagingError, description="Bad Request - Invalid data")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not a member of this POD")
    @proposals_blp.response(201, ProposalSchemaResponse, description="Proposal created successfully")
    @jwt_required()
    def post(self, input_data: Dict, pod_id: str):
        """Create a new proposal for this specific POD"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Get the POD
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Check if user is a member of the POD
        if auth_user not in pod.members:
            raise Unauthorized("User is not a member of this POD")
        
        # Get the DAO this POD belongs to
        dao = DAO.get_by_id(pod.dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Add required fields to the input data
        input_data["pod_id"] = pod_id
        input_data["dao_id"] = pod.dao_id
        input_data["created_by"] = auth_user.user_id
        
        try:
            # Create the proposal
            proposal = Proposal.create(input_data)
            
            # Add to database
            db.session.add(proposal)
            db.session.commit()
            
            return {
                "action": "created",
                "proposal": proposal
            }
            
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error creating POD proposal: {error}")
            raise BadRequest("Failed to create POD proposal")


@proposals_blp.route("/pod/<string:pod_id>/proposals/active")
class PODActiveProposalsView(MethodView):
    
    @proposals_blp.doc(operationId='GetActiveProposalsByPOD')
    @proposals_blp.response(404, PagingError, description="POD not found")
    @proposals_blp.response(200, PodProposalListResponse, description="List of active proposals for the POD")
    def get(self, pod_id: str):
        """Get all active proposals for a specific POD"""
        db: SQLAlchemy = current_app.db
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Get all proposals for this POD
        all_proposals = Proposal.get_by_pod_id(pod_id, db.session)
        
        # Filter for active proposals
        active_proposals = [p for p in all_proposals if p.is_active()]
        
        return {
            "pod_id": pod_id,
            "proposals": active_proposals,
            "total_count": len(active_proposals)
        }


@proposals_blp.route("/pod/<string:pod_id>/proposals/<string:proposal_id>")
class OnePODProposalView(MethodView):
    
    @proposals_blp.doc(operationId='GetPODProposalById')
    @proposals_blp.response(404, PagingError, description="POD or Proposal not found")
    @proposals_blp.response(400, PagingError, description="Proposal does not belong to this POD")
    @proposals_blp.response(200, ProposalSchema, description="Proposal retrieved successfully")
    def get(self, pod_id: str, proposal_id: str):
        """Get a specific proposal for a POD"""
        db: SQLAlchemy = current_app.db
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this POD
        if proposal.pod_id != pod_id:
            raise BadRequest("Proposal does not belong to this POD")
        
        return proposal
    
    @proposals_blp.arguments(ProposalUpdateSchema)
    @proposals_blp.doc(operationId='UpdatePODProposal')
    @proposals_blp.response(404, PagingError, description="POD or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not the creator or a POD member")
    @proposals_blp.response(400, PagingError, description="Bad Request - Invalid data or Proposal does not belong to this POD")
    @proposals_blp.response(200, ProposalSchemaResponse, description="Proposal updated successfully")
    @jwt_required()
    def put(self, input_data: Dict, pod_id: str, proposal_id: str):
        """Update a proposal for a POD"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this POD
        if proposal.pod_id != pod_id:
            raise BadRequest("Proposal does not belong to this POD")
        
        # Check if user is creator or a member of the POD
        if proposal.created_by != auth_user.user_id and auth_user not in pod.members:
            raise Unauthorized("Only the creator or a POD member can update this proposal")
        
        try:
            # Update proposal
            proposal.update(input_data)
            db.session.commit()
            
            return {
                "action": "updated",
                "proposal": proposal
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error updating POD proposal: {error}")
            raise BadRequest("Failed to update POD proposal")
    
    @proposals_blp.doc(operationId='DeletePODProposal')
    @proposals_blp.response(404, PagingError, description="POD or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not the creator of the proposal")
    @proposals_blp.response(400, PagingError, description="Bad Request - Error deleting proposal or Proposal does not belong to this POD")
    @proposals_blp.response(200, ProposalSchemaResponse, description="Proposal deleted successfully")
    @jwt_required()
    def delete(self, pod_id: str, proposal_id: str):
        """Delete a proposal for a POD"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this POD
        if proposal.pod_id != pod_id:
            raise BadRequest("Proposal does not belong to this POD")
        
        # Check if user is creator
        if proposal.created_by != auth_user.user_id:
            raise Unauthorized("Only the creator can delete this proposal")
        
        try:
            # Delete proposal
            db.session.delete(proposal)
            db.session.commit()
            
            return {
                "action": "deleted",
                "proposal": proposal
            }
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error deleting POD proposal: {error}")
            raise BadRequest("Failed to delete POD proposal")


@proposals_blp.route("/pod/<string:pod_id>/proposals/<string:proposal_id>/vote")
class PODProposalVoteView(MethodView):
    
    @proposals_blp.doc(operationId='GetPODProposalVotes')
    @proposals_blp.response(404, PagingError, description="POD or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(400, PagingError, description="Bad Request - Proposal does not belong to this POD")
    @proposals_blp.response(200, ProposalVoteResponse, description="Vote counts retrieved successfully")
    @jwt_required()
    def get(self, pod_id: str, proposal_id: str):
        """Get vote counts for a POD proposal"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this POD
        if proposal.pod_id != pod_id:
            raise BadRequest("Proposal does not belong to this POD")
        
        # Determine current user's vote status
        vote_status = "none"
        if auth_user in proposal.for_voters:
            vote_status = "for"
        elif auth_user in proposal.against_voters:
            vote_status = "against"
        
        return {
            "action": "get_votes",
            "vote_status": vote_status,
            "proposal": proposal,
            "for_votes_count": proposal.for_votes_count,
            "against_votes_count": proposal.against_votes_count
        }
    
    @proposals_blp.arguments(ProposalVoteSchema)
    @proposals_blp.doc(operationId='VoteOnPODProposal')
    @proposals_blp.response(404, PagingError, description="POD or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not a member of this POD")
    @proposals_blp.response(400, PagingError, description="Bad Request - Proposal is not active, user has already voted, or proposal does not belong to this POD")
    @proposals_blp.response(200, ProposalVoteResponse, description="Vote recorded successfully")
    @jwt_required()
    def post(self, input_data: Dict, pod_id: str, proposal_id: str):
        """Vote on a POD proposal"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Verify user is a member of the POD
        if auth_user not in pod.members:
            raise Unauthorized("Only POD members can vote on POD proposals")
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this POD
        if proposal.pod_id != pod_id:
            raise BadRequest("Proposal does not belong to this POD")
        
        # Check if proposal is active
        if not proposal.is_active():
            raise BadRequest("Proposal is not currently active for voting")
        
        # Check if user has already voted
        if auth_user in proposal.for_voters or auth_user in proposal.against_voters:
            raise BadRequest("User has already voted on this proposal")
        
        # Record the vote
        vote_type = input_data.get("vote")
        vote_success = False
        
        if vote_type == "for":
            vote_success = proposal.vote_for(auth_user)
        elif vote_type == "against":
            vote_success = proposal.vote_against(auth_user)
        
        if not vote_success:
            raise BadRequest("Failed to record vote")
        
        # Save the vote
        db.session.commit()
        
        return {
            "action": "voted",
            "vote_status": vote_type,
            "proposal": proposal,
            "for_votes_count": proposal.for_votes_count,
            "against_votes_count": proposal.against_votes_count
        }
    
    @proposals_blp.doc(operationId='RemoveVoteFromPODProposal')
    @proposals_blp.response(404, PagingError, description="POD or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(400, PagingError, description="Bad Request - Proposal is not active, user has not voted, or proposal does not belong to this POD")
    @proposals_blp.response(200, ProposalVoteResponse, description="Vote removed successfully")
    @jwt_required()
    def delete(self, pod_id: str, proposal_id: str):
        """Remove a vote from a POD proposal"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify POD exists
        pod = POD.get_by_id(pod_id, db.session)
        if pod is None:
            raise NotFound("POD not found")
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this POD
        if proposal.pod_id != pod_id:
            raise BadRequest("Proposal does not belong to this POD")
        
        # Check if proposal is active
        if not proposal.is_active():
            raise BadRequest("Proposal is not currently active for voting")
        
        # Check if user has voted
        if auth_user not in proposal.for_voters and auth_user not in proposal.against_voters:
            raise BadRequest("User has not voted on this proposal")
        
        # Remove the vote
        vote_success = proposal.remove_vote(auth_user)
        
        if not vote_success:
            raise BadRequest("Failed to remove vote")
        
        # Save the changes
        db.session.commit()
        
        return {
            "action": "vote_removed",
            "vote_status": "none",
            "proposal": proposal,
            "for_votes_count": proposal.for_votes_count,
            "against_votes_count": proposal.against_votes_count
        } 