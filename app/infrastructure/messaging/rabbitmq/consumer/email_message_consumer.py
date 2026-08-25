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
            await self._forward_to_dlq(message, str(e), correlation_id)
            await message.ack()
            
        except Exception as e:
            logger.error(f"=== ERRO AO PROCESSAR MENSAGEM ===")
            logger.error(f"Correlation ID: {correlation_id}")
            logger.error(f"Erro: {e}")
            import traceback
            tb_str = traceback.format_exc()
            logger.error(f"Traceback: {tb_str}")
            await self._forward_to_dlq(message, str(e), correlation_id, tb_str)
            await message.ack()

    async def _forward_to_dlq(self, message, error_msg: str, correlation_id: str, stacktrace: str = ""):
        try:
            from aio_pika import Message as AioMessage
            headers = dict(message.headers or {})
            headers["x-exception-message"] = error_msg
            headers["x-exception-stacktrace"] = stacktrace[:2000] if stacktrace else ""
            headers["x-original-queue"] = self.rabbitmq_config.config.queues.get("email_send", "unknown")
            headers["x-correlation-id"] = correlation_id
            
            dlt_exchange_name = self.rabbitmq_config.config.exchanges.get("email_exchange_dlt", "srv-email-google-sender-exchange-dlt")
            routing_key = self.rabbitmq_config.config.routing_keys.get("email_failed", "failed")
            
            dlt_exchange = await self.rabbitmq_config.channel.get_exchange(dlt_exchange_name)
            await dlt_exchange.publish(
                AioMessage(
                    body=message.body,
                    headers=headers,
                    content_type=message.content_type
                ),
                routing_key=routing_key
            )
            logger.info(f"🚨 [DLQ Forense] Mensagem {correlation_id} encaminhada para {dlt_exchange_name} com metadados forenses")
        except Exception as dlq_err:
            logger.error(f"Falha ao enviar mensagem para DLQ forense: {dlq_err}")

