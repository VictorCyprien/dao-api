import pytest
from unittest.mock import patch, MagicMock

from helpers.smtp_file import send_email


def test_send_email_localhost_success():
    with patch('helpers.smtp_file.SMTP') as mock_smtp:
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Call function
        result = send_email(
            recipient_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )

        # Verify SMTP interactions
        mock_smtp.assert_called_once()
        mock_server.send_message.assert_called_once()



def test_send_email_remote_server_success():
    with patch('helpers.smtp_file.SMTP') as mock_smtp:

        from api.config import config

        config.SMTP_SERVER = "smtp.gmail.com"
        config.SMTP_USERNAME = "user"
        config.SMTP_PASSWORD = "pass"
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Call function
        result = send_email(
            recipient_email="test@example.com",
            subject="Test Subject", 
            body="Test Body"
        )

        # Verify TLS and login used for remote server
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.send_message.assert_called_once()


def test_send_email_smtp_error():
    with patch('helpers.smtp_file.SMTP') as mock_smtp:
        # Configure mock to raise error
        mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")

        # Call function and verify it handles error
        with pytest.raises(Exception) as exc:
            send_email(
                recipient_email="test@example.com",
                subject="Test Subject",
                body="Test Body" 
            )
        assert str(exc.value) == "SMTP Error"
