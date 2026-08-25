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
        max_attempts = 3
        backoff = 1.0
        
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
            
            # Processar mensagem com até 3 tentativas e backoff exponencial
            last_err = None
            for attempt in range(1, max_attempts + 1):
                try:
                    if self.message_processor:
                        await self.message_processor.process_message(email_message)
                        logger.info(f"=== E-MAIL ENVIADO COM SUCESSO (Tentativa {attempt}) ===")
                    else:
                        logger.warning("Message processor não configurado - e-mail não será enviado")
                    
                    await message.ack()
                    logger.info(f"=== MENSAGEM PROCESSADA COM SUCESSO ===")
                    return
                except MessageValidationError as val_err:
                    # Erro de validação não deve ter retry
                    logger.error(f"Erro de validação irrecuperável: {val_err}")
                    await self._forward_to_dlq(message, str(val_err), correlation_id, "", 1)
                    await message.ack()
                    return
                except Exception as proc_err:
                    last_err = proc_err
                    logger.warning(f"⚠️ Falha na tentativa {attempt}/{max_attempts}: {proc_err}")
                    if attempt < max_attempts:
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2.0, 5.0)

            # Esgotou tentativas
            import traceback
            tb_str = traceback.format_exc()
            logger.error(f"❌ Esgotadas todas as tentativas para {correlation_id}. Encaminhando para DLQ.")
            await self._forward_to_dlq(message, str(last_err), correlation_id, tb_str, max_attempts)
            await message.ack()
            
        except Exception as e:
            logger.error(f"=== ERRO GERAL AO PROCESSAR MENSAGEM ===")
            logger.error(f"Correlation ID: {correlation_id}")
            logger.error(f"Erro: {e}")
            import traceback
            tb_str = traceback.format_exc()
            await self._forward_to_dlq(message, str(e), correlation_id, tb_str, 1)
            await message.ack()

    async def _forward_to_dlq(self, message, error_msg: str, correlation_id: str, stacktrace: str = "", retry_count: int = 1):
        try:
            from aio_pika import Message as AioMessage
            import datetime
            headers = dict(message.headers or {})
            headers["x-exception-message"] = str(error_msg)
            headers["x-exception-stacktrace"] = stacktrace[:2000] if stacktrace else ""
            headers["x-original-queue"] = self.rabbitmq_config.config.queues.get("email_send", "unknown")
            headers["x-correlation-id"] = correlation_id
            headers["x-retry-count"] = retry_count
            headers["x-failed-timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
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
            logger.info(f"🚨 [DLQ Forense] Mensagem {correlation_id} encaminhada para {dlt_exchange_name} com metadados forenses (Retries: {retry_count})")
        except Exception as dlq_err:
            logger.error(f"Falha ao enviar mensagem para DLQ forense: {dlq_err}")

