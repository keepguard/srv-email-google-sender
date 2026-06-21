"""
Testes unitários para as exceções de domínio.
"""
import pytest
from app.domain.errors import (
    EmailSendingError,
    EmailValidationError,
    GmailAuthenticationError,
    RabbitMQConnectionError,
    RabbitMQMessageProcessingError,
    ConfigurationError,
    TemplateNotFoundError,
    TemplateValidationError
)


class TestEmailSendingError:
    """Testes para EmailSendingError."""

    def test_email_sending_error_creation_with_message(self):
        """Testa criação de EmailSendingError com mensagem."""
        error = EmailSendingError("Failed to send email")
        
        assert str(error) == "Failed to send email"
        assert error.message == "Failed to send email"

    def test_email_sending_error_creation_with_message_and_details(self):
        """Testa criação de EmailSendingError com mensagem e detalhes."""
        error = EmailSendingError("Failed to send email", details={"recipient": "test@example.com"})
        
        assert str(error) == "Failed to send email"
        assert error.message == "Failed to send email"
        assert error.details == {"recipient": "test@example.com"}

    def test_email_sending_error_creation_with_message_and_cause(self):
        """Testa criação de EmailSendingError com mensagem e causa."""
        cause = Exception("Original error")
        error = EmailSendingError("Failed to send email", cause=cause)
        
        assert str(error) == "Failed to send email"
        assert error.message == "Failed to send email"
        assert error.cause == cause

    def test_email_sending_error_creation_with_all_parameters(self):
        """Testa criação de EmailSendingError com todos os parâmetros."""
        cause = Exception("Original error")
        error = EmailSendingError(
            "Failed to send email",
            details={"recipient": "test@example.com"},
            cause=cause
        )
        
        assert str(error) == "Failed to send email"
        assert error.message == "Failed to send email"
        assert error.details == {"recipient": "test@example.com"}
        assert error.cause == cause

    def test_email_sending_error_inheritance(self):
        """Testa herança de EmailSendingError."""
        error = EmailSendingError("Failed to send email")
        
        assert isinstance(error, Exception)
        assert isinstance(error, EmailSendingError)

    def test_email_sending_error_with_empty_message(self):
        """Testa EmailSendingError com mensagem vazia."""
        error = EmailSendingError("")
        
        assert str(error) == ""
        assert error.message == ""

    def test_email_sending_error_with_none_details(self):
        """Testa EmailSendingError com detalhes None."""
        error = EmailSendingError("Failed to send email", details=None)
        
        assert str(error) == "Failed to send email"
        assert error.details is None

    def test_email_sending_error_with_none_cause(self):
        """Testa EmailSendingError com causa None."""
        error = EmailSendingError("Failed to send email", cause=None)
        
        assert str(error) == "Failed to send email"
        assert error.cause is None


class TestEmailValidationError:
    """Testes para EmailValidationError."""

    def test_email_validation_error_creation_with_message(self):
        """Testa criação de EmailValidationError com mensagem."""
        error = EmailValidationError("Invalid email format")
        
        assert str(error) == "Invalid email format"
        assert error.message == "Invalid email format"

    def test_email_validation_error_creation_with_message_and_field(self):
        """Testa criação de EmailValidationError com mensagem e campo."""
        error = EmailValidationError("Invalid email format", field="to")
        
        assert str(error) == "Invalid email format"
        assert error.message == "Invalid email format"
        assert error.field == "to"

    def test_email_validation_error_creation_with_message_and_value(self):
        """Testa criação de EmailValidationError com mensagem e valor."""
        error = EmailValidationError("Invalid email format", value="invalid-email")
        
        assert str(error) == "Invalid email format"
        assert error.message == "Invalid email format"
        assert error.value == "invalid-email"

    def test_email_validation_error_creation_with_all_parameters(self):
        """Testa criação de EmailValidationError com todos os parâmetros."""
        error = EmailValidationError(
            "Invalid email format",
            field="to",
            value="invalid-email"
        )
        
        assert str(error) == "Invalid email format"
        assert error.message == "Invalid email format"
        assert error.field == "to"
        assert error.value == "invalid-email"

    def test_email_validation_error_inheritance(self):
        """Testa herança de EmailValidationError."""
        error = EmailValidationError("Invalid email format")
        
        assert isinstance(error, Exception)
        assert isinstance(error, EmailValidationError)

    def test_email_validation_error_with_empty_field(self):
        """Testa EmailValidationError com campo vazio."""
        error = EmailValidationError("Invalid email format", field="")
        
        assert str(error) == "Invalid email format"
        assert error.field == ""

    def test_email_validation_error_with_none_field(self):
        """Testa EmailValidationError com campo None."""
        error = EmailValidationError("Invalid email format", field=None)
        
        assert str(error) == "Invalid email format"
        assert error.field is None


