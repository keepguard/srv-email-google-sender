"""Prometheus Metrics Implementation."""

from prometheus_client import Counter, Gauge, Histogram, Info
from typing import Dict, Any

# Application info
app_info = Info('srv_email_google_sender_app', 'Email Google Sender Service application info')

# Email metrics
email_sent_total = Counter(
    'srv_email_sent_total',
    'Total number of emails sent',
    ['status']  # status: success, failure, retry
)

email_send_duration = Histogram(
    'srv_email_send_duration_seconds',
    'Time taken to send email',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Gmail API metrics
gmail_api_calls_total = Counter(
    'srv_gmail_api_calls_total',
    'Total number of Gmail API calls',
    ['method', 'status']  # method: send, status: success, error
)

gmail_api_duration = Histogram(
    'srv_gmail_api_duration_seconds',
    'Gmail API call duration',
    ['method'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0]
)

# Token refresh metrics
token_refresh_total = Counter(
    'srv_token_refresh_total',
    'Total number of token refresh attempts',
    ['email', 'status', 'source']  # source: local, token_manager
)

token_refresh_duration = Histogram(
    'srv_token_refresh_duration_seconds',
    'Time taken to refresh token',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# RabbitMQ metrics
rabbitmq_messages_consumed_total = Counter(
    'srv_rabbitmq_messages_consumed_total',
    'Total number of RabbitMQ messages consumed',
    ['queue', 'status']  # status: success, failure, requeue
)

rabbitmq_message_processing_duration = Histogram(
    'srv_rabbitmq_message_processing_duration_seconds',
    'Time taken to process RabbitMQ message',
    ['queue'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

rabbitmq_connection_status = Gauge(
    'srv_rabbitmq_connection_status',
    'RabbitMQ connection status (0=disconnected, 1=connected)'
)

# Cache metrics
cache_hits_total = Counter(
    'srv_cache_hits_total',
    'Total cache hits',
    ['cache_type']  # redis, local
)

cache_misses_total = Counter(
    'srv_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# API metrics
http_requests_total = Counter(
    'srv_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration = Histogram(
    'srv_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

redis_operation_duration = Histogram(
    'srv_redis_operation_duration_seconds',
    'Time taken for Redis operations',
    ['operation'],  # get, set, delete
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
)


def update_app_info(version: str, environment: str, python_version: str) -> None:
    """Update application info metrics."""
    app_info.info({
        'version': version,
        'environment': environment,
        'python_version': python_version
    })


def increment_email_sent(status: str) -> None:
    """Increment email sent counter."""
    email_sent_total.labels(status=status).inc()


def increment_gmail_api_calls(method: str, status: str) -> None:
    """Increment Gmail API calls counter."""
    gmail_api_calls_total.labels(method=method, status=status).inc()


def increment_token_refresh(email: str, status: str, source: str = "local") -> None:
    """Increment token refresh counter."""
    token_refresh_total.labels(email=email, status=status, source=source).inc()


def increment_rabbitmq_messages(queue: str, status: str) -> None:
    """Increment RabbitMQ messages consumed counter."""
    rabbitmq_messages_consumed_total.labels(queue=queue, status=status).inc()


def update_rabbitmq_connection_status(connected: bool) -> None:
    """Update RabbitMQ connection status."""
    rabbitmq_connection_status.set(1 if connected else 0)


def increment_cache_hits(cache_type: str) -> None:
    """Increment cache hits counter."""
    cache_hits_total.labels(cache_type=cache_type).inc()


def increment_cache_misses(cache_type: str) -> None:
    """Increment cache misses counter."""
    cache_misses_total.labels(cache_type=cache_type).inc()


def increment_http_requests(method: str, endpoint: str, status_code: int) -> None:
    """Increment HTTP requests counter."""
    http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

