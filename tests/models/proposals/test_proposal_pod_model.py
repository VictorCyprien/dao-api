import pytest
from datetime import datetime, timedelta
from api.models.proposal import Proposal
from api.models.user import User
from api.models.pod import POD


def test_pod_proposal_creation(app, db, dao, pod, victor):
    """Test creating a proposal for a POD"""
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    proposal_data = {
        "name": "Test POD Proposal",
        "description": "A test proposal for the POD",
        "dao_id": dao.dao_id,
        "pod_id": pod.pod_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": start_time,
        "end_time": end_time
    }
    
    with app.app_context():
        proposal = Proposal.create(proposal_data)
        db.session.add(proposal)
        db.session.commit()
        
        # Verify the proposal was created with the POD ID
        saved_proposal = Proposal.get_by_id(proposal.proposal_id, db.session)
        assert saved_proposal is not None
        assert saved_proposal.pod_id == pod.pod_id
        assert saved_proposal.dao_id == dao.dao_id
        
        # Clean up
        db.session.delete(proposal)
        db.session.commit()

def test_pod_proposal_voting_restrictions(app, db, dao, pod, victor, sayori, natsuki):
    """Test that only POD members can vote on POD proposals"""
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    proposal_data = {
        "name": "Test POD Proposal",
        "description": "A test proposal for the POD",
        "dao_id": dao.dao_id,
        "pod_id": pod.pod_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": start_time,
        "end_time": end_time
    }
    
    with app.app_context():
        current_pod = db.session.merge(pod)
        current_victor = db.session.merge(victor)
        current_sayori = db.session.merge(sayori)
        current_natsuki = db.session.merge(natsuki)
        
        # Add Victor and Sayori to the POD
        current_pod.add_member(current_victor)
        current_pod.add_member(current_sayori)
        
        # Create proposal
        proposal = Proposal.create(proposal_data)
        db.session.add(proposal)
        db.session.commit()
        
        # Test voting - Victor should be able to vote (POD member)
        assert proposal.can_vote(current_victor) == True
        assert proposal.vote_for(current_victor) == True
        
        # Test voting - Sayori should be able to vote (POD member)
        assert proposal.can_vote(current_sayori) == True
        assert proposal.vote_against(current_sayori) == True
        
        # Test voting - Natsuki should not be able to vote (not a POD member)
        assert proposal.can_vote(current_natsuki) == False
        assert proposal.vote_for(current_natsuki) == False
        
        # Verify vote counts
        assert proposal.for_votes_count == 1
        assert proposal.against_votes_count == 1
        
        # Clean up
        db.session.delete(proposal)
        db.session.commit()

def test_dao_proposal_no_pod_restrictions(app, db, dao, victor, sayori, natsuki):
    """Test that DAO proposals don't have POD-based voting restrictions"""
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    proposal_data = {
        "name": "Test DAO Proposal",
        "description": "A test proposal for the DAO only",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": start_time,
        "end_time": end_time
    }
    
    with app.app_context():
        current_victor = db.session.merge(victor)
        current_sayori = db.session.merge(sayori)
        current_natsuki = db.session.merge(natsuki)
        
        # Create proposal
        proposal = Proposal.create(proposal_data)
        db.session.add(proposal)
        db.session.commit()
        
        # Test voting - all users should be able to vote since no POD restriction
        assert proposal.can_vote(current_victor) == True
        assert proposal.can_vote(current_sayori) == True
        assert proposal.can_vote(current_natsuki) == True
        
        # Clean up
        db.session.delete(proposal)
        db.session.commit()

def test_update_pod_id(app, db, dao, pod, victor):
    """Test updating the pod_id of an existing proposal"""
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    proposal_data = {
        "name": "Test DAO Proposal",
        "description": "A test proposal for the DAO only",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": start_time,
        "end_time": end_time
    }
    
    with app.app_context():
        # Create proposal without pod_id
        proposal = Proposal.create(proposal_data)
        db.session.add(proposal)
        db.session.commit()
        
        # Verify no pod_id initially
        assert proposal.pod_id is None
        
        # Update with pod_id
        update_data = {"pod_id": pod.pod_id}
        proposal.update(update_data)
        db.session.commit()
        
        # Verify pod_id was updated
        assert proposal.pod_id == pod.pod_id
        
        # Clean up
        db.session.delete(proposal)
        db.session.commit()

def test_get_proposals_by_pod(app, db, dao, pod, victor):
    """Test fetching proposals by POD ID"""
    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=5)
    
    # Create a POD proposal
    pod_proposal_data = {
        "name": "POD Proposal",
        "description": "A proposal for the POD",
        "dao_id": dao.dao_id,
        "pod_id": pod.pod_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": start_time,
        "end_time": end_time
    }
    
    # Create a DAO proposal
    dao_proposal_data = {
        "name": "DAO Proposal",
        "description": "A proposal for the DAO only",
        "dao_id": dao.dao_id,
        "created_by": victor.user_id,
        "created_by_username": victor.username,
        "start_time": start_time,
        "end_time": end_time
    }
    
    with app.app_context():
        # Create both proposals
        pod_proposal = Proposal.create(pod_proposal_data)
        dao_proposal = Proposal.create(dao_proposal_data)
        db.session.add(pod_proposal)
        db.session.add(dao_proposal)
        db.session.commit()
        
        # Test get_by_pod_id method
        pod_proposals = Proposal.get_by_pod_id(pod.pod_id, db.session)
        
        # Verify only the POD proposal is returned
        assert len(pod_proposals) == 1
        assert pod_proposals[0].proposal_id == pod_proposal.proposal_id
        assert pod_proposals[0].name == "POD Proposal"
        
        # Clean up
        db.session.delete(pod_proposal)
        db.session.delete(dao_proposal)
        db.session.commit() 