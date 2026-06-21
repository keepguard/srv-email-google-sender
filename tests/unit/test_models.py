"""
Testes unitários para os modelos de domínio.
"""
import pytest
from pydantic import ValidationError
from app.domain.models import EmailPayload


class TestEmailPayload:
    """Testes para o modelo EmailPayload."""

    def test_email_payload_creation_with_valid_data(self):
        """Testa criação de EmailPayload com dados válidos."""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "message": "Test content",
            "html": "<p>Test HTML content</p>",
            "cc": None,
            "replyTo": None
        }
        
        email = EmailPayload(**email_data)
        
        assert email.to == "test@example.com"
        assert email.subject == "Test Subject"
        assert email.message == "Test content"
        assert email.html == "<p>Test HTML content</p>"
        assert email.cc is None
        assert email.replyTo is None

    def test_email_payload_creation_with_minimal_data(self):
        """Testa criação de EmailPayload com dados mínimos."""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject"
        }
        
        email = EmailPayload(**email_data)
        
        assert email.to == "test@example.com"
        assert email.subject == "Test Subject"
        assert email.message is None
        assert email.html is None
        assert email.cc is None
        assert email.replyTo is None

    def test_email_payload_creation_with_invalid_email(self):
        """Testa criação de EmailPayload com email inválido."""
        email_data = {
            "to": "invalid-email",
            "subject": "Test Subject"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailPayload(**email_data)
        
        assert "to" in str(exc_info.value)

    def test_email_payload_creation_with_missing_required_fields(self):
        """Testa criação de EmailPayload com campos obrigatórios ausentes."""
        email_data = {
            "subject": "Test Subject"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailPayload(**email_data)
        
        assert "to" in str(exc_info.value)

    def test_email_payload_creation_with_empty_subject(self):
        """Testa criação de EmailPayload com assunto vazio."""
        email_data = {
            "to": "test@example.com",
            "subject": ""
        }
        
        with pytest.raises(ValidationError) as exc_info:
            EmailPayload(**email_data)
        
        assert "subject" in str(exc_info.value)

    def test_email_payload_with_cc_and_reply_to(self):
        """Testa EmailPayload com CC e Reply-To."""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "cc": "cc@example.com",
            "replyTo": "reply@example.com"
        }
        
        email = EmailPayload(**email_data)
        
        assert email.cc == "cc@example.com"
        assert email.replyTo == "reply@example.com"

    def test_email_payload_serialization(self):
        """Testa serialização de EmailPayload."""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "message": "Test content"
        }
        
        email = EmailPayload(**email_data)
        serialized = email.dict()
        
        assert serialized["to"] == "test@example.com"
        assert serialized["subject"] == "Test Subject"
        assert serialized["message"] == "Test content"

    def test_email_payload_json_serialization(self):
        """Testa serialização JSON de EmailPayload."""
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "message": "Test content"
        }
        
        email = EmailPayload(**email_data)
        json_str = email.json()
        
        assert "test@example.com" in json_str
        assert "Test Subject" in json_str
        assert "Test content" in json_str