from typing import Dict

from flask import current_app
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy

from api.models.proposal import Proposal
from api.models.dao import DAO
from api.models.user import User
from api.schemas.proposal_schemas import (
    ProposalSchema,
    InputCreateProposalSchema,
    ProposalUpdateSchema,
    ProposalSchemaResponse,
    ProposalVoteSchema,
    ProposalVoteResponse
)
from api.schemas.communs_schemas import PagingError
from api.views.proposals.proposals_blp import proposals_blp
from helpers.errors_file import BadRequest, NotFound, ErrorHandler, Unauthorized
from helpers.logging_file import Logger

logger = Logger()


@proposals_blp.route("/dao/<string:dao_id>/proposals")
class DAOProposalsView(MethodView):
    
    @proposals_blp.doc(operationId='GetProposalsByDAO')
    @proposals_blp.response(404, PagingError, description="DAO not found")
    @proposals_blp.response(200, ProposalSchema(many=True), description="List of proposals for the DAO")
    def get(self, dao_id: str):
        """Get all proposals for a specific DAO"""
        db: SQLAlchemy = current_app.db
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get proposals for this DAO
        proposals = Proposal.get_by_dao_id(dao_id, db.session)
        return proposals
    
    @proposals_blp.arguments(InputCreateProposalSchema)
    @proposals_blp.doc(operationId='CreateProposalForDAO')
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(404, PagingError, description="DAO not found")
    @proposals_blp.response(400, PagingError, description="Bad Request - Invalid data")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not a member of this DAO")
    @proposals_blp.response(201, ProposalSchemaResponse, description="Proposal created successfully")
    @jwt_required()
    def post(self, input_data: Dict, dao_id: str):
        """Create a new proposal for this specific DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Get the DAO
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Check if user is a member or admin of the DAO
        if auth_user not in dao.members:
            raise Unauthorized("User is not a member of this DAO")
        
        # Override any dao_id in input_data with the path parameter
        input_data["dao_id"] = dao_id
        # Add the user ID to the input data
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
            logger.error(f"Error creating proposal: {error}")
            raise BadRequest("Failed to create proposal")


@proposals_blp.route("/dao/<string:dao_id>/proposals/active")
class DAOActiveProposalsView(MethodView):
    
    @proposals_blp.doc(operationId='GetActiveProposalsByDAO')
    @proposals_blp.response(404, PagingError, description="DAO not found")
    @proposals_blp.response(200, ProposalSchema(many=True), description="List of active proposals for the DAO")
    def get(self, dao_id: str):
        """Get all active proposals for a specific DAO"""
        db: SQLAlchemy = current_app.db
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get all proposals for this DAO
        all_proposals = Proposal.get_by_dao_id(dao_id, db.session)
        
        # Filter for active proposals
        active_proposals = [p for p in all_proposals if p.is_active()]
        
        return active_proposals


@proposals_blp.route("/dao/<string:dao_id>/proposals/<string:proposal_id>")
class OneDAOProposalView(MethodView):
    
    @proposals_blp.doc(operationId='GetDAOProposalById')
    @proposals_blp.response(404, PagingError, description="DAO or Proposal not found")
    @proposals_blp.response(400, PagingError, description="Proposal does not belong to this DAO")
    @proposals_blp.response(200, ProposalSchema, description="Proposal retrieved successfully")
    def get(self, dao_id: str, proposal_id: str):
        """Get a specific proposal for a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this DAO
        if proposal.dao_id != dao_id:
            raise BadRequest("Proposal does not belong to this DAO")
        
        return proposal
    
    @proposals_blp.arguments(ProposalUpdateSchema)
    @proposals_blp.doc(operationId='UpdateDAOProposal')
    @proposals_blp.response(404, PagingError, description="DAO or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not the creator or an admin")
    @proposals_blp.response(400, PagingError, description="Bad Request - Invalid data or Proposal does not belong to this DAO")
    @proposals_blp.response(200, ProposalSchemaResponse, description="Proposal updated successfully")
    @jwt_required()
    def put(self, input_data: Dict, dao_id: str, proposal_id: str):
        """Update a proposal for a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this DAO
        if proposal.dao_id != dao_id:
            raise BadRequest("Proposal does not belong to this DAO")
        
        # Check if user is creator or admin
        if proposal.created_by != auth_user.user_id:
            if auth_user not in dao.admins:
                raise Unauthorized("Only the creator, DAO admin or user who has created the proposal can update this proposal")
        
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
            logger.error(f"Error updating proposal: {error}")
            raise BadRequest("Failed to update proposal")
    
    @proposals_blp.doc(operationId='DeleteDAOProposal')
    @proposals_blp.response(404, PagingError, description="DAO or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not the creator or an admin")
    @proposals_blp.response(400, PagingError, description="Bad Request - Error deleting proposal or Proposal does not belong to this DAO")
    @proposals_blp.response(200, ProposalSchemaResponse, description="Proposal deleted successfully")
    @jwt_required()
    def delete(self, dao_id: str, proposal_id: str):
        """Delete a proposal for a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this DAO
        if proposal.dao_id != dao_id:
            raise BadRequest("Proposal does not belong to this DAO")
        
        # Check if user is creator or admin
        if proposal.created_by != auth_user.user_id and auth_user not in dao.admins:
            raise Unauthorized("Only the creator or DAO admin can delete this proposal")
        
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
            logger.error(f"Error deleting proposal: {error}")
            raise BadRequest("Failed to delete proposal")


