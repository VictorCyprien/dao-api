import pytest
from datetime import datetime, timedelta
from unittest.mock import ANY

from api.models.proposal import Proposal
from api.models.user import User
from api.models.dao import DAO


def test_model_create_proposal(app, victor: User, dao: DAO):
    """Test creating a new proposal"""
    # Prepare proposal data
    start_time = datetime.now()
    end_time = datetime.now() + timedelta(days=7)
    
    proposal_data = {
        "name": "Test Proposal Creation",
        "description": "Testing proposal model creation",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time,
        "actions": {"action_type": "add_wallet", "target_address": "0xTestWallet"}
    }
    
    # Create proposal
    proposal = Proposal.create(proposal_data)
    
    # Verify proposal was created with correct attributes
    assert proposal.proposal_id == ANY  # ID is auto-generated
    assert proposal.name == "Test Proposal Creation"
    assert proposal.description == "Testing proposal model creation"
    assert proposal.dao_id == dao.dao_id
    assert proposal.created_by == victor.user_id
    assert proposal.start_time == start_time
    assert proposal.end_time == end_time
    assert proposal.actions == {"action_type": "add_wallet", "target_address": "0xTestWallet"}
    assert proposal.for_votes_count == 0
    assert proposal.against_votes_count == 0
    assert len(proposal.for_voters) == 0
    assert len(proposal.against_voters) == 0


def test_model_update_proposal(app, victor: User, dao: DAO):
    """Test updating a proposal"""
    # Create a proposal first
    start_time = datetime.now()
    end_time = datetime.now() + timedelta(days=7)
    
    proposal_data = {
        "name": "Original Proposal Name",
        "description": "Original proposal description",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Update data
    new_name = "Updated Proposal Name"
    new_description = "Updated proposal description"
    new_start_time = datetime.now() + timedelta(days=1)
    new_end_time = datetime.now() + timedelta(days=14)
    new_actions = {"action_type": "remove_wallet", "target_address": "0xOldWallet"}
    
    update_data = {
        "name": new_name,
        "description": new_description,
        "start_time": new_start_time,
        "end_time": new_end_time,
        "actions": new_actions
    }
    
    # Update proposal
    proposal.update(update_data)
    
    # Verify updated attributes
    assert proposal.name == new_name
    assert proposal.description == new_description
    assert proposal.start_time == new_start_time
    assert proposal.end_time == new_end_time
    assert proposal.actions == new_actions


def test_model_partial_update_proposal(app, victor: User, dao: DAO):
    """Test partially updating a proposal"""
    # Create a proposal first
    start_time = datetime.now()
    end_time = datetime.now() + timedelta(days=7)
    
    proposal_data = {
        "name": "Original Proposal Name",
        "description": "Original proposal description",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Update only name and description
    update_data = {
        "name": "Only Name Updated",
        "description": "Only description updated"
    }
    
    # Update proposal
    proposal.update(update_data)
    
    # Verify only specified fields were updated
    assert proposal.name == "Only Name Updated"
    assert proposal.description == "Only description updated"
    assert proposal.start_time == start_time  # Unchanged
    assert proposal.end_time == end_time  # Unchanged
    assert proposal.actions is None  # Unchanged


def test_model_vote_for_proposal(app, victor: User, sayori: User, dao: DAO):
    """Test voting for a proposal"""
    # Create a proposal
    proposal_data = {
        "name": "Voting Test Proposal",
        "description": "Testing voting functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Vote for the proposal
    result = proposal.vote_for(victor)
    
    # Verify vote was registered
    assert result is True
    assert victor in proposal.for_voters
    assert victor not in proposal.against_voters
    assert proposal.for_votes_count == 1
    assert proposal.against_votes_count == 0
    
    # Add another voter
    proposal.vote_for(sayori)
    
    # Verify both votes
    assert sayori in proposal.for_voters
    assert proposal.for_votes_count == 2


def test_model_vote_against_proposal(app, victor: User, sayori: User, dao: DAO):
    """Test voting against a proposal"""
    # Create a proposal
    proposal_data = {
        "name": "Voting Test Proposal",
        "description": "Testing voting functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Vote against the proposal
    result = proposal.vote_against(victor)
    
    # Verify vote was registered
    assert result is True
    assert victor in proposal.against_voters
    assert victor not in proposal.for_voters
    assert proposal.against_votes_count == 1
    assert proposal.for_votes_count == 0
    
    # Add another voter
    proposal.vote_against(sayori)
    
    # Verify both votes
    assert sayori in proposal.against_voters
    assert proposal.against_votes_count == 2


def test_model_remove_vote(app, victor: User, sayori: User, dao: DAO):
    """Test removing votes from a proposal"""
    # Create a proposal
    proposal_data = {
        "name": "Vote Removal Test",
        "description": "Testing vote removal functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Add votes - victor votes for, sayori votes against
    proposal.vote_for(victor)
    proposal.vote_against(sayori)
    
    # Verify initial votes
    assert victor in proposal.for_voters
    assert sayori in proposal.against_voters
    assert proposal.for_votes_count == 1
    assert proposal.against_votes_count == 1
    
    # Remove victor's vote
    result = proposal.remove_vote(victor)
    
    # Verify vote was removed
    assert result is True
    assert victor not in proposal.for_voters
    assert proposal.for_votes_count == 0
    assert proposal.against_votes_count == 1  # Unchanged
    
    # Remove sayori's vote
    result = proposal.remove_vote(sayori)
    
    # Verify vote was removed
    assert result is True
    assert sayori not in proposal.against_voters
    assert proposal.against_votes_count == 0
    
    # Try to remove a non-existent vote
    result = proposal.remove_vote(victor)
    
    # Verify operation failed
    assert result is False


def test_model_vote_duplicate_prevention(app, victor: User, dao: DAO):
    """Test that a user cannot vote multiple times"""
    # Create a proposal
    proposal_data = {
        "name": "Duplicate Vote Test",
        "description": "Testing duplicate vote prevention",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # First vote (should succeed)
    result1 = proposal.vote_for(victor)
    assert result1 is True
    assert proposal.for_votes_count == 1
    
    # Try to vote again (should fail)
    result2 = proposal.vote_for(victor)
    assert result2 is False
    assert proposal.for_votes_count == 1  # Count remains the same
    
    # Try to vote against after voting for (should fail)
    result3 = proposal.vote_against(victor)
    assert result3 is False
    assert proposal.for_votes_count == 1
    assert proposal.against_votes_count == 0


def test_model_proposal_is_active(app, victor: User, dao: DAO):
    """Test checking if a proposal is active based on time period"""
    # Create an active proposal (current time within start and end time)
    active_proposal_data = {
        "name": "Active Proposal",
        "description": "Testing is_active functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    active_proposal = Proposal.create(active_proposal_data)
    
    # Verify proposal is active
    assert active_proposal.is_active() is True
    
    # Create a future proposal (not started yet)
    future_proposal_data = {
        "name": "Future Proposal",
        "description": "Testing is_active functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    future_proposal = Proposal.create(future_proposal_data)
    
    # Verify future proposal is not active
    assert future_proposal.is_active() is False
    
    # Create a past proposal (already ended)
    past_proposal_data = {
        "name": "Past Proposal",
        "description": "Testing is_active functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=10),
        "end_time": datetime.now() - timedelta(days=5)
    }
    
    past_proposal = Proposal.create(past_proposal_data)
    
    # Verify past proposal is not active
    assert past_proposal.is_active() is False


def test_model_proposal_has_passed(app, victor: User, sayori: User, natsuki: User, dao: DAO):
    """Test checking if a proposal has passed based on votes"""
    # Create a proposal
    proposal_data = {
        "name": "Vote Counting Test",
        "description": "Testing has_passed functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # No votes yet - should not pass
    assert proposal.has_passed() is False
    
    # More votes against than for - should not pass
    proposal.vote_against(victor)
    proposal.vote_against(sayori)
    proposal.vote_for(natsuki)
    
    assert proposal.for_votes_count == 1
    assert proposal.against_votes_count == 2
    assert proposal.has_passed() is False
    
    # Change to more votes for than against - should pass
    proposal.remove_vote(victor)
    proposal.remove_vote(sayori)
    proposal.vote_for(victor)
    proposal.vote_for(sayori)
    
    assert proposal.for_votes_count == 3
    assert proposal.against_votes_count == 0
    assert proposal.has_passed() is True
    
    # Equal votes - should not pass (tie means not passed)
    proposal.remove_vote(victor)
    proposal.remove_vote(sayori)
    proposal.vote_against(victor)
    proposal.vote_against(sayori)
    
    assert proposal.for_votes_count == 1
    assert proposal.against_votes_count == 2
    assert proposal.has_passed() is False


def test_model_proposal_static_methods(app, db, victor: User, dao: DAO):
    """Test static methods like get_by_id, get_by_dao_id, get_active, etc."""
    # Create test proposals
    proposal1_data = {
        "name": "Active Proposal 1",
        "description": "First active proposal",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal2_data = {
        "name": "Active Proposal 2",
        "description": "Second active proposal",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=2),
        "end_time": datetime.now() + timedelta(days=3)
    }
    
    proposal3_data = {
        "name": "Inactive Proposal",
        "description": "An inactive proposal",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=10),
        "end_time": datetime.now() - timedelta(days=5)
    }
    
    with app.app_context():
        # Create and save proposals
        proposal1 = Proposal.create(proposal1_data)
        proposal2 = Proposal.create(proposal2_data)
        proposal3 = Proposal.create(proposal3_data)
        
        db.session.add(proposal1)
        db.session.add(proposal2)
        db.session.add(proposal3)
        db.session.commit()
        
        # Test get_by_id
        fetched_proposal = Proposal.get_by_id(proposal1.proposal_id, db.session)
        assert fetched_proposal.proposal_id == proposal1.proposal_id
        assert fetched_proposal.name == proposal1.name
        
        # Test get_by_dao_id
        dao_proposals = Proposal.get_by_dao_id(dao.dao_id, db.session)
        assert len(dao_proposals) == 3
        assert proposal1 in dao_proposals
        assert proposal2 in dao_proposals
        assert proposal3 in dao_proposals
        
        # Test get_active
        active_proposals = Proposal.get_active(db.session)
        assert len(active_proposals) == 2
        inactive_ids = [p.proposal_id for p in active_proposals]
        assert proposal1.proposal_id in inactive_ids
        assert proposal2.proposal_id in inactive_ids
        assert proposal3.proposal_id not in inactive_ids
        
        # Test get_all
        all_proposals = Proposal.get_all(db.session)
        assert len(all_proposals) >= 3  # At least our 3 proposals
        for p in [proposal1, proposal2, proposal3]:
            assert p in all_proposals
        
        # Clean up
        db.session.delete(proposal1)
        db.session.delete(proposal2)
        db.session.delete(proposal3)
        db.session.commit()


def test_model_proposal_to_dict(app, victor: User, dao: DAO):
    """Test the to_dict method for serialization"""
    # Create a proposal
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    proposal_data = {
        "name": "Serialization Test",
        "description": "Testing to_dict functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time,
        "actions": {"action_type": "add_wallet", "target_address": "0xTestWallet"}
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Add a vote
    proposal.vote_for(victor)
    
    # Convert to dict
    proposal_dict = proposal.to_dict()
    
    # Verify dict structure
    assert proposal_dict["proposal_id"] == proposal.proposal_id
    assert proposal_dict["name"] == "Serialization Test"
    assert proposal_dict["description"] == "Testing to_dict functionality"
    assert proposal_dict["dao_id"] == dao.dao_id
    assert proposal_dict["created_by"] == victor.user_id
    assert proposal_dict["start_time"] == start_time.isoformat()
    assert proposal_dict["end_time"] == end_time.isoformat()
    assert proposal_dict["actions"] == {"action_type": "add_wallet", "target_address": "0xTestWallet"}
    assert proposal_dict["for_votes_count"] == 1
    assert proposal_dict["against_votes_count"] == 0
    assert len(proposal_dict["for_voters"]) == 1
    assert proposal_dict["for_voters"][0]["user_id"] == victor.user_id
    assert proposal_dict["is_active"] is True
    assert proposal_dict["has_passed"] is True


def test_model_proposal_iter(app, victor: User, dao: DAO):
    """Test the __iter__ method for dict conversion"""
    # Create a proposal
    proposal_data = {
        "name": "Iter Test",
        "description": "Testing __iter__ functionality",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Convert to dict using dict()
    proposal_dict = dict(proposal)
    
    # Verify dict structure
    assert proposal_dict["proposal_id"] == proposal.proposal_id
    assert proposal_dict["name"] == "Iter Test"
    assert proposal_dict["description"] == "Testing __iter__ functionality"
    assert proposal_dict["dao_id"] == dao.dao_id
    assert proposal_dict["created_by"] == victor.user_id
    assert proposal_dict["for_votes_count"] == 0
    assert proposal_dict["against_votes_count"] == 0
    assert proposal_dict["is_active"] is True
    assert proposal_dict["has_passed"] is False 