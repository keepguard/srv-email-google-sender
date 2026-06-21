from abc import ABC, abstractmethod
from app.domain.messaging.email_message import EmailMessage


class MessageConsumerPort(ABC):
    """Port de entrada para processamento de mensagens de e-mail"""
    
    @abstractmethod
    async def process_message(self, message: EmailMessage) -> None:
        """
        Processa uma mensagem de e-mail recebida do RabbitMQ
        
        Args:
            message: EmailMessage contendo os dados do e-mail a ser enviado
            
        Raises:
            MessageProcessingError: Em caso de erro no processamento
        """
        pass
