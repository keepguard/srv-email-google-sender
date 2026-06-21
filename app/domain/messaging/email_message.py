from typing import Optional
from pydantic import EmailStr, Field, field_validator
from app.domain.models import EmailPayload
from app.domain.errors import MessageValidationError


class EmailMessage:
    """Entity de domínio para mensagem de e-mail do RabbitMQ"""
    
    def __init__(
        self,
        x_application: str,
        x_correlation_id: str,
        to: str,
        subject: str,
        html: Optional[str] = None,
        cc: Optional[str] = None,
        reply_to: Optional[str] = None
    ):
        self.x_application = x_application
        self.x_correlation_id = x_correlation_id
        self.to = to
        self.subject = subject
        self.html = html
        self.cc = cc
        self.reply_to = reply_to
        
        # Validações de domínio
        self._validate()
    
    def _validate(self) -> None:
        """Valida os campos obrigatórios e formato de e-mail"""
        if not self.x_application or not self.x_application.strip():
            raise MessageValidationError("x_application é obrigatório")
        
        if not self.x_correlation_id or not self.x_correlation_id.strip():
            raise MessageValidationError("x_correlation_id é obrigatório")
        
        if not self.to or not self.to.strip():
            raise MessageValidationError("to é obrigatório")
        
        if not self.subject or not self.subject.strip():
            raise MessageValidationError("subject é obrigatório")
        
        # Validação básica de e-mail (formato simples)
        if "@" not in self.to or "." not in self.to.split("@")[-1]:
            raise MessageValidationError("to deve ser um e-mail válido")
        
        if self.cc and "@" not in self.cc:
            raise MessageValidationError("cc deve ser um e-mail válido")
        
        if self.reply_to and "@" not in self.reply_to:
            raise MessageValidationError("reply_to deve ser um e-mail válido")
    
    def to_email_payload(self) -> EmailPayload:
        """Converte para EmailPayload para uso no SendEmailUseCase"""
        # Extrair texto simples do HTML se necessário
        message_text = None
        if self.html:
            # Remover tags HTML para criar texto simples
            import re
            message_text = re.sub(r'<[^>]+>', '', self.html)
            message_text = message_text.strip()
        
        return EmailPayload(
            to=self.to,
            subject=self.subject,
            message=message_text,  # Texto simples
            html=self.html,        # HTML
            cc=self.cc,
            replyTo=self.reply_to
        )
    
    def __str__(self) -> str:
        return f"EmailMessage(x_correlation_id={self.x_correlation_id}, to={self.to}, subject={self.subject})"
    
    def __repr__(self) -> str:
        return self.__str__()