class TestGmailAuthenticationError:
    """Testes para GmailAuthenticationError."""

    def test_gmail_authentication_error_creation_with_message(self):
        """Testa criação de GmailAuthenticationError com mensagem."""
        error = GmailAuthenticationError("Failed to authenticate with Gmail")
        
        assert str(error) == "Failed to authenticate with Gmail"
        assert error.message == "Failed to authenticate with Gmail"

    def test_gmail_authentication_error_creation_with_message_and_details(self):
        """Testa criação de GmailAuthenticationError com mensagem e detalhes."""
        error = GmailAuthenticationError(
            "Failed to authenticate with Gmail",
            details={"service_account_file": "missing.json"}
        )
        
        assert str(error) == "Failed to authenticate with Gmail"
        assert error.message == "Failed to authenticate with Gmail"
        assert error.details == {"service_account_file": "missing.json"}

    def test_gmail_authentication_error_inheritance(self):
        """Testa herança de GmailAuthenticationError."""
        error = GmailAuthenticationError("Failed to authenticate with Gmail")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GmailAuthenticationError)


class TestRabbitMQConnectionError:
    """Testes para RabbitMQConnectionError."""

    def test_rabbitmq_connection_error_creation_with_message(self):
        """Testa criação de RabbitMQConnectionError com mensagem."""
        error = RabbitMQConnectionError("Failed to connect to RabbitMQ")
        
        assert str(error) == "Failed to connect to RabbitMQ"
        assert error.message == "Failed to connect to RabbitMQ"

    def test_rabbitmq_connection_error_creation_with_message_and_details(self):
        """Testa criação de RabbitMQConnectionError com mensagem e detalhes."""
        error = RabbitMQConnectionError(
            "Failed to connect to RabbitMQ",
            details={"host": "localhost", "port": 5672}
        )
        
        assert str(error) == "Failed to connect to RabbitMQ"
        assert error.message == "Failed to connect to RabbitMQ"
        assert error.details == {"host": "localhost", "port": 5672}

    def test_rabbitmq_connection_error_inheritance(self):
        """Testa herança de RabbitMQConnectionError."""
        error = RabbitMQConnectionError("Failed to connect to RabbitMQ")
        
        assert isinstance(error, Exception)
        assert isinstance(error, RabbitMQConnectionError)


class TestRabbitMQMessageProcessingError:
    """Testes para RabbitMQMessageProcessingError."""

    def test_rabbitmq_message_processing_error_creation_with_message(self):
        """Testa criação de RabbitMQMessageProcessingError com mensagem."""
        error = RabbitMQMessageProcessingError("Failed to process message")
        
        assert str(error) == "Failed to process message"
        assert error.message == "Failed to process message"

    def test_rabbitmq_message_processing_error_creation_with_message_and_details(self):
        """Testa criação de RabbitMQMessageProcessingError com mensagem e detalhes."""
        error = RabbitMQMessageProcessingError(
            "Failed to process message",
            details={"message_id": "123", "queue": "email.queue"}
        )
        
        assert str(error) == "Failed to process message"
        assert error.message == "Failed to process message"
        assert error.details == {"message_id": "123", "queue": "email.queue"}

    def test_rabbitmq_message_processing_error_inheritance(self):
        """Testa herança de RabbitMQMessageProcessingError."""
        error = RabbitMQMessageProcessingError("Failed to process message")
        
        assert isinstance(error, Exception)
        assert isinstance(error, RabbitMQMessageProcessingError)


class TestConfigurationError:
    """Testes para ConfigurationError."""

    def test_configuration_error_creation_with_message(self):
        """Testa criação de ConfigurationError com mensagem."""
        error = ConfigurationError("Invalid configuration")
        
        assert str(error) == "Invalid configuration"
        assert error.message == "Invalid configuration"

    def test_configuration_error_creation_with_message_and_details(self):
        """Testa criação de ConfigurationError com mensagem e detalhes."""
        error = ConfigurationError(
            "Invalid configuration",
            details={"missing_key": "gmail.service_account_file"}
        )
        
        assert str(error) == "Invalid configuration"
        assert error.message == "Invalid configuration"
        assert error.details == {"missing_key": "gmail.service_account_file"}

    def test_configuration_error_inheritance(self):
        """Testa herança de ConfigurationError."""
        error = ConfigurationError("Invalid configuration")
        
        assert isinstance(error, Exception)
        assert isinstance(error, ConfigurationError)


