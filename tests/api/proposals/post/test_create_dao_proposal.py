import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch
from flask.app import Flask

from api.models.dao import DAO
from api.models.user import User
from api.models.proposal import Proposal


def test_create_proposal_success(client: Flask, dao: DAO, victor: User, victor_logged_in: str):
    """Test successfully creating a proposal for a DAO"""
    # Prepare proposal data
    start_time = datetime.now() + timedelta(days=1)
    end_time = datetime.now() + timedelta(days=7)
    
    proposal_data = {
        "name": "New Test Proposal",
        "description": "A new test proposal for the DAO",
        "dao_id": dao.dao_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "actions": {"action_type": "add_wallet", "target_address": "0xTestWallet"}
    }
    
    # Make request to create proposal
    response = client.post(
        f"/proposals/dao/{dao.dao_id}/proposals",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=proposal_data
    )
    
    # Verify response
    print(response.data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["action"] == "created"
    assert data["proposal"]["name"] == proposal_data["name"]
    assert data["proposal"]["description"] == proposal_data["description"]
    assert data["proposal"]["dao_id"] == dao.dao_id
    assert data["proposal"]["created_by"] == victor.user_id


def test_create_proposal_dao_not_found(client: Flask, victor: User, victor_logged_in: str):
    """Test creating a proposal for a non-existent DAO"""
    # Prepare proposal data
    start_time = datetime.now() + timedelta(days=1)
    end_time = datetime.now() + timedelta(days=7)
    
    proposal_data = {
        "name": "New Test Proposal",
        "description": "A new test proposal for the DAO",
        "dao_id": "non-existent-dao",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    # Make request to create proposal for non-existent DAO
    response = client.post(
        "/proposals/dao/non-existent-dao/proposals",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=proposal_data
    )
    
    # Verify response
    print(response.data)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "This DAO doesn't exist !" in data["message"]


def test_create_proposal_unauthorized(client: Flask, dao: DAO):
    """Test creating a proposal without authentication"""
    # Prepare proposal data
    start_time = datetime.now() + timedelta(days=1)
    end_time = datetime.now() + timedelta(days=7)
    
    proposal_data = {
        "name": "New Test Proposal",
        "description": "A new test proposal for the DAO",
        "dao_id": dao.dao_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    # Make request without authentication
    response = client.post(
        f"/proposals/dao/{dao.dao_id}/proposals",
        json=proposal_data
    )
    
    # Verify response
    assert response.status_code == 401


def test_create_proposal_non_member(client: Flask, dao: DAO, natsuki: User, natsuki_logged_in: str):
    """Test creating a proposal by a user who is not a member of the DAO"""
    # Prepare proposal data
    start_time = datetime.now() + timedelta(days=1)
    end_time = datetime.now() + timedelta(days=7)
    
    proposal_data = {
        "name": "New Test Proposal",
        "description": "A new test proposal for the DAO",
        "dao_id": dao.dao_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    # Make request as non-member
    response = client.post(
        f"/proposals/dao/{dao.dao_id}/proposals",
        headers={"Authorization": f"Bearer {natsuki_logged_in}"},
        json=proposal_data
    )
    
    # Verify response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["code"] == 401
    assert "User is not a member of this DAO" in data["message"]


def test_create_proposal_invalid_data(client: Flask, dao: DAO, victor_logged_in: str):
    """Test creating a proposal with invalid data"""
    # Missing required fields
    proposal_data = {
        "name": "New Test Proposal"
        # Missing description, start_time, end_time
    }
    
    # Make request with invalid data
    response = client.post(
        f"/proposals/dao/{dao.dao_id}/proposals",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=proposal_data
    )
    
    # Verify response
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data["code"] == 422


def test_create_proposal_vote(client: Flask, dao: DAO, proposal: Proposal, 
                             victor: User, victor_logged_in: str):
    """Test voting on a proposal"""
    # Vote data
    vote_data = {
        "vote": "for"
    }
    
    # Make vote request
    response = client.post(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=vote_data
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "voted_for"
    assert victor.user_id in [voter["user_id"] for voter in data["proposal"]["for_voters"]]
    assert data["proposal"]["for_votes_count"] == 1
    

def test_create_proposal_vote_not_member(client: Flask, dao: DAO, proposal: Proposal, 
                                        natsuki_logged_in: str):
    """Test voting on a proposal as a non-member"""
    # Vote data
    vote_data = {
        "vote": "for"
    }
    
    # Make vote request as non-member
    response = client.post(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {natsuki_logged_in}"},
        json=vote_data
    )
    
    # Verify response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["code"] == 401
    assert "Only DAO members can vote on proposals" in data["message"]


def test_create_proposal_vote_inactive(client: Flask, dao: DAO, inactive_proposal: Proposal,
                                      victor_logged_in: str):
    """Test voting on an inactive proposal"""
    # Vote data
    vote_data = {
        "vote": "for"
    }
    
    # Make vote request for inactive proposal
    response = client.post(
        f"/proposals/dao/{dao.dao_id}/proposals/{inactive_proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=vote_data
    )
    
    # Verify response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["code"] == 400
    assert "This proposal is not currently active for voting" in data["message"] 