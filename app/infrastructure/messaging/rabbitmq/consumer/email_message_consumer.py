import asyncio
import json
import logging
from typing import Optional
from aio_pika.abc import AbstractIncomingMessage

from app.domain.messaging.email_message import EmailMessage
from app.domain.errors import MessageValidationError, MessageProcessingError
from app.infrastructure.messaging.rabbitmq.dto.email_message_dto import EmailMessageDTO

logger = logging.getLogger(__name__)

class EmailMessageConsumer:
    def __init__(self, rabbitmq_config, message_processor):
        self.rabbitmq_config = rabbitmq_config
        self.message_processor = message_processor
        self.is_consuming = False
    
    async def start_consuming(self):
        try:
            if not self.rabbitmq_config.email_send_queue:
                raise RuntimeError("Queue não configurada")
            
            self.is_consuming = True
            logger.info("=== INICIANDO CONSUMER RABBITMQ ===")
            
            await self.rabbitmq_config.email_send_queue.consume(
                self._process_message,
                no_ack=False
            )
            
            logger.info("=== CONSUMER INICIADO COM SUCESSO ===")
            
        except Exception as e:
            logger.error(f"=== ERRO AO INICIAR CONSUMER: {e} ===")
            raise
    
    async def stop_consuming(self):
        self.is_consuming = False
        logger.info("Parando consumer RabbitMQ")
    
    async def _process_message(self, message):
        correlation_id = "unknown"
        
        try:
            correlation_id = message.headers.get("x-correlation-id", "unknown") if message.headers else "unknown"
            logger.info(f"=== MENSAGEM RECEBIDA ===")
            logger.info(f"Correlation ID: {correlation_id}")
            logger.info(f"Delivery Tag: {message.delivery_tag}")
            
            # Deserializar mensagem
            body = message.body.decode('utf-8')
            data = json.loads(body)
            logger.info(f"Dados da mensagem: {data}")
            
            # Converter para DTO e depois para domain entity
            email_dto = EmailMessageDTO(**data)
            email_message = email_dto.to_domain()
            
            # Processar mensagem usando o message_processor (SendEmailUseCase)
            if self.message_processor:
                await self.message_processor.process_message(email_message)
                logger.info(f"=== E-MAIL ENVIADO COM SUCESSO ===")
            else:
                logger.warning("Message processor não configurado - e-mail não será enviado")
            
            await message.ack()
            logger.info(f"=== MENSAGEM PROCESSADA COM SUCESSO ===")
            
        except MessageValidationError as e:
            logger.error(f"=== ERRO DE VALIDAÇÃO ===")
            logger.error(f"Correlation ID: {correlation_id}")
            logger.error(f"Erro: {e}")
            await message.nack(requeue=False)
            
        except Exception as e:
            logger.error(f"=== ERRO AO PROCESSAR MENSAGEM ===")
            logger.error(f"Correlation ID: {correlation_id}")
            logger.error(f"Erro: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            await message.nack(requeue=False)
