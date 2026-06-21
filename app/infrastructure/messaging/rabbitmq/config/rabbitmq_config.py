import asyncio
import logging
from typing import Optional
from aio_pika import connect, Connection, Channel, Exchange, Queue, Message
from aio_pika.abc import AbstractIncomingMessage
from app.config.loader import RabbitMQCfg

logger = logging.getLogger(__name__)


class RabbitMQConfig:
    """Configuração e setup do RabbitMQ"""
    
    def __init__(self, config: RabbitMQCfg):
        self.config = config
        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None
        self.exchange: Optional[Exchange] = None
        self.email_send_queue: Optional[Queue] = None
        self.email_send_dlt_queue: Optional[Queue] = None
    
    async def connect(self) -> None:
        """Estabelece conexão com RabbitMQ"""
        try:
            # URL de conexão
            url = f"amqp://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}{self.config.vhost}"
            
            self.connection = await connect(url)
            self.channel = await self.connection.channel()
            
            # Configurar QoS para processar uma mensagem por vez
            await self.channel.set_qos(prefetch_count=1)
            
            logger.info(f"Conectado ao RabbitMQ: {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"Erro ao conectar com RabbitMQ: {e}")
            raise
    
    async def setup_queues(self) -> None:
        """Configura exchanges, queues e bindings"""
        try:
            if not self.channel:
                raise RuntimeError("Canal não inicializado. Execute connect() primeiro.")
            
            # Exchange principal (usando configuração do YAML)
            exchange_name = self.config.exchanges.get("email_exchange", "srv-email-google-sender-exchange")
            self.exchange = await self.channel.declare_exchange(
                exchange_name,
                durable=True,
                type="topic"
            )
            
            # Dead Letter Exchange (usando configuração do YAML)
            dlt_exchange_name = self.config.exchanges.get("email_exchange_dlt", "srv-email-google-sender-exchange-dlt")
            dlt_exchange = await self.channel.declare_exchange(
                dlt_exchange_name,
                durable=True,
                type="direct"
            )
            
            # Queue principal com DLT
            self.email_send_queue = await self.channel.declare_queue(
                self.config.queues["email_send"],
                durable=True,
                arguments={
                    "x-dead-letter-exchange": dlt_exchange_name,
                    "x-dead-letter-routing-key": self.config.routing_keys["email_failed"],
                    "x-message-ttl": 300000,  # 5 minutos TTL
                }
            )
            
            # Queue DLT
            self.email_send_dlt_queue = await self.channel.declare_queue(
                self.config.queues["email_send_dlt"],
                durable=True
            )
            
            # Bindings
            await self.email_send_queue.bind(self.exchange, self.config.routing_keys["email_send"])
            await self.email_send_dlt_queue.bind(dlt_exchange, self.config.routing_keys["email_failed"])
            
            logger.info(f"Queues e exchanges configurados com sucesso: {exchange_name}, {dlt_exchange_name}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar queues: {e}")
            raise
    
    async def get_retry_count(self, message: AbstractIncomingMessage) -> int:
        """Obtém o número de tentativas da mensagem"""
        try:
            headers = message.headers or {}
            x_death = headers.get("x-death", [])
            
            if not x_death:
                return 0
            
            # Contar tentativas do x-death
            total_attempts = 0
            for death in x_death:
                if isinstance(death, dict) and "count" in death:
                    total_attempts += death["count"]
            
            return total_attempts
            
        except Exception as e:
            logger.warning(f"Erro ao obter contagem de retry: {e}")
            return 0
    
    def should_retry(self, retry_count: int) -> bool:
        """Verifica se deve tentar novamente baseado na configuração"""
        return retry_count < self.config.retry["max_attempts"]
    
    async def close(self) -> None:
        """Fecha conexão com RabbitMQ"""
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("Conexão RabbitMQ fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão RabbitMQ: {e}")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        await self.setup_queues()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
