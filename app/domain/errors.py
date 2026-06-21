
class EmailSendError(Exception):
    pass


class MessageValidationError(Exception):
    """Erro de validação de mensagem RabbitMQ"""
    pass


class MessageProcessingError(Exception):
    """Erro de processamento de mensagem RabbitMQ"""
    pass
