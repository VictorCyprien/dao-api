from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from api.config import config

from helpers.logging_file import Logger


logger = Logger()


def send_email(recipient_email: str, subject: str, body: str) -> bool:
    """Send an email using SMTP
    
    Args:
        recipient_email: Email address of the recipient
        subject: Subject line of the email
        body: Body text of the email
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Email configuration
    sender_email = "noreply@dao.io"
    smtp_server = config.SMTP_SERVER
    smtp_port = config.SMTP_PORT
    smtp_username = config.SMTP_USERNAME
    smtp_password = config.SMTP_PASSWORD

    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Add body
    message.attach(MIMEText(body, "plain"))

    # Create SMTP session
    with SMTP(smtp_server, smtp_port) as server:
        if smtp_server != "localhost":
            server.starttls()
            server.login(smtp_username, smtp_password)
        server.send_message(message)

