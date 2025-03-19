import json
import pytest


def test_get_pod_proposals(client, pod, pod_proposal):
    """Test getting all proposals for a POD"""
    response = client.get(f"/proposals/pod/{pod.pod_id}/proposals")
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["pod_id"] == pod.pod_id
    assert len(data["proposals"]) == 1
    assert data["total_count"] == 1
    assert data["proposals"][0]["proposal_id"] == pod_proposal.proposal_id

def test_get_pod_proposal_not_found(client):
    """Test getting proposals for a non-existent POD"""
    response = client.get("/proposals/pod/nonexistent/proposals")
    assert response.status_code == 404

def test_get_pod_proposal_by_id(client, pod, pod_proposal):
    """Test getting a specific proposal for a POD"""
    response = client.get(f"/proposals/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}")
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["proposal_id"] == pod_proposal.proposal_id
    assert data["pod_id"] == pod.pod_id

def test_get_pod_proposal_wrong_pod(client, pod, proposal):
    """Test getting a DAO proposal using the POD endpoint"""
    # This should fail because the proposal belongs to a DAO, not the POD
    response = client.get(f"/proposals/pod/{pod.pod_id}/proposals/{proposal.proposal_id}")
    assert response.status_code == 400

def test_get_active_pod_proposals(client, pod, pod_proposal):
    """Test getting active proposals for a POD"""
    response = client.get(f"/proposals/pod/{pod.pod_id}/proposals/active")
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["pod_id"] == pod.pod_id
    assert len(data["proposals"]) == 1  # One active proposal
    assert data["proposals"][0]["proposal_id"] == pod_proposal.proposal_id
    
def test_get_proposal_votes_no_vote(client, pod, pod_proposal, victor_in_pod, victor_logged_in):
    """Test getting vote counts for a proposal where user hasn't voted"""
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.get(
        f"/proposals/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}/vote",
        headers=headers
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["action"] == "get_votes"
    assert data["vote_status"] == "none"
    assert data["for_votes_count"] == 0
    assert data["against_votes_count"] == 0
    
def test_get_proposal_votes_voted_for(client, pod, pod_proposal, victor, victor_logged_in, db):
    """Test getting vote counts for a proposal where user voted 'for'"""
    # First add victor to POD and have them vote 'for'
    with client.application.app_context():
        current_pod = db.session.merge(pod)
        current_victor = db.session.merge(victor)
        current_pod.add_member(current_victor)
        
        current_proposal = db.session.merge(pod_proposal)
        current_proposal.vote_for(current_victor)
        db.session.commit()
        
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.get(
        f"/proposals/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}/vote",
        headers=headers
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["action"] == "get_votes"
    assert data["vote_status"] == "for"
    assert data["for_votes_count"] == 1
    assert data["against_votes_count"] == 0
    
def test_get_proposal_votes_voted_against(client, pod, pod_proposal, victor, victor_logged_in, db):
    """Test getting vote counts for a proposal where user voted 'against'"""
    # First add victor to POD and have them vote 'against'
    with client.application.app_context():
        current_pod = db.session.merge(pod)
        current_victor = db.session.merge(victor)
        current_pod.add_member(current_victor)
        
        current_proposal = db.session.merge(pod_proposal)
        current_proposal.vote_against(current_victor)
        db.session.commit()
        
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.get(
        f"/proposals/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}/vote",
        headers=headers
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["action"] == "get_votes"
    assert data["vote_status"] == "against"
    assert data["for_votes_count"] == 0
    assert data["against_votes_count"] == 1
    
def test_get_proposal_votes_pod_not_found(client, pod_proposal, victor_logged_in):
    """Test getting vote counts for a non-existent POD"""
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.get(
        f"/proposals/pod/nonexistent/proposals/{pod_proposal.proposal_id}/vote",
        headers=headers
    )
    
    assert response.status_code == 404
    
def test_get_proposal_votes_proposal_not_found(client, pod, victor_logged_in):
    """Test getting vote counts for a non-existent proposal"""
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.get(
        f"/proposals/pod/{pod.pod_id}/proposals/nonexistent/vote",
        headers=headers
    )
    
    assert response.status_code == 404
    
def test_get_proposal_votes_wrong_pod(client, pod, proposal, victor_logged_in):
    """Test getting vote counts for a proposal that doesn't belong to the POD"""
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.get(
        f"/proposals/pod/{pod.pod_id}/proposals/{proposal.proposal_id}/vote", 
        headers=headers
    )
    
    assert response.status_code == 400
    
def test_get_proposal_votes_unauthorized(client, pod, pod_proposal):
    """Test getting vote counts without authentication"""
    response = client.get(
        f"/proposals/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}/vote"
    )
    
    assert response.status_code == 401 