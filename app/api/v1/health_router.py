
from fastapi import APIRouter
from typing import Optional
from app.infrastructure.messaging.lifecycle import RabbitMQLifecycleManager

router = APIRouter()

# Variável global para o lifecycle manager (será definida pelo main.py)
rabbitmq_lifecycle: Optional[RabbitMQLifecycleManager] = None

def set_rabbitmq_lifecycle(lifecycle: RabbitMQLifecycleManager):
    """Define o lifecycle manager (chamado pelo main.py)"""
    global rabbitmq_lifecycle
    rabbitmq_lifecycle = lifecycle

@router.get("/health")
def health():
    return {"status": "UP"}

@router.get("/health/rabbitmq")
async def health_rabbitmq():
    """Health check específico para RabbitMQ Consumer"""
    if not rabbitmq_lifecycle:
        return {"status": "DOWN", "message": "RabbitMQ Consumer não inicializado"}
    
    is_healthy = await rabbitmq_lifecycle.health_check()
    
    if is_healthy:
        return {"status": "UP", "message": "RabbitMQ Consumer funcionando"}
    else:
        return {"status": "DOWN", "message": "RabbitMQ Consumer com problemas"}
