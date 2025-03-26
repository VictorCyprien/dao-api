import json
from unittest.mock import patch, MagicMock

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from api.models.dao import DAO
from api.models.user import User
from api.models.treasury import Token
from helpers.errors_file import ErrorHandler

from api.views.treasury.dao_treasury_view import make_get_treasury_key, make_put_treasury_key
from helpers.build_cache_key import make_token_key



@pytest.fixture
def mock_update_token_percentages():
    """Mock the _update_token_percentages method"""
    with patch.object(DAOTokensPercentagesView, '_update_token_percentages', 
              return_value=True) as mock:
        yield mock


class TestDAOTokensPercentagesView:
    """Tests for the DAOTokensPercentagesView PUT method"""
    
    def test_update_percentages_success(self, client, victor_logged_in, dao, token, mock_update_token_percentages):
        """Test successful token percentages update by an admin user"""
        # Make request with admin token
        response = client.put(
            f'/treasury/daos/{dao.dao_id}/update-percentages',
            headers={'Authorization': f'Bearer {victor_logged_in}'}
        )
        
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['action'] == 'updated_percentages'
        assert data['message'] == 'Token percentages updated successfully'
        assert 'tokens' in data
        assert 'total_value' in data
    
    def test_update_percentages_dao_not_found(self, client, victor_logged_in):
        """Test updating percentages for a non-existent DAO"""
        # Make request for non-existent DAO
        response = client.put(
            '/treasury/daos/non-existent-dao/update-percentages',
            headers={'Authorization': f'Bearer {victor_logged_in}'}
        )
        
        # Assert response
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['code'] == 404
        assert ErrorHandler.DAO_NOT_FOUND in data['message']
    
    def test_update_percentages_unauthorized(self, client, dao):
        """Test updating percentages without authentication"""
        # Make request without token
        response = client.put(f'/treasury/daos/{dao.dao_id}/update-percentages')
        
        # Assert response
        assert response.status_code == 401
    
    def test_update_percentages_not_admin(self, client, sayori_logged_in, dao):
        """Test updating percentages by a non-admin user"""
        # Make request with non-admin token (sayori is not an admin of the DAO)
        response = client.put(
            f'/treasury/daos/{dao.dao_id}/update-percentages',
            headers={'Authorization': f'Bearer {sayori_logged_in}'}
        )
        
        # Assert response
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['code'] == 401
        assert ErrorHandler.USER_NOT_ADMIN in data['message']
    
    @patch('api.models.treasury.Token.get_by_dao_id')
    def test_update_percentages_no_tokens(self, mock_get_tokens, client, victor_logged_in, dao):
        """Test updating percentages when there are no tokens"""
        # Mock Token.get_by_dao_id to return empty list
        mock_get_tokens.return_value = []
        
        # Make request
        response = client.put(
            f'/treasury/daos/{dao.dao_id}/update-percentages',
            headers={'Authorization': f'Bearer {victor_logged_in}'}
        )
        
        # Assert response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['action'] == 'updated_percentages'
        assert data['message'] == 'No tokens found in the treasury to update'
    
    def test_update_percentages_update_failure(self, client, victor_logged_in, dao, token):
        """Test when the token percentages update fails"""
        # Mock _update_token_percentages to return False (update failed)
        with patch.object(DAOTokensPercentagesView, '_update_token_percentages', 
                  return_value=False):
            
            # Make request
            response = client.put(
                f'/treasury/daos/{dao.dao_id}/update-percentages',
                headers={'Authorization': f'Bearer {victor_logged_in}'}
            )
            
            # Assert response
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['code'] == 400
            assert "Failed to update token percentages" in data['message']
    
    # Direct patch of the view's method instead of the imported function
    def test_cache_invalidation(self, client, victor_logged_in, dao, token, mock_update_token_percentages):
        """Test that cache invalidation is being called by checking the log output"""
        # Make request
        with patch('api.views.treasury.dao_treasury_view.logger') as mock_logger:
            response = client.put(
                f'/treasury/daos/{dao.dao_id}/update-percentages',
                headers={'Authorization': f'Bearer {victor_logged_in}'}
            )
            
            # Assert response
            assert response.status_code == 200
            
            # Check that the cache invalidation log message appears
            invalidation_log_calls = [
                call for call in mock_logger.info.call_args_list 
                if "Invalidated GET cache for DAO" in str(call)
            ]
            
            assert len(invalidation_log_calls) >= 1, "Cache invalidation log message not found"
    
    @patch('api.views.treasury.dao_treasury_view.logger')
    def test_cached_response(self, mock_logger, client, victor_logged_in, dao, token, mock_update_token_percentages):
        """Test that responses are properly cached"""
        # First request - should hit the database
        response1 = client.put(
            f'/treasury/daos/{dao.dao_id}/update-percentages',
            headers={'Authorization': f'Bearer {victor_logged_in}'}
        )
        
        # Assert first response
        assert response1.status_code == 200
        
        # Second request - should be served from cache
        response2 = client.put(
            f'/treasury/daos/{dao.dao_id}/update-percentages',
            headers={'Authorization': f'Bearer {victor_logged_in}'}
        )
        
        # Assert second response
        assert response2.status_code == 200
        
        # Responses should be identical
        assert response1.data == response2.data
        
        # Check that the success log message appears only once
        success_log_calls = sum(
            1 for call in mock_logger.info.call_args_list 
            if "Successfully updated token percentages" in str(call)
        )
        assert success_log_calls <= 1, "Database was accessed more than once"
