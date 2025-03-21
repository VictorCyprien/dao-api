import json
import pytest


def test_delete_pod_proposal(client, pod, pod_proposal, victor_in_pod, victor_logged_in):
    """Test deleting a POD proposal"""
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.delete(
        f"/proposals/dao/{pod.dao_id}/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["action"] == "deleted"

def test_remove_vote(client, pod, pod_proposal, victor, sayori, sayori_logged_in, db):
    """Test removing a vote from a POD proposal"""
    # First add sayori to the POD and cast a vote
    with client.application.app_context():
        current_pod = db.session.merge(pod)
        current_sayori = db.session.merge(sayori)
        current_pod.add_member(current_sayori)
        
        current_proposal = db.session.merge(pod_proposal)
        current_proposal.vote_for(current_sayori)
        db.session.commit()
    
    headers = {"Authorization": f"Bearer {sayori_logged_in}"}
    
    response = client.delete(
        f"/proposals/dao/{pod.dao_id}/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}/vote",
        headers=headers
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["action"] == "vote_removed"
    assert data["vote_status"] == "none"
    assert data["for_votes_count"] == 0 