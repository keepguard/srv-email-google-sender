"""
Fixtures compartilhadas para testes do srv-email-google-sender.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any
import asyncio
from aio_pika import Connection, Channel, Exchange, Queue
from google.oauth2.service_account import Credentials

from app.config.loader import Settings
from app.domain.models import EmailPayload


@pytest.fixture
def mock_settings() -> Settings:
    """Mock das configurações da aplicação."""
    return Settings(
        app_name="email-google-sender",
        version="1.0.0",
        environment="test",
        debug=True,
        rabbitmq={
            "host": "localhost",
            "port": 5672,
            "user": "guest",
            "password": "guest",
            "vhost": "/",
            "queues": {
                "email_send": "email.google.sender.message.send.test",
                "email_send_dlt": "email.google.sender.message.send.dlt.test"
            },
            "exchanges": {
                "email_exchange": "email-google-sender-exchange",
                "email_exchange_dlt": "email-google-sender-exchange-dlt"
            },
            "routing_keys": {
                "email_send": "email.google.send",
                "email_failed": "email.failed"
            },
            "retry": {
                "max_attempts": 3,
                "initial_delay_seconds": 5
            }
        },
        gmail={
            "service_account_file": "test-service-account.json",
            "scopes": ["https://www.googleapis.com/auth/gmail.send"],
            "subject_prefix": "[TEST]"
        }
    )


@pytest.fixture
def mock_gmail_credentials() -> Mock:
    """Mock das credenciais do Gmail."""
    credentials = Mock(spec=Credentials)
    credentials.valid = True
    credentials.expired = False
    return credentials


@pytest.fixture
def mock_gmail_service() -> Mock:
    """Mock do serviço Gmail."""
    service = Mock()
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
        "id": "test-message-id",
        "threadId": "test-thread-id",
        "labelIds": ["SENT"]
    }
    return service


@pytest.fixture
def mock_rabbitmq_connection() -> Mock:
    """Mock da conexão RabbitMQ."""
    connection = AsyncMock(spec=Connection)
    return connection


@pytest.fixture
def mock_rabbitmq_channel() -> Mock:
    """Mock do canal RabbitMQ."""
    channel = AsyncMock(spec=Channel)
    return channel


@pytest.fixture
def mock_rabbitmq_exchange() -> Mock:
    """Mock do exchange RabbitMQ."""
    exchange = AsyncMock(spec=Exchange)
    return exchange


@pytest.fixture
def mock_rabbitmq_queue() -> Mock:
    """Mock da queue RabbitMQ."""
    queue = AsyncMock(spec=Queue)
    return queue


@pytest.fixture
def sample_email_message() -> EmailPayload:
    """Mensagem de email de exemplo para testes."""
    return EmailPayload(
        to="test@example.com",
        subject="Test Subject",
        message="Test content",
        html="<p>Test HTML content</p>",
        cc=None,
        replyTo=None
    )


@pytest.fixture
def sample_email_message_data() -> Dict[str, Any]:
    """Dados de mensagem de email em formato de dicionário."""
    return {
        "to": "test@example.com",
        "subject": "Test Subject",
        "message": "Test content",
        "html": "<p>Test HTML content</p>",
        "cc": None,
        "replyTo": None
    }


@pytest.fixture
def mock_rabbitmq_message():
    """Mock de mensagem RabbitMQ."""
    message = Mock()
    message.body = b'{"to": "test@example.com", "subject": "Test", "message": "Test content"}'
    message.delivery_tag = 1
    message.exchange = "test-exchange"
    message.routing_key = "test.routing.key"
    return message


@pytest.fixture
def mock_logger():
    """Mock do logger."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def mock_http_client():
    """Mock do cliente HTTP."""
    client = AsyncMock()
    client.post = AsyncMock()
    client.get = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def event_loop():
    """Event loop para testes assíncronos."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()