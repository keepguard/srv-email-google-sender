import asyncio
import logging
import json
from typing import Optional
try:
    from aio_pika.exceptions import QueueEmpty
except Exception:  # fallback if import path changes
    class QueueEmpty(Exception):
        pass

logger = logging.getLogger(__name__)

class RabbitMQLifecycleManager:
    def __init__(self, rabbitmq_config, send_email_usecase):
        self.rabbitmq_config = rabbitmq_config
        self.send_email_usecase = send_email_usecase
        self.is_connected = False
        self._consumer_task = None
    
    async def start(self):
        try:
            logger.info("Iniciando RabbitMQ Lifecycle Manager")
            
            # Conectar com RabbitMQ
            try:
                from app.infrastructure.messaging.rabbitmq.config.rabbitmq_config import RabbitMQConfig
                self.rabbitmq_config = RabbitMQConfig(self.rabbitmq_config)
                await self.rabbitmq_config.connect()
                await self.rabbitmq_config.setup_queues()
                self.is_connected = True
                logger.info("RabbitMQ conectado com sucesso")
                
                # Iniciar consumer em background
                self._consumer_task = asyncio.create_task(self._consume_messages())
                
            except Exception as e:
                logger.error(f"Erro ao conectar com RabbitMQ: {e}")
                self.is_connected = False
                logger.warning("Continuando sem RabbitMQ Consumer")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar RabbitMQ Lifecycle Manager: {e}")
            self.is_connected = False
    
    async def stop(self):
        try:
            logger.info("Parando RabbitMQ Lifecycle Manager")
            
            if self._consumer_task and not self._consumer_task.done():
                self._consumer_task.cancel()
                try:
                    await self._consumer_task
                except asyncio.CancelledError:
                    pass
            
            if hasattr(self.rabbitmq_config, 'close') and self.is_connected:
                await self.rabbitmq_config.close()
            
            self.is_connected = False
            logger.info("RabbitMQ Lifecycle Manager parado")
            
        except Exception as e:
            logger.error(f"Erro ao parar RabbitMQ Consumer: {e}")
    
    async def _consume_messages(self):
        """Consumer simples que processa mensagens da fila"""
        try:
            logger.info("Iniciando consumer de mensagens RabbitMQ")
            
            while self.is_connected:
                try:
                    # Verificar se há mensagens na fila
                    if self.rabbitmq_config.email_send_queue:
                        try:
                            message = await self.rabbitmq_config.email_send_queue.get(no_ack=False)
                        except QueueEmpty:
                            # Fila vazia não é erro; apenas aguardar
                            await asyncio.sleep(1)
                            continue

                        if message:
                            await self._process_message(message)
                        else:
                            # Não há mensagens, aguardar um pouco
                            await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Erro ao consumir mensagem: {e}")
                    await asyncio.sleep(1)
                    
        except asyncio.CancelledError:
            logger.info("Consumer task cancelado")
        except Exception as e:
            logger.error(f"Erro no consumer task: {e}")
    
    async def _process_message(self, message):
        """Processa uma mensagem recebida"""
        try:
            logger.info("=== MENSAGEM RECEBIDA VIA RABBITMQ ===")
            
            # Deserializar mensagem
            body = message.body.decode('utf-8')
            data = json.loads(body)
            logger.info(f"Dados da mensagem: {data}")
            
            # Converter para EmailPayload
            from app.domain.models import EmailPayload
            
            # Extrair texto simples do HTML
            message_text = None
            if data.get('html'):
                import re
                message_text = re.sub(r'<[^>]+>', '', data['html'])
                message_text = message_text.strip()
            
            email_payload = EmailPayload(
                to=data['to'],
                subject=data['subject'],
                message=message_text,
                html=data.get('html'),
                cc=data.get('cc'),
                replyTo=data.get('reply_to')
            )
            
            logger.info(f"EmailPayload: {email_payload}")
            
            # Enviar e-mail
            logger.info("Enviando e-mail via SendEmailUseCase...")
            message_id = self.send_email_usecase.execute(email_payload)
            
            logger.info(f"=== E-MAIL ENVIADO COM SUCESSO ===")
            logger.info(f"Message ID: {message_id}")
            
            # Confirmar mensagem
            await message.ack()
            logger.info("Mensagem confirmada (ACK)")
            
        except Exception as e:
            logger.error(f"=== ERRO AO PROCESSAR MENSAGEM ===")
            logger.error(f"Erro: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Rejeitar mensagem
            await message.nack(requeue=False)
            logger.error("Mensagem rejeitada (NACK)")
    
    async def health_check(self):
        return self.is_connected