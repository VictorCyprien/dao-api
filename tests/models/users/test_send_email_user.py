import pytest
from unittest.mock import patch, MagicMock

from api.models.user import User


def test_send_email_to_user(sayori: User):
    with patch('api.models.user.send_email') as mock_send_email:
        # Call function
        sayori.send_email_to_user()

        # Verify email was sent with correct parameters
        mock_send_email.assert_called_once_with(sayori.email, "Welcome to DAO.io", "Welcome to DAO.io")


def test_send_email_to_user_error(sayori: User):
    # Create test user

    with patch('api.models.user.send_email') as mock_send_email:
        # Configure mock to raise error
        mock_send_email.side_effect = Exception("SMTP Error")

        # Call function and verify it handles error
        with pytest.raises(Exception) as exc:
            sayori.send_email_to_user()
        assert str(exc.value) == "SMTP Error"
