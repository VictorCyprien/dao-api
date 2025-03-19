import json
from datetime import datetime, timedelta
import pytest
from api.models.dao import DAO
from api.models.pod import POD


def test_create_pod_proposal(client, pod: POD, victor_in_pod, victor_logged_in, dao: DAO):
    """Test creating a new proposal for a POD"""
    start_time = datetime.now() + timedelta(days=1)
    end_time = datetime.now() + timedelta(days=6)
    
    proposal_data = {
        "name": "New POD Proposal",
        "description": "A new proposal for testing",
        "dao_id": dao.dao_id,
        "pod_id": pod.pod_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "actions": {"action_type": "add_wallet", "target_address": "0xNewWallet"}
    }
    
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.post(
        f"/proposals/pod/{pod.pod_id}/proposals",
        json=proposal_data,
        headers=headers
    )
    
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert data["action"] == "created"
    assert data["proposal"]["name"] == "New POD Proposal"
    assert data["proposal"]["pod_id"] == pod.pod_id

def test_create_pod_proposal_unauthorized(client, pod: POD, natsuki_logged_in, dao: DAO):
    """Test creating a proposal by a non-member of the POD"""
    start_time = datetime.now() + timedelta(days=1)
    end_time = datetime.now() + timedelta(days=6)
    
    proposal_data = {
        "name": "Unauthorized Proposal",
        "description": "This shouldn't work",
        "dao_id": dao.dao_id,
        "pod_id": pod.pod_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    headers = {"Authorization": f"Bearer {natsuki_logged_in}"}
    response = client.post(
        f"/proposals/pod/{pod.pod_id}/proposals",
        json=proposal_data,
        headers=headers
    )
    
    assert response.status_code == 401

def test_vote_on_pod_proposal(client, pod, pod_proposal, victor, sayori, sayori_logged_in, db):
    """Test voting on a POD proposal"""
    # First add sayori to the POD to allow voting
    with client.application.app_context():
        current_pod = db.session.merge(pod)
        current_sayori = db.session.merge(sayori)
        current_pod.add_member(current_sayori)
        db.session.commit()
    
    vote_data = {"vote": "for"}
    headers = {"Authorization": f"Bearer {sayori_logged_in}"}
    
    response = client.post(
        f"/proposals/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}/vote",
        json=vote_data,
        headers=headers
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["action"] == "voted"
    assert data["vote_status"] == "for"
    assert data["for_votes_count"] == 1
    assert data["against_votes_count"] == 0

def test_vote_unauthorized(client, pod, pod_proposal, natsuki_logged_in):
    """Test voting by a non-member of the POD"""
    vote_data = {"vote": "for"}
    headers = {"Authorization": f"Bearer {natsuki_logged_in}"}
    
    response = client.post(
        f"/proposals/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}/vote",
        json=vote_data,
        headers=headers
    )
    
    assert response.status_code == 401 