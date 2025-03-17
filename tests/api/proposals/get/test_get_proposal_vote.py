import pytest
import json
from unittest.mock import patch
from flask.app import Flask
from datetime import datetime

from api.models.dao import DAO
from api.models.user import User
from api.models.proposal import Proposal


def test_get_vote_counts(client: Flask, dao: DAO, proposal: Proposal, victor_logged_in: str):
    """Test getting vote counts for a proposal"""
    # Make request to get vote counts
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "get_votes"
    assert data["vote_status"] == "none"
    assert "proposal" in data
    assert "for_votes_count" in data
    assert "against_votes_count" in data
    assert isinstance(data["for_votes_count"], int)
    assert isinstance(data["against_votes_count"], int)


def test_get_vote_counts_with_votes(client: Flask, app, db, dao: DAO, proposal: Proposal, 
                                 victor: User, victor_logged_in: str):
    """Test getting vote counts with existing votes"""
    # Add votes to the proposal
    with app.app_context():
        current_proposal = db.session.merge(proposal)
        
        # Create test users with all required fields
        now = datetime.now()
        test_users = []
        
        for i in range(1, 4):
            user = User(
                user_id=f"test-user-{i}",
                username=f"TestUser{i}",
                wallet_address=f"0xTestWallet{i}",
                email=f"testuser{i}@example.com",
                member_name=f"Test User {i}",
                discord_username=f"testuser{i}",
                twitter_username=f"testuser{i}",
                telegram_username=f"testuser{i}",
                last_login=now,
                last_interaction=now
            )
            test_users.append(user)
        
        db.session.add_all(test_users)
        db.session.flush()
        
        # Have users vote
        current_proposal.vote_for(test_users[0])
        current_proposal.vote_for(test_users[1])
        current_proposal.vote_against(test_users[2])
        
        # Make sure victor has not voted yet
        current_victor = db.session.merge(victor)
        assert current_victor not in current_proposal.for_voters
        assert current_victor not in current_proposal.against_voters
        
        db.session.commit()
    
    # Make request to get vote counts
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "get_votes"
    assert data["vote_status"] == "none"  # Victor still hasn't voted
    assert data["for_votes_count"] == 2
    assert data["against_votes_count"] == 1


def test_get_vote_counts_as_voter(client: Flask, app, db, dao: DAO, proposal: Proposal, 
                               victor: User, victor_logged_in: str):
    """Test getting vote counts as a user who has voted"""
    # Add vote for victor
    with app.app_context():
        current_victor = db.session.merge(victor)
        current_proposal = db.session.merge(proposal)
        current_proposal.vote_for(current_victor)
        db.session.commit()
    
    # Make request to get vote counts
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["action"] == "get_votes"
    assert data["vote_status"] == "for"  # Victor voted "for"
    assert data["for_votes_count"] == 1
    assert data["against_votes_count"] == 0


def test_get_vote_counts_dao_not_found(client: Flask, proposal: Proposal, victor_logged_in: str):
    """Test getting vote counts with non-existent DAO"""
    # Make request with non-existent DAO
    response = client.get(
        f"/proposals/dao/non-existent-dao/proposals/{proposal.proposal_id}/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "doesn't exist" in data["message"]


def test_get_vote_counts_proposal_not_found(client: Flask, dao: DAO, victor_logged_in: str):
    """Test getting vote counts with non-existent proposal"""
    # Make request with non-existent proposal
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/non-existent-proposal/vote",
        headers={"Authorization": f"Bearer {victor_logged_in}"}
    )
    
    # Verify response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["code"] == 404
    assert "Proposal not found" in data["message"]


def test_get_vote_counts_wrong_dao(client: Flask, app, db, dao: DAO, proposal: Proposal, 
                               victor_logged_in: str):
    """Test getting vote counts for a proposal with incorrect DAO ID"""
    # Create a new DAO with a different ID
    with app.app_context():
        other_dao_data = {
            "name": "Other DAO",
            "description": "Another DAO",
            "owner_id": "some-owner-id"
        }
        other_dao = DAO.create(other_dao_data)
        db.session.add(other_dao)
        db.session.commit()
        
        # Make request with wrong DAO ID
        response = client.get(
            f"/proposals/dao/{other_dao.dao_id}/proposals/{proposal.proposal_id}/vote",
            headers={"Authorization": f"Bearer {victor_logged_in}"}
        )
        
        # Verify response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["code"] == 400
        assert "Proposal does not belong to this DAO" in data["message"]
        
        # Clean up
        db.session.delete(other_dao)
        db.session.commit()


def test_get_vote_counts_unauthorized(client: Flask, dao: DAO, proposal: Proposal):
    """Test getting vote counts without authentication"""
    # Make request without token
    response = client.get(
        f"/proposals/dao/{dao.dao_id}/proposals/{proposal.proposal_id}/vote"
    )
    
    # Verify response
    assert response.status_code == 401 