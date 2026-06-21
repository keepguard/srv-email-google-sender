import logging
from app.domain.messaging.email_message import EmailMessage
from app.domain.errors import MessageProcessingError
from app.application.port.in.messaging.message_consumer_port import MessageConsumerPort
from app.application.usecases.send_email_usecase import SendEmailUseCase

logger = logging.getLogger(__name__)


class EmailMessageProcessor(MessageConsumerPort):
    """Adapter que implementa MessageConsumerPort usando SendEmailUseCase"""
    
    def __init__(self, send_email_usecase: SendEmailUseCase):
        self.send_email_usecase = send_email_usecase
    
    async def process_message(self, message: EmailMessage) -> None:
        """
        Processa uma mensagem de e-mail recebida do RabbitMQ
        
        Args:
            message: EmailMessage contendo os dados do e-mail a ser enviado
            
        Raises:
            MessageProcessingError: Em caso de erro no processamento
        """
        try:
            logger.info(f"=== INICIANDO PROCESSAMENTO DE E-MAIL ===")
            logger.info(f"Correlation ID: {message.x_correlation_id}")
            logger.info(f"Para: {message.to}")
            logger.info(f"Assunto: {message.subject}")
            logger.info(f"HTML: {message.html}")
            logger.info(f"CC: {message.cc}")
            logger.info(f"Reply-To: {message.reply_to}")
            
            # Converter para EmailPayload
            email_payload = message.to_email_payload()
            logger.info(f"EmailPayload convertido: {email_payload}")
            
            # Enviar e-mail usando o usecase
            logger.info("Chamando SendEmailUseCase.execute()...")
            message_id = self.send_email_usecase.execute(email_payload)
            
            logger.info(f"=== E-MAIL ENVIADO COM SUCESSO ===")
            logger.info(f"Correlation ID: {message.x_correlation_id}")
            logger.info(f"Message ID: {message_id}")
            
        except Exception as e:
            logger.error(f"=== ERRO AO PROCESSAR E-MAIL ===")
            logger.error(f"Correlation ID: {message.x_correlation_id}")
            logger.error(f"Erro: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise MessageProcessingError(f"Falha no envio do e-mail: {e}") from e
