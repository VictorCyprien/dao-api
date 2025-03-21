import pytest
import json
from unittest.mock import patch
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User
from api.models.proposal import Proposal


def test_get_dao_proposals(client: Flask, dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test getting all proposals for a DAO"""
    # Make request to get all proposals for a DAO
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    
    # Check proposal data
    assert data[0]["proposal_id"] == proposal.proposal_id
    assert data[0]["name"] == proposal.name
    assert data[0]["description"] == proposal.description
    assert data[0]["dao_id"] == dao.dao_id
    assert data[0]["created_by"] == proposal.created_by


def test_get_dao_proposals_dao_not_found(client: Flask, victor_logged_in: str):
    """Test getting proposals for a DAO that doesn't exist"""
    # Make request to get proposals for non-existent DAO
    response = client.get(
        "/proposals/dao/non-existent-dao/proposals",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "This DAO doesn't exist !" in data["message"]


def test_get_active_dao_proposals(client: Flask, dao: DAO, proposal: Proposal, 
                                  inactive_proposal: Proposal, victor_logged_in: str):
    """Test getting active proposals for a DAO"""
    # Make request to get active proposals for DAO
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/active",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Should only include the active proposal, not the inactive one
    assert len(data) == 1
    assert data[0]["proposal_id"] == proposal.proposal_id
    assert data[0]["name"] == proposal.name
    assert data[0]["is_active"] == True


def test_get_dao_proposal_by_id(client: Flask, dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test getting a specific proposal by ID"""
    # Make request to get proposal by ID
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check proposal data
    assert data["proposal_id"] == proposal.proposal_id
    assert data["name"] == proposal.name
    assert data["description"] == proposal.description
    assert data["dao_id"] == dao.dao_id
    assert data["created_by"] == proposal.created_by


def test_get_dao_proposal_proposal_not_found(client: Flask, dao: DAO, victor_logged_in: str):
    """Test getting a proposal that doesn't exist"""
    # Make request for non-existent proposal
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/non-existent-proposal",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "Proposal not found" in data["message"]


def test_get_dao_proposal_wrong_dao(client: Flask, dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test getting a proposal with the wrong DAO ID"""
    # Make request with wrong DAO ID
    response = client.get(
        f"/proposals/dao/wrong-dao-id/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response (should be 404 DAO not found)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "This DAO doesn't exist !" in data["message"] 