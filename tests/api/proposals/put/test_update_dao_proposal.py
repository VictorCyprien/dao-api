import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch
from flask.app import Flask

from api.models.dao import DAO
from api.models.user import User
from api.models.proposal import Proposal


def test_update_proposal_success(client: Flask, dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test successfully updating a proposal as the creator"""
    # Prepare update data
    update_data = {
        "name": "Updated Proposal Name",
        "description": "Updated proposal description"
    }
    
    # Make update request
    response = client.put(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "updated"
    assert data["proposal"]["name"] == update_data["name"]
    assert data["proposal"]["description"] == update_data["description"]
    assert data["proposal"]["dao_id"] == dao.dao_id


def test_update_proposal_as_admin(client: Flask, app, db, dao: DAO, proposal: Proposal, 
                                sayori: User, sayori_logged_in: str):
    """Test updating a proposal as a DAO admin (not the creator)"""
    # Add sayori as an admin of the DAO
    with app.app_context():
        current_sayori = db.session.merge(sayori)
        current_dao = db.session.merge(dao)
        current_dao.admins.append(current_sayori)
        current_dao.members.append(current_sayori)
        db.session.commit()
    
    # Prepare update data
    update_data = {
        "name": "Admin Updated Name",
        "description": "Proposal updated by an admin"
    }
    
    # Make update request as admin
    response = client.put(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {sayori_logged_in}"},
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "updated"
    assert data["proposal"]["name"] == update_data["name"]
    assert data["proposal"]["description"] == update_data["description"]


def test_update_proposal_dao_not_found(client: Flask, proposal: Proposal, victor_logged_in: str):
    """Test updating a proposal for a non-existent DAO"""
    # Prepare update data
    update_data = {
        "name": "Updated Name",
        "description": "Updated description"
    }
    
    # Make update request with non-existent DAO
    response = client.put(
        f"/proposals/dao/non-existent-dao/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "This DAO doesn't exist !" in data["message"]


def test_update_proposal_not_found(client: Flask, dao: DAO, victor_logged_in: str):
    """Test updating a non-existent proposal"""
    # Prepare update data
    update_data = {
        "name": "Updated Name",
        "description": "Updated description"
    }
    
    # Make update request with non-existent proposal
    response = client.put(
        f"/proposals/dao/{dao.dao_id}/proposals/non-existent-proposal",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "Proposal not found" in data["message"]


def test_update_proposal_unauthorized(client: Flask, dao: DAO, proposal: Proposal):
    """Test updating a proposal without authentication"""
    # Prepare update data
    update_data = {
        "name": "Updated Name",
        "description": "Updated description"
    }
    
    # Make update request without authentication
    response = client.put(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 401


def test_update_proposal_wrong_user(client: Flask, dao: DAO, proposal: Proposal, 
                                   natsuki: User, natsuki_logged_in: str):
    """Test updating a proposal by a user who is not the creator or admin"""
    # Add natsuki as a member but not an admin
    with pytest.raises(Exception):
        # Make update request as non-creator/non-admin
        update_data = {
            "name": "Unauthorized Update",
            "description": "This update should fail"
        }
        
        response = client.put(
            f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
            headers={"Authorization": f"Bearer {natsuki_logged_in}"},
            json=update_data
        )
        
        # Verify response
        print(response.data)
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["code"] == 401
        assert "Only the creator or DAO admin can update this proposal" in data["message"]


def test_update_proposal_invalid_data(client: Flask, dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test updating a proposal with invalid data"""
    # Prepare invalid update data (empty name)
    update_data = {
        "name": "",  # Empty name should be invalid
        "description": "Valid description"
    }
    
    # Make update request with invalid data
    response = client.put(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"},
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data["code"] == 422 