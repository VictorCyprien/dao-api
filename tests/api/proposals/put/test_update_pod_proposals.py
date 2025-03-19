import json
import pytest


def test_update_pod_proposal(client, pod, pod_proposal, victor_in_pod, victor_logged_in):
    """Test updating a POD proposal"""
    update_data = {
        "name": "Updated POD Proposal",
        "description": "Updated description"
    }
    
    headers = {"Authorization": f"Bearer {victor_logged_in}"}
    response = client.put(
        f"/proposals/dao/{pod.dao_id}/pod/{pod.pod_id}/proposals/{pod_proposal.proposal_id}",
        json=update_data,
        headers=headers
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data["action"] == "updated"
    assert data["proposal"]["name"] == "Updated POD Proposal"
    assert data["proposal"]["description"] == "Updated description" 