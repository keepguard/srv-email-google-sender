"""
Testes unitários para o Gmail Email Sender.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.infrastructure.gmail.gmail_email_sender import GmailEmailSender
from app.domain.errors import GmailAuthenticationError, EmailSendingError
from app.domain.models import EmailMessage


class TestGmailEmailSender:
    """Testes para GmailEmailSender."""

    def test_gmail_email_sender_initialization(self, mock_settings, mock_gmail_service):
        """Testa inicialização do GmailEmailSender."""
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        assert sender.settings == mock_settings
        assert sender.service == mock_gmail_service

    def test_gmail_email_sender_initialization_with_none_service(self, mock_settings):
        """Testa inicialização do GmailEmailSender com serviço None."""
        sender = GmailEmailSender(mock_settings, None)
        
        assert sender.settings == mock_settings
        assert sender.service is None

    @patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode')
    @patch('app.infrastructure.gmail.gmail_email_sender.MIMEText')
    def test_create_message_with_text_content(self, mock_mimetext, mock_b64encode, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com conteúdo de texto."""
        # Setup mocks
        mock_message = Mock()
        mock_mimetext.return_value = mock_message
        mock_message.as_string.return_value = "email content"
        mock_b64encode.return_value = b"encoded_content"
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "content": "Test content"
        }
        email = EmailMessage(**email_data)
        
        result = sender.create_message(email)
        
        assert result == {"raw": "encoded_content"}
        mock_mimetext.assert_called_once_with("Test content", "plain", "utf-8")

    @patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode')
    @patch('app.infrastructure.gmail.gmail_email_sender.MIMEText')
    def test_create_message_with_html_content(self, mock_mimetext, mock_b64encode, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com conteúdo HTML."""
        # Setup mocks
        mock_message = Mock()
        mock_mimetext.return_value = mock_message
        mock_message.as_string.return_value = "html email content"
        mock_b64encode.return_value = b"encoded_html_content"
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "content": "Test content",
            "html_content": "<p>Test HTML content</p>"
        }
        email = EmailMessage(**email_data)
        
        result = sender.create_message(email)
        
        assert result == {"raw": "encoded_html_content"}
        mock_mimetext.assert_called_once_with("<p>Test HTML content</p>", "html", "utf-8")

    @patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode')
    @patch('app.infrastructure.gmail.gmail_email_sender.MIMEMultipart')
    def test_create_message_with_both_text_and_html(self, mock_mimemultipart, mock_b64encode, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com texto e HTML."""
        # Setup mocks
        mock_message = Mock()
        mock_mimemultipart.return_value = mock_message
        mock_message.as_string.return_value = "multipart email content"
        mock_b64encode.return_value = b"encoded_multipart_content"
        
        # Mock MIMEText for attachments
        with patch('app.infrastructure.gmail.gmail_email_sender.MIMEText') as mock_mimetext:
            mock_text_part = Mock()
            mock_html_part = Mock()
            mock_mimetext.side_effect = [mock_text_part, mock_html_part]
            
            sender = GmailEmailSender(mock_settings, mock_gmail_service)
            
            email_data = {
                "to": "test@example.com",
                "subject": "Test Subject",
                "content": "Test content",
                "html_content": "<p>Test HTML content</p>"
            }
            email = EmailMessage(**email_data)
            
            result = sender.create_message(email)
            
            assert result == {"raw": "encoded_multipart_content"}
            assert mock_message.attach.call_count == 2

    def test_create_message_with_subject_prefix(self, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com prefixo no assunto."""
        # Setup mock settings with subject prefix
        mock_settings.gmail["subject_prefix"] = "[TEST]"
        
        with patch('app.infrastructure.gmail.gmail_email_sender.MIMEText') as mock_mimetext, \
             patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode') as mock_b64encode:
            
            mock_message = Mock()
            mock_mimetext.return_value = mock_message
            mock_message.as_string.return_value = "email content"
            mock_b64encode.return_value = b"encoded_content"
            
            sender = GmailEmailSender(mock_settings, mock_gmail_service)
            
            email_data = {
                "to": "test@example.com",
                "subject": "Test Subject",
                "content": "Test content"
            }
            email = EmailMessage(**email_data)
            
            result = sender.create_message(email)
            
            # Verifica se o prefixo foi adicionado ao assunto
            assert mock_message["Subject"] == "[TEST] Test Subject"

    def test_create_message_without_subject_prefix(self, mock_settings, mock_gmail_service):
        """Testa criação de mensagem sem prefixo no assunto."""
        # Setup mock settings without subject prefix
        mock_settings.gmail["subject_prefix"] = ""
        
        with patch('app.infrastructure.gmail.gmail_email_sender.MIMEText') as mock_mimetext, \
             patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode') as mock_b64encode:
            
            mock_message = Mock()
            mock_mimetext.return_value = mock_message
            mock_message.as_string.return_value = "email content"
            mock_b64encode.return_value = b"encoded_content"
            
            sender = GmailEmailSender(mock_settings, mock_gmail_service)
            
            email_data = {
                "to": "test@example.com",
                "subject": "Test Subject",
                "content": "Test content"
            }
            email = EmailMessage(**email_data)
            
            result = sender.create_message(email)
            
            # Verifica se o assunto não tem prefixo
            assert mock_message["Subject"] == "Test Subject"

    def test_create_message_with_variables(self, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com variáveis."""
        with patch('app.infrastructure.gmail.gmail_email_sender.MIMEText') as mock_mimetext, \
             patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode') as mock_b64encode:
            
            mock_message = Mock()
            mock_mimetext.return_value = mock_message
            mock_message.as_string.return_value = "email content with variables"
            mock_b64encode.return_value = b"encoded_content_with_variables"
            
            sender = GmailEmailSender(mock_settings, mock_gmail_service)
            
            email_data = {
                "to": "test@example.com",
                "subject": "Welcome {{userName}}!",
                "content": "Hello {{userName}}, welcome to {{appName}}!",
                "variables": {"userName": "John", "appName": "TestApp"}
            }
            email = EmailMessage(**email_data)
            
            result = sender.create_message(email)
            
            # Verifica se as variáveis foram substituídas
            assert mock_message["Subject"] == "Welcome John!"
            # O conteúdo também deve ter as variáveis substituídas
            mock_mimetext.assert_called_once_with("Hello John, welcome to TestApp!", "plain", "utf-8")

    def test_create_message_with_special_characters(self, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com caracteres especiais."""
        with patch('app.infrastructure.gmail.gmail_email_sender.MIMEText') as mock_mimetext, \
             patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode') as mock_b64encode:
            
            mock_message = Mock()
            mock_mimetext.return_value = mock_message
            mock_message.as_string.return_value = "email content with special chars"
            mock_b64encode.return_value = b"encoded_content_with_special_chars"
            
            sender = GmailEmailSender(mock_settings, mock_gmail_service)
            
            email_data = {
                "to": "test@example.com",
                "subject": "Test with émojis 🚀 and special chars: àáâãäå",
                "content": "Content with special chars: àáâãäå and émojis 🚀"
            }
            email = EmailMessage(**email_data)
            
            result = sender.create_message(email)
            
            # Verifica se os caracteres especiais foram mantidos
            assert "émojis" in mock_message["Subject"]
            assert "àáâãäå" in mock_message["Subject"]

    def test_send_email_success(self, mock_settings, mock_gmail_service):
        """Testa envio de email com sucesso."""
        # Setup mocks
        mock_gmail_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "id": "test-message-id",
            "threadId": "test-thread-id",
            "labelIds": ["SENT"]
        }
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "content": "Test content"
        }
        email = EmailMessage(**email_data)
        
        with patch.object(sender, 'create_message', return_value={"raw": "encoded_content"}):
            result = sender.send_email(email)
        
        assert result == "test-message-id"
        mock_gmail_service.users.return_value.messages.return_value.send.assert_called_once()

    def test_send_email_with_none_service(self, mock_settings):
        """Testa envio de email com serviço None."""
        sender = GmailEmailSender(mock_settings, None)
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "content": "Test content"
        }
        email = EmailMessage(**email_data)
        
        with pytest.raises(GmailAuthenticationError) as exc_info:
            sender.send_email(email)
        
        assert "Gmail service not initialized" in str(exc_info.value)

    def test_send_email_with_service_exception(self, mock_settings, mock_gmail_service):
        """Testa envio de email com exceção do serviço."""
        # Setup mock to raise exception
        mock_gmail_service.users.return_value.messages.return_value.send.return_value.execute.side_effect = Exception("Gmail API error")
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "content": "Test content"
        }
        email = EmailMessage(**email_data)
        
        with patch.object(sender, 'create_message', return_value={"raw": "encoded_content"}):
            with pytest.raises(EmailSendingError) as exc_info:
                sender.send_email(email)
        
        assert "Failed to send email" in str(exc_info.value)
        assert exc_info.value.cause is not None

    def test_send_email_with_invalid_response(self, mock_settings, mock_gmail_service):
        """Testa envio de email com resposta inválida."""
        # Setup mock to return invalid response
        mock_gmail_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "threadId": "test-thread-id",
            "labelIds": ["SENT"]
            # Missing "id" field
        }
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "content": "Test content"
        }
        email = EmailMessage(**email_data)
        
        with patch.object(sender, 'create_message', return_value={"raw": "encoded_content"}):
            with pytest.raises(EmailSendingError) as exc_info:
                sender.send_email(email)
        
        assert "Invalid response from Gmail API" in str(exc_info.value)

    def test_test_connection_success(self, mock_settings, mock_gmail_service):
        """Testa teste de conexão com sucesso."""
        # Setup mock for successful connection test
        mock_gmail_service.users.return_value.getProfile.return_value.execute.return_value = {
            "emailAddress": "test@example.com",
            "messagesTotal": 100,
            "threadsTotal": 50
        }
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        result = sender.test_connection()
        
        assert result is True
        mock_gmail_service.users.return_value.getProfile.assert_called_once()

    def test_test_connection_with_none_service(self, mock_settings):
        """Testa teste de conexão com serviço None."""
        sender = GmailEmailSender(mock_settings, None)
        
        result = sender.test_connection()
        
        assert result is False

    def test_test_connection_with_exception(self, mock_settings, mock_gmail_service):
        """Testa teste de conexão com exceção."""
        # Setup mock to raise exception
        mock_gmail_service.users.return_value.getProfile.return_value.execute.side_effect = Exception("Connection error")
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        result = sender.test_connection()
        
        assert result is False

    def test_test_connection_with_invalid_response(self, mock_settings, mock_gmail_service):
        """Testa teste de conexão com resposta inválida."""
        # Setup mock to return invalid response
        mock_gmail_service.users.return_value.getProfile.return_value.execute.return_value = {
            "emailAddress": "test@example.com"
            # Missing required fields
        }
        
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        result = sender.test_connection()
        
        assert result is False

    def test_create_message_with_encoding_error(self, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com erro de codificação."""
        with patch('app.infrastructure.gmail.gmail_email_sender.MIMEText') as mock_mimetext:
            mock_message = Mock()
            mock_message.as_string.side_effect = UnicodeEncodeError("utf-8", "test", 0, 1, "invalid character")
            mock_mimetext.return_value = mock_message
            
            sender = GmailEmailSender(mock_settings, mock_gmail_service)
            
            email_data = {
                "to": "test@example.com",
                " sujet": "Test Subject",
                "content": "Test content"
            }
            email = EmailMessage(**email_data)
            
            with pytest.raises(EmailSendingError) as exc_info:
                sender.create_message(email)
            
            assert "Failed to create email message" in str(exc_info.value)

    def test_send_email_with_create_message_error(self, mock_settings, mock_gmail_service):
        """Testa envio de email com erro na criação da mensagem."""
        sender = GmailEmailSender(mock_settings, mock_gmail_service)
        
        email_data = {
            "to": "test@example.com",
            "subject": "Test Subject",
            "content": "Test content"
        }
        email = EmailMessage(**email_data)
        
        with patch.object(sender, 'create_message', side_effect=EmailSendingError("Failed to create message")):
            with pytest.raises(EmailSendingError) as exc_info:
                sender.send_email(email)
        
        assert "Failed to create message" in str(exc_info.value)

    def test_gmail_email_sender_with_different_settings(self, mock_gmail_service):
        """Testa GmailEmailSender com configurações diferentes."""
        # Create custom settings
        custom_settings = Mock()
        custom_settings.gmail = {
            "service_account_file": "custom-service-account.json",
            "scopes": ["https://www.googleapis.com/auth/gmail.send"],
            "subject_prefix": "[CUSTOM]"
        }
        
        sender = GmailEmailSender(custom_settings, mock_gmail_service)
        
        assert sender.settings == custom_settings
        assert sender.settings.gmail["subject_prefix"] == "[CUSTOM]"

    def test_create_message_with_empty_variables(self, mock_settings, mock_gmail_service):
        """Testa criação de mensagem com variáveis vazias."""
        with patch('app.infrastructure.gmail.gmail_email_sender.MIMEText') as mock_mimetext, \
             patch('app.infrastructure.gmail.gmail_email_sender.base64.urlsafe_b64encode') as mock_b64encode:
            
            mock_message = Mock()
            mock_mimetext.return_value = mock_message
            mock_message.as_string.return_value = "email content"
            mock_b64encode.return_value = b"encoded_content"
            
            sender = GmailEmailSender(mock_settings, mock_gmail_service)
            
            email_data = {
                "to": "test@example.com",
                "subject": "Test Subject with {{undefinedVariable}}",
                "content": "Test content with {{undefinedVariable}}",
                "variables": {}  # Empty variables
            }
            email = EmailMessage(**email_data)
            
            result = sender.create_message(email)
            
            # Variables should remain unchanged when not provided
            assert mock_message["Subject"] == "Test Subject with {{undefinedVariable}}"
            mock_mimetext.assert_called_once_with("Test content with {{undefinedVariable}}", "plain", "utf-8")
