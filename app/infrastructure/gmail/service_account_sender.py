import base64
import logging
from email.message import EmailMessage
from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.domain.errors import EmailSendError
from app.domain.models import EmailPayload

logger = logging.getLogger(__name__)

class ServiceAccountEmailSender:
    """Sender usando Service Account (recomendado para produção)"""
    
    def __init__(self, sender_email: str, service_account_file: str, delegated_user: str = None):
        self.sender_email = sender_email
        self.service_account_file = service_account_file
        self.delegated_user = delegated_user or sender_email
        self._service = None
        self._creds = None

    def _ensure_credentials(self):
        try:
            logger.info("Configurando credenciais Service Account...")
            
            # Scopes necessários para Gmail
            scopes = ['https://www.googleapis.com/auth/gmail.send']
            
            # Carregar credenciais do service account
            self._creds = service_account.Credentials.from_service_account_file(
                self.service_account_file, 
                scopes=scopes
            )
            
            # Se há usuário delegado, configurar domain-wide delegation
            if self.delegated_user:
                self._creds = self._creds.with_subject(self.delegated_user)
                logger.info(f"Configurado domain-wide delegation para: {self.delegated_user}")
            
            self._service = build("gmail", "v1", credentials=self._creds)
            logger.info("Service Account configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar Service Account: {e}")
            raise EmailSendError(f"Falha ao configurar Service Account: {e}") from e

    def _build_message(self, payload: EmailPayload) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = payload.to
        if payload.cc:
            msg["Cc"] = payload.cc
        if payload.replyTo:
            msg["Reply-To"] = payload.replyTo
        msg["Subject"] = payload.subject

        if payload.html:
            plain = payload.message or ""
            msg.set_content(plain)
            msg.add_alternative(payload.html, subtype="html")
        else:
            msg.set_content(payload.message or "")

        return msg

    def send(self, payload: EmailPayload) -> str:
        try:
            self._ensure_credentials()

            msg = self._build_message(payload)
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            body = {"raw": raw}

            result = (
                self._service.users()
                .messages()
                .send(userId="me", body=body)
                .execute()
            )
            
            message_id = result.get("id")
            logger.info(f"E-mail enviado via Service Account. Message ID: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail via Service Account: {e}")
            raise EmailSendError(f"Falha no envio do e-mail: {e}") from e