class TestTemplateNotFoundError:
    """Testes para TemplateNotFoundError."""

    def test_template_not_found_error_creation_with_message(self):
        """Testa criação de TemplateNotFoundError com mensagem."""
        error = TemplateNotFoundError("Template not found")
        
        assert str(error) == "Template not found"
        assert error.message == "Template not found"

    def test_template_not_found_error_creation_with_message_and_template_name(self):
        """Testa criação de TemplateNotFoundError com mensagem e nome do template."""
        error = TemplateNotFoundError("Template not found", template_name="welcome_template")
        
        assert str(error) == "Template not found"
        assert error.message == "Template not found"
        assert error.template_name == "welcome_template"

    def test_template_not_found_error_inheritance(self):
        """Testa herança de TemplateNotFoundError."""
        error = TemplateNotFoundError("Template not found")
        
        assert isinstance(error, Exception)
        assert isinstance(error, TemplateNotFoundError)


class TestTemplateValidationError:
    """Testes para TemplateValidationError."""

    def test_template_validation_error_creation_with_message(self):
        """Testa criação de TemplateValidationError com mensagem."""
        error = TemplateValidationError("Invalid template")
        
        assert str(error) == "Invalid template"
        assert error.message == "Invalid template"

    def test_template_validation_error_creation_with_message_and_template_name(self):
        """Testa criação de TemplateValidationError com mensagem e nome do template."""
        error = TemplateValidationError("Invalid template", template_name="welcome_template")
        
        assert str(error) == "Invalid template"
        assert error.message == "Invalid template"
        assert error.template_name == "welcome_template"

    def test_template_validation_error_creation_with_message_and_field(self):
        """Testa criação de TemplateValidationError com mensagem e campo."""
        error = TemplateValidationError("Invalid template", field="subject")
        
        assert str(error) == "Invalid template"
        assert error.message == "Invalid template"
        assert error.field == "subject"

    def test_template_validation_error_creation_with_all_parameters(self):
        """Testa criação de TemplateValidationError com todos os parâmetros."""
        error = TemplateValidationError(
            "Invalid template",
            template_name="welcome_template",
            field="subject"
        )
        
        assert str(error) == "Invalid template"
        assert error.message == "Invalid template"
        assert error.template_name == "welcome_template"
        assert error.field == "subject"

    def test_template_validation_error_inheritance(self):
        """Testa herança de TemplateValidationError."""
        error = TemplateValidationError("Invalid template")
        
        assert isinstance(error, Exception)
        assert isinstance(error, TemplateValidationError)


class TestErrorChaining:
    """Testes para encadeamento de exceções."""

    def test_error_chaining_with_cause(self):
        """Testa encadeamento de exceções com causa."""
        original_error = ValueError("Original error")
        wrapped_error = EmailSendingError("Failed to send email", cause=original_error)
        
        assert wrapped_error.cause == original_error
        assert str(wrapped_error) == "Failed to send email"

    def test_error_chaining_with_details(self):
        """Testa encadeamento de exceções com detalhes."""
        error = EmailSendingError(
            "Failed to send email",
            details={"recipient": "test@example.com", "error_code": "SMTP_ERROR"}
        )
        
        assert error.details["recipient"] == "test@example.com"
        assert error.details["error_code"] == "SMTP_ERROR"

    def test_error_chaining_with_both_cause_and_details(self):
        """Testa encadeamento de exceções com causa e detalhes."""
        original_error = ConnectionError("Connection failed")
        error = RabbitMQConnectionError(
            "Failed to connect to RabbitMQ",
            details={"host": "localhost", "port": 5672},
            cause=original_error
        )
        
        assert error.cause == original_error
        assert error.details["host"] == "localhost"
        assert error.details["port"] == 5672

    def test_error_inheritance_hierarchy(self):
        """Testa hierarquia de herança das exceções."""
        # Todas as exceções devem herdar de Exception
        errors = [
            EmailSendingError("test"),
            EmailValidationError("test"),
            GmailAuthenticationError("test"),
            RabbitMQConnectionError("test"),
            RabbitMQMessageProcessingError("test"),
            ConfigurationError("test"),
            TemplateNotFoundError("test"),
            TemplateValidationError("test")
        ]
        
        for error in errors:
            assert isinstance(error, Exception)
            assert hasattr(error, 'message')
            assert str(error) == "test"
