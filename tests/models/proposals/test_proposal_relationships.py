import pytest
from datetime import datetime, timedelta
from unittest.mock import ANY

from api.models.proposal import Proposal
from api.models.user import User
from api.models.dao import DAO


def test_proposal_dao_relationship(app, db, victor: User, dao: DAO):
    """Test the relationship between Proposal and DAO"""
    # Create a proposal for the DAO
    proposal_data = {
        "name": "DAO Relationship Test",
        "description": "Testing proposal-DAO relationship",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    with app.app_context():
        # Get current session references to user and dao
        current_dao = db.session.merge(dao)
        
        # Create and save proposal
        proposal = Proposal.create(proposal_data)
        db.session.add(proposal)
        db.session.commit()
        
        # Verify the relationship from proposal to DAO
        assert proposal.dao is not None
        assert proposal.dao.dao_id == current_dao.dao_id
        assert proposal.dao.name == current_dao.name
        
        # Verify the relationship from DAO to proposal
        db.session.refresh(current_dao)  # Now refresh works because the DAO is attached to this session
        assert proposal in current_dao.proposals
        
        # Clean up
        db.session.delete(proposal)
        db.session.commit()


def test_proposal_creator_relationship(app, db, victor: User, dao: DAO):
    """Test the relationship between Proposal and its creator (User)"""
    # Create a proposal
    proposal_data = {
        "name": "Creator Relationship Test",
        "description": "Testing proposal-creator relationship",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    with app.app_context():
        # Get current session reference to user
        current_victor = db.session.merge(victor)
        
        # Create and save proposal
        proposal = Proposal.create(proposal_data)
        db.session.add(proposal)
        db.session.commit()
        
        # Verify the relationship from proposal to creator
        assert proposal.creator is not None
        assert proposal.creator.user_id == current_victor.user_id
        assert proposal.creator.username == current_victor.username
        
        # Verify the relationship from creator to proposal
        db.session.refresh(current_victor)
        assert proposal in current_victor.created_proposals
        
        # Clean up
        db.session.delete(proposal)
        db.session.commit()


def test_proposal_voters_relationship(app, db, victor: User, sayori: User, dao: DAO):
    """Test the relationships between Proposal and its voters"""
    # Create a proposal
    proposal_data = {
        "name": "Voters Relationship Test",
        "description": "Testing proposal-voters relationship",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    with app.app_context():
        # Get merged references to users
        current_victor = db.session.merge(victor)
        current_sayori = db.session.merge(sayori)
        
        # Create and save proposal
        proposal = Proposal.create(proposal_data)
        db.session.add(proposal)
        db.session.commit()
        
        # Add votes
        proposal.vote_for(current_victor)
        proposal.vote_against(current_sayori)
        db.session.commit()
        
        # Refresh users to ensure we get the updated relationship data
        db.session.refresh(current_victor)
        db.session.refresh(current_sayori)
        
        # Verify relationship from proposal to voters
        assert current_victor in proposal.for_voters
        assert current_sayori in proposal.against_voters
        
        # Verify relationship from voters to proposal
        assert proposal in current_victor.for_votes
        assert proposal in current_sayori.against_votes
        
        # Test removing votes
        proposal.remove_vote(current_victor)
        db.session.commit()
        db.session.refresh(current_victor)
        
        # Verify relationship is removed
        assert current_victor not in proposal.for_voters
        assert proposal not in current_victor.for_votes
        
        # Clean up
        db.session.delete(proposal)
        db.session.commit()


def test_cascade_delete_dao(app, db, victor: User, dao: DAO):
    """Test that deleting a DAO cascades to delete its proposals"""
    # Create a few proposals for the DAO
    proposal1_data = {
        "name": "Cascade Test 1",
        "description": "Testing cascade delete 1",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal2_data = {
        "name": "Cascade Test 2",
        "description": "Testing cascade delete 2",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    with app.app_context():
        # Get current session references
        current_dao = db.session.merge(dao)
        
        # Create and save proposals
        proposal1 = Proposal.create(proposal1_data)
        proposal2 = Proposal.create(proposal2_data)
        db.session.add(proposal1)
        db.session.add(proposal2)
        db.session.commit()
        
        # Store proposal IDs
        p1_id = proposal1.proposal_id
        p2_id = proposal2.proposal_id
        
        # Verify proposals exist
        assert Proposal.get_by_id(p1_id, db.session) is not None
        assert Proposal.get_by_id(p2_id, db.session) is not None
        
        # Now delete the DAO
        db.session.delete(current_dao)
        db.session.commit()
        
        # Verify proposals were cascade-deleted
        assert Proposal.get_by_id(p1_id, db.session) is None
        assert Proposal.get_by_id(p2_id, db.session) is None


def test_multiple_proposals_per_dao(app, db, victor: User, dao: DAO):
    """Test that a DAO can have multiple proposals"""
    # Create multiple proposals for the same DAO
    proposals_data = [
        {
            "name": f"Multi-Proposal Test {i}",
            "description": f"Testing multiple proposals per DAO {i}",
            "dao_id": dao.dao_id,
            "created_by": victor.user_id,
            "created_by_username": victor.username,
            "start_time": datetime.now() - timedelta(days=1),
            "end_time": datetime.now() + timedelta(days=5)
        }
        for i in range(1, 6)  # Create 5 proposals
    ]
    
    with app.app_context():
        # Get current session reference to DAO
        current_dao = db.session.merge(dao)
        
        # Create and save all proposals
        proposals = []
        for proposal_data in proposals_data:
            proposal = Proposal.create(proposal_data)
            db.session.add(proposal)
            proposals.append(proposal)
        
        db.session.commit()
        
        # Refresh DAO to ensure we get the updated relationship data
        db.session.refresh(current_dao)
        
        # Verify all proposals are linked to the DAO
        for proposal in proposals:
            assert proposal.dao.dao_id == current_dao.dao_id
            assert proposal in current_dao.proposals
        
        # Verify DAO has all proposals
        assert len(current_dao.proposals) >= len(proposals)
        for proposal in proposals:
            assert proposal in current_dao.proposals
        
        # Clean up
        for proposal in proposals:
            db.session.delete(proposal)
        db.session.commit() 