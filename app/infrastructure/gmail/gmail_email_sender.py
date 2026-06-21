import base64
import os
import logging
from email.message import EmailMessage
from typing import Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

from app.domain.errors import EmailSendError
from app.domain.models import EmailPayload
from app.infrastructure.token_manager import TokenManagerClientFactory
from app.infrastructure.token_manager.token_manager_client import TokenManagerError

logger = logging.getLogger(__name__)

class GmailEmailSender:
    def __init__(self, sender_email: str, client_secrets_file: str, token_file: str, scopes: list, auth_mode: str = "token-only", token_manager_url: str = "http://srv-token-manager:8700"):
        self.sender_email = sender_email
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        self.scopes = scopes
        self.auth_mode = auth_mode
        self.token_manager_url = token_manager_url
        self._service = None
        self._creds: Optional[Credentials] = None
        self._token_manager_client = None

    def _get_token_manager_client(self):
        """Get TokenManagerClient instance."""
        if self._token_manager_client is None:
            self._token_manager_client = TokenManagerClientFactory.get_client(self.token_manager_url)
        return self._token_manager_client

    async def _ensure_credentials_from_token_manager(self):
        """Ensure credentials using TokenManagerClient."""
        try:
            logger.debug(f"Getting credentials from TokenManager for {self.sender_email}")
            
            # Get token from TokenManager
            token_data = await self._get_token_manager_client().get_token(self.sender_email)
            
            # Create credentials from token data
            creds = Credentials.from_authorized_user_info(token_data, self.scopes)
            
            if not creds or not creds.valid:
                logger.warning("Token from TokenManager is invalid, attempting refresh")
                # Try to refresh token
                token_data = await self._get_token_manager_client().refresh_token(self.sender_email)
                creds = Credentials.from_authorized_user_info(token_data, self.scopes)
            
            if not creds or not creds.valid:
                raise EmailSendError("Invalid credentials from TokenManager")
            
            self._creds = creds
            self._service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service initialized with TokenManager credentials")
            
        except TokenManagerError as e:
            logger.error(f"TokenManager error: {e}")
            raise EmailSendError(f"TokenManager error: {e}") from e
        except Exception as e:
            logger.error(f"Error getting credentials from TokenManager: {e}")
            raise EmailSendError(f"Failed to get credentials from TokenManager: {e}") from e

    def _ensure_credentials(self):
        try:
            logger.debug(f"🔍 token_file: {self.token_file}")
            logger.debug(f"🔍 client_secrets_file: {self.client_secrets_file}")
            creds: Optional[Credentials] = None

            # Carregar credenciais existentes
            if self.token_file and os.path.exists(self.token_file):
                try:
                    creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
                    logger.info("Credenciais carregadas do arquivo de token")
                except Exception as e:
                    logger.warning(f"Erro ao carregar token existente: {e}")
                    creds = None

            # Se não há credenciais válidas, tentar refresh
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Token expirado, tentando refresh automático...")
                    creds.refresh(Request())
                    
                    # Salvar token atualizado
                    os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
                    with open(self.token_file, "w", encoding="utf-8") as f:
                        f.write(creds.to_json())
                    
                    logger.info("Token renovado automaticamente com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao renovar token automaticamente: {e}")
                    creds = None

            # Se ainda não há credenciais válidas e auth_mode permite console
            if (not creds or not creds.valid) and self.auth_mode == "console":
                logger.info("Iniciando fluxo de autenticação interativo...")
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
                creds = flow.run_local_server(port=0)
                os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
                with open(self.token_file, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
                logger.info("Novo token gerado via fluxo interativo")

            # Verificar se temos credenciais válidas
            if not creds or not creds.valid:
                raise EmailSendError("Credenciais inválidas ou expiradas. Execute o script de geração de token ou configure auth_mode=console.")

            self._creds = creds
            self._service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar credenciais Gmail: {e}")
            raise EmailSendError(f"Falha ao configurar credenciais Gmail: {e}") from e

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
            # texto alternativo
            plain = payload.message or ""
            msg.set_content(plain)
            msg.add_alternative(payload.html, subtype="html")
        else:
            msg.set_content(payload.message or "")

        return msg

    async def send_async(self, payload: EmailPayload) -> str:
        """Send email asynchronously using TokenManager."""
        try:
            await self._ensure_credentials_from_token_manager()

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
            logger.info(f"E-mail enviado com sucesso via TokenManager. Message ID: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail via TokenManager: {e}")
            # Se o erro for de credenciais, tentar refresh uma vez
            if "invalid_grant" in str(e) or "Token has been expired" in str(e):
                logger.warning("Token expirado, tentando refresh via TokenManager...")
                try:
                    self._creds = None
                    self._service = None
                    await self._ensure_credentials_from_token_manager()
                    
                    # Tentar enviar novamente
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
                    logger.info(f"E-mail enviado após refresh via TokenManager. Message ID: {message_id}")
                    return message_id
                    
                except Exception as retry_error:
                    logger.error(f"Erro após tentativa de refresh via TokenManager: {retry_error}")
                    raise EmailSendError(f"Falha no envio após refresh via TokenManager: {retry_error}") from retry_error
            else:
                raise EmailSendError(f"Falha no envio do e-mail via TokenManager: {e}") from e

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
            logger.info(f"E-mail enviado com sucesso. Message ID: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail: {e}")
            # Se o erro for de credenciais, tentar refresh uma vez
            if "invalid_grant" in str(e) or "Token has been expired" in str(e):
                logger.warning("Token expirado, tentando refresh...")
                try:
                    self._creds = None
                    self._service = None
                    self._ensure_credentials()
                    
                    # Tentar enviar novamente
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
                    logger.info(f"E-mail enviado após refresh do token. Message ID: {message_id}")
                    return message_id
                    
                except Exception as retry_error:
                    logger.error(f"Erro após tentativa de refresh: {retry_error}")
                    raise EmailSendError(f"Falha no envio após refresh do token: {retry_error}") from retry_error
            else:
                raise EmailSendError(f"Falha no envio do e-mail: {e}") from e