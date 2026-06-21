from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.messaging.email_message import EmailMessage


class EmailMessageDTO(BaseModel):
    """DTO para deserialização de mensagens RabbitMQ"""
    
    x_application: str = Field(..., description="Identificador da aplicação origem")
    x_correlation_id: str = Field(..., description="ID de correlação para rastreamento")
    to: str = Field(..., description="E-mail destinatário")
    subject: str = Field(..., description="Assunto do e-mail")
    html: Optional[str] = Field(None, description="Conteúdo HTML do e-mail")
    cc: Optional[str] = Field(None, description="E-mail em cópia")
    reply_to: Optional[str] = Field(None, description="E-mail para resposta")
    
    @field_validator('x_application')
    @classmethod
    def validate_x_application(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('x_application não pode ser vazio')
        return v.strip()
    
    @field_validator('x_correlation_id')
    @classmethod
    def validate_x_correlation_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('x_correlation_id não pode ser vazio')
        return v.strip()
    
    @field_validator('to')
    @classmethod
    def validate_to(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('to não pode ser vazio')
        return v.strip()
    
    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('subject não pode ser vazio')
        return v.strip()
    
    @field_validator('cc')
    @classmethod
    def validate_cc(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v
    
    @field_validator('reply_to')
    @classmethod
    def validate_reply_to(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v
    
    def to_domain(self) -> EmailMessage:
        """Converte DTO para entity de domínio"""
        return EmailMessage(
            x_application=self.x_application,
            x_correlation_id=self.x_correlation_id,
            to=self.to,
            subject=self.subject,
            html=self.html,
            cc=self.cc,
            reply_to=self.reply_to
        )
    
    class Config:
        """Configuração do Pydantic"""
        str_strip_whitespace = True
        validate_assignment = True