@proposals_blp.route("/dao/<string:dao_id>/proposals/<string:proposal_id>/vote")
class DAOProposalVoteView(MethodView):
    
    @proposals_blp.doc(operationId='GetProposalVotes')
    @proposals_blp.response(404, PagingError, description="DAO or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(400, PagingError, description="Bad Request - Proposal does not belong to this DAO")
    @proposals_blp.response(200, ProposalVoteResponse, description="Vote counts retrieved successfully")
    @jwt_required()
    def get(self, dao_id: str, proposal_id: str):
        """Get vote counts for a proposal"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user (for permission checking)
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this DAO
        if proposal.dao_id != dao_id:
            raise BadRequest("Proposal does not belong to this DAO")
        
        # Determine current user's vote status
        vote_status = "none"
        if auth_user in proposal.for_voters:
            vote_status = "for"
        elif auth_user in proposal.against_voters:
            vote_status = "against"
        
        # Return both the vote status and vote counts
        return {
            "action": "get_votes",
            "vote_status": vote_status,
            "proposal": proposal,
            "for_votes_count": proposal.for_votes_count,
            "against_votes_count": proposal.against_votes_count
        }
    
    @proposals_blp.arguments(ProposalVoteSchema)
    @proposals_blp.doc(operationId='VoteOnDAOProposal')
    @proposals_blp.response(404, PagingError, description="DAO or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(403, PagingError, description="Forbidden - User is not a member of this DAO")
    @proposals_blp.response(400, PagingError, description="Bad Request - Proposal is not active, user has already voted, or proposal does not belong to this DAO")
    @proposals_blp.response(200, ProposalVoteResponse, description="Vote recorded successfully")
    @jwt_required()
    def post(self, input_data: Dict, dao_id: str, proposal_id: str):
        """Vote on a proposal for a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this DAO
        if proposal.dao_id != dao_id:
            raise BadRequest("Proposal does not belong to this DAO")
        
        # Check if user is a member of the DAO
        if auth_user not in dao.members:
            raise Unauthorized("Only DAO members can vote on proposals")
        
        # Check if proposal is active
        if not proposal.is_active():
            raise BadRequest("This proposal is not currently active for voting")
        
        try:
            # Process the vote
            vote_type = input_data["vote"]
            
            # Check if the user has already voted
            if auth_user in proposal.for_voters or auth_user in proposal.against_voters:
                # Remove previous vote
                proposal.remove_vote(auth_user)
            
            # Record the vote
            if vote_type == "for":
                success = proposal.vote_for(auth_user)
            else:  # vote_type == "against"
                success = proposal.vote_against(auth_user)
            
            if not success:
                raise BadRequest("Failed to record vote")
            
            db.session.commit()
            
            return {
                "action": f"voted_{vote_type}",
                "proposal": proposal
            }
            
        except Exception as error:
            db.session.rollback()
            logger.error(f"Error voting on proposal: {error}")
            raise BadRequest("Failed to process vote")
    

    @proposals_blp.doc(operationId='RemoveVoteFromDAOProposal')
    @proposals_blp.response(404, PagingError, description="DAO or Proposal not found")
    @proposals_blp.response(401, PagingError, description="Unauthorized - Invalid or missing token")
    @proposals_blp.response(400, PagingError, description="Bad Request - Proposal is not active, user has not voted, or proposal does not belong to this DAO")
    @proposals_blp.response(200, ProposalVoteResponse, description="Vote removed successfully")
    @jwt_required()
    def delete(self, dao_id: str, proposal_id: str):
        """Remove vote from a proposal for a DAO"""
        db: SQLAlchemy = current_app.db
        
        # Get authenticated user
        auth_user = User.get_by_id(get_jwt_identity(), db.session)
        
        # Verify DAO exists
        dao = DAO.get_by_id(dao_id, db.session)
        if dao is None:
            raise NotFound(ErrorHandler.DAO_NOT_FOUND)
        
        # Get proposal
        proposal = Proposal.get_by_id(proposal_id, db.session)
        if proposal is None:
            raise NotFound("Proposal not found")
        
        # Verify proposal belongs to this DAO
        if proposal.dao_id != dao_id:
            raise BadRequest("Proposal does not belong to this DAO")
        
        # Check if proposal is active
        if not proposal.is_active():
            raise BadRequest("This proposal is not currently active for voting")
        
        # Remove the vote
        success = proposal.remove_vote(auth_user)
        
        if not success:
            raise BadRequest("No vote found to remove")
        
        db.session.commit()
        
        return {
            "action": "vote_removed",
            "proposal": proposal
        }
        
