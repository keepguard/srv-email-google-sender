
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
import uvicorn
import sys
import time

from app.config.loader import load_settings
from app.api.v1.health_router import router as health_router, set_rabbitmq_lifecycle
from app.api.v1.mail_router import build_mail_router
from app.application.usecases.send_email_usecase import SendEmailUseCase
from app.infrastructure.gmail.gmail_email_sender import GmailEmailSender
from app.infrastructure.messaging.lifecycle import RabbitMQLifecycleManager
from app.infrastructure.monitoring import logger as monitoring_logger
from app.infrastructure.monitoring import metrics
from prometheus_client import make_asgi_app

settings = load_settings()

# Configure structured logging
monitoring_logger.configure_logging(
    level=getattr(settings, 'log_level', 'info'),
    format_type=getattr(settings, 'log_format', 'json')
)
logger = monitoring_logger.get_logger(__name__)

# Update app info metrics
metrics.update_app_info(
    version=settings.app_version,
    environment=getattr(settings, 'env', 'local'),
    python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
)

# Variáveis globais
rabbitmq_lifecycle: RabbitMQLifecycleManager = None
usecase = None


def create_usecase():
    """Cria o usecase globalmente"""
    global usecase
    if settings.gmail.auth_mode == "service-account":
        from app.infrastructure.gmail.service_account_sender import ServiceAccountEmailSender
        sender = ServiceAccountEmailSender(
            sender_email=settings.gmail.sender_email,
            service_account_file=settings.gmail.client_secrets_file,
            delegated_user=settings.gmail.sender_email
        )
    else:
        # Check if TokenManager is enabled
        token_manager_url = None
        if hasattr(settings.gmail, 'token_manager') and settings.gmail.token_manager.enabled:
            token_manager_url = settings.gmail.token_manager.base_url
        
        sender = GmailEmailSender(
            sender_email=settings.gmail.sender_email,
            client_secrets_file=settings.gmail.client_secrets_file,
            token_file=settings.gmail.token_file,
            scopes=settings.gmail.scopes,
            auth_mode=settings.gmail.auth_mode,
            token_manager_url=token_manager_url
        )
    usecase = SendEmailUseCase(sender)
    return usecase


# Middleware para métricas HTTP
async def metrics_middleware(request: Request, call_next):
    """Middleware para coletar métricas HTTP."""
    start_time = time.time()
    
    # Get correlation_id
    correlation_id = request.headers.get("X-Correlation-ID", "")
    
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Record metrics
    metrics.increment_http_requests(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    )
    
    # Log API request
    monitoring_logger.log_api_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        correlation_id=correlation_id
    )
    
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rabbitmq_lifecycle, usecase
    try:
        logger.info("Iniciando RabbitMQ Consumer...")
        rabbitmq_lifecycle = RabbitMQLifecycleManager(settings.rabbitmq, usecase)
        await rabbitmq_lifecycle.start()
        # Definir o lifecycle no health router
        set_rabbitmq_lifecycle(rabbitmq_lifecycle)
        logger.info("RabbitMQ Consumer iniciado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao iniciar RabbitMQ Consumer: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        if rabbitmq_lifecycle:
            logger.info("Parando RabbitMQ Consumer...")
            await rabbitmq_lifecycle.stop()
            logger.info("RabbitMQ Consumer parado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao parar RabbitMQ Consumer: {e}")


def create_app() -> FastAPI:
    # Criar o usecase globalmente
    create_usecase()
    
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

    app.include_router(health_router, tags=["health"])
    app.include_router(build_mail_router(usecase), tags=["mail"])

    return app

app = create_app()

if __name__ == "__main__":
    logger.info(
        "starting_server",
        host=settings.server.host,
        port=settings.server.port,
        version=settings.app_version
    )
    
    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True
    )
