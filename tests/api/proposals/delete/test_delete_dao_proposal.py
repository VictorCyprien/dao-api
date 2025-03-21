import pytest
import json
from unittest.mock import patch
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User
from api.models.proposal import Proposal


def test_delete_proposal_success(client: Flask, app: Flask, db: SQLAlchemy,
                              dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test successfully deleting a proposal as the creator"""
    # Make delete request
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "deleted"
    assert data["proposal"]["proposal_id"] == proposal.proposal_id
    
    # Verify proposal was deleted from database
    with app.app_context():
        deleted_proposal = Proposal.get_by_id(proposal.proposal_id, db.session)
        assert deleted_proposal is None


def test_delete_proposal_as_admin(client: Flask, app: Flask, db: SQLAlchemy,
                               dao: DAO, proposal: Proposal, 
                               sayori: User, sayori_logged_in: str):
    """Test deleting a proposal as a DAO admin (not the creator)"""
    # Add sayori as an admin of the DAO
    with app.app_context():
        current_sayori = db.session.merge(sayori)
        current_dao = db.session.merge(dao)
        current_dao.admins.append(current_sayori)
        current_dao.members.append(current_sayori)
        db.session.commit()
    
    # Make delete request as admin
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {sayori_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "deleted"
    assert data["proposal"]["proposal_id"] == proposal.proposal_id
    
    # Verify proposal was deleted from database
    with app.app_context():
        deleted_proposal = Proposal.get_by_id(proposal.proposal_id, db.session)
        assert deleted_proposal is None


def test_delete_proposal_dao_not_found(client: Flask, proposal: Proposal, victor_logged_in: str):
    """Test deleting a proposal for a non-existent DAO"""
    # Make delete request with non-existent DAO
    response = client.delete(
        f"/proposals/dao/non-existent-dao/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "This DAO doesn't exist !" in data["message"]


def test_delete_proposal_not_found(client: Flask, dao: DAO, victor_logged_in: str):
    """Test deleting a non-existent proposal"""
    # Make delete request with non-existent proposal
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/non-existent-proposal",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "Proposal not found" in data["message"]


def test_delete_proposal_unauthorized(client: Flask, dao: DAO, proposal: Proposal):
    """Test deleting a proposal without authentication"""
    # Make delete request without authentication
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}"
    )
    
    # Verify response
    assert response.status_code == 401


def test_delete_proposal_wrong_user(client: Flask, dao: DAO, proposal: Proposal, 
                                  natsuki: User, natsuki_logged_in: str):
    """Test deleting a proposal by a user who is not the creator or admin"""
    # Make delete request as non-creator/non-admin
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}",
        headers={"Authorization": f"Bearer {natsuki_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["code"] == 401
    assert "Only the creator or DAO admin can delete this proposal" in data["message"]


def test_delete_vote(client: Flask, app: Flask, db: SQLAlchemy, dao: DAO, 
                   proposal: Proposal, victor: User, victor_logged_in: str):
    """Test removing a vote from a proposal"""
    # First, add a vote
    with app.app_context():
        current_proposal = db.session.merge(proposal)
        current_victor = db.session.merge(victor)
        current_proposal.vote_for(current_victor)
        db.session.commit()
    
    # Make delete vote request
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "vote_removed"
    assert victor.user_id not in [voter["user_id"] for voter in data["proposal"]["for_voters"]]
    assert data["proposal"]["for_votes_count"] == 0


def test_delete_vote_no_vote(client: Flask, dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test removing a vote when user hasn't voted"""
    # Make delete vote request without having voted
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["code"] == 400
    assert "No vote found to remove" in data["message"]


def test_delete_vote_inactive_proposal(client: Flask, app: Flask, db: SQLAlchemy, dao: DAO, 
                                     inactive_proposal: Proposal, victor: User, victor_logged_in: str):
    """Test removing a vote from an inactive proposal"""
    # Make delete vote request on inactive proposal
    response = client.delete(
        f"/proposals/dao/{dao.dao_id}/proposals/{inactive_proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["code"] == 400
    assert "This proposal is not currently active for voting" in data["message"] 