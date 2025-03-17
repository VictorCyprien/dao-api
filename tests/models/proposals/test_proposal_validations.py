import pytest
from datetime import datetime, timedelta
import sys

from api.models.proposal import Proposal
from api.models.user import User
from api.models.dao import DAO


def test_proposal_id_generation(app):
    """Test that proposal IDs are correctly generated"""
    # Create multiple proposals and verify they all have unique IDs
    proposal_ids = [Proposal.generate_proposal_id() for _ in range(10)]
    
    # Verify all IDs are unique
    assert len(proposal_ids) == len(set(proposal_ids))
    
    # Verify ID format (should be a string representation of an integer)
    for proposal_id in proposal_ids:
        assert isinstance(proposal_id, str)
        assert proposal_id.isdigit()
        assert 1 <= int(proposal_id) <= sys.maxsize


def test_proposal_actions_optional(app, victor: User, dao: DAO):
    """Test that the actions field is optional"""
    # Create a proposal without actions
    proposal_data = {
        "name": "No Actions Test",
        "description": "Testing optional actions field",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(days=7)
        # No actions field
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Verify proposal was created successfully without actions
    assert proposal.proposal_id is not None
    assert proposal.actions is None


def test_proposal_date_validation(app, victor: User, dao: DAO):
    """Test validation of start and end dates"""
    # This test demonstrates expected behavior - in a real application,
    # you might want to add validation to prevent end_time being before start_time
    
    # Create a proposal with end_time before start_time
    start_time = datetime.now() + timedelta(days=5)
    end_time = datetime.now()  # Earlier than start_time
    
    proposal_data = {
        "name": "Invalid Dates Test",
        "description": "Testing date validation",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": start_time,
        "end_time": end_time
    }
    
    # Create proposal with invalid dates
    proposal = Proposal.create(proposal_data)
    
    # Verify proposal was created (current implementation doesn't validate dates)
    assert proposal.proposal_id is not None
    assert proposal.start_time == start_time
    assert proposal.end_time == end_time
    
    # Verify it's not active (as expected with these dates)
    assert proposal.is_active() is False


def test_proposal_vote_count_consistency(app, victor: User, sayori: User, natsuki: User, dao: DAO):
    """Test that vote counts are consistent with voter collections"""
    # Create a proposal
    proposal_data = {
        "name": "Vote Count Test",
        "description": "Testing vote count consistency",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Add votes
    proposal.vote_for(victor)
    proposal.vote_for(sayori)
    proposal.vote_against(natsuki)
    
    # Verify counts match collection lengths
    assert proposal.for_votes_count == len(proposal.for_voters)
    assert proposal.against_votes_count == len(proposal.against_voters)
    
    # Remove votes
    proposal.remove_vote(victor)
    
    # Verify counts are still consistent
    assert proposal.for_votes_count == len(proposal.for_voters)
    assert proposal.against_votes_count == len(proposal.against_voters)


def test_proposal_vote_state_transitions(app, victor: User, dao: DAO):
    """Test transitions of voting state (for/against/none)"""
    # Create a proposal
    proposal_data = {
        "name": "Vote State Test",
        "description": "Testing vote state transitions",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=5)
    }
    
    proposal = Proposal.create(proposal_data)
    
    # Initial state - no votes
    assert victor not in proposal.for_voters
    assert victor not in proposal.against_voters
    assert proposal.for_votes_count == 0
    assert proposal.against_votes_count == 0
    
    # Transition to voting "for"
    proposal.vote_for(victor)
    assert victor in proposal.for_voters
    assert victor not in proposal.against_voters
    assert proposal.for_votes_count == 1
    assert proposal.against_votes_count == 0
    
    # Transition to no vote
    proposal.remove_vote(victor)
    assert victor not in proposal.for_voters
    assert victor not in proposal.against_voters
    assert proposal.for_votes_count == 0
    assert proposal.against_votes_count == 0
    
    # Transition to voting "against"
    proposal.vote_against(victor)
    assert victor not in proposal.for_voters
    assert victor in proposal.against_voters
    assert proposal.for_votes_count == 0
    assert proposal.against_votes_count == 1
    
    # Transition back to no vote
    proposal.remove_vote(victor)
    assert victor not in proposal.for_voters
    assert victor not in proposal.against_voters
    assert proposal.for_votes_count == 0
    assert proposal.against_votes_count == 0


def test_proposal_extreme_time_values(app, victor: User, dao: DAO):
    """Test proposal with extreme time values"""
    # Create a proposal with far future dates
    far_future_start = datetime.now() + timedelta(days=365 * 10)  # 10 years from now
    far_future_end = datetime.now() + timedelta(days=365 * 20)    # 20 years from now
    
    future_proposal_data = {
        "name": "Far Future Proposal",
        "description": "Testing extreme future dates",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": far_future_start,
        "end_time": far_future_end
    }
    
    future_proposal = Proposal.create(future_proposal_data)
    
    # Verify proposal was created with these dates
    assert future_proposal.start_time == far_future_start
    assert future_proposal.end_time == far_future_end
    assert future_proposal.is_active() is False  # Not active yet
    
    # Create a proposal with far past dates
    far_past_start = datetime(1970, 1, 1)  # Unix epoch
    far_past_end = datetime(1980, 1, 1)    # 10 years after epoch
    
    past_proposal_data = {
        "name": "Far Past Proposal",
        "description": "Testing extreme past dates",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "start_time": far_past_start,
        "end_time": far_past_end
    }
    
    past_proposal = Proposal.create(past_proposal_data)
    
    # Verify proposal was created with these dates
    assert past_proposal.start_time == far_past_start
    assert past_proposal.end_time == far_past_end
    assert past_proposal.is_active() is False  # No longer active 