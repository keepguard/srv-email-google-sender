#!/usr/bin/env python3
"""
Script para monitorar e renovar automaticamente tokens Gmail
Executar como cron job ou serviço
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/gmail-token-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_token_expiry(token_file: str, client_secrets_file: str, scopes: list) -> bool:
    """Verifica se o token está próximo do vencimento e renova se necessário"""
    try:
        if not os.path.exists(token_file):
            logger.error(f"Arquivo de token não encontrado: {token_file}")
            return False
        
        # Carregar credenciais
        creds = Credentials.from_authorized_user_file(token_file, scopes)
        
        # Verificar se está expirado ou próximo do vencimento (1 hora antes)
        expiry_time = creds.expiry
        if expiry_time:
            time_until_expiry = expiry_time - datetime.utcnow()
            logger.info(f"Token expira em: {time_until_expiry}")
            
            # Se expira em menos de 1 hora, renovar
            if time_until_expiry < timedelta(hours=1):
                logger.warning("Token próximo do vencimento, renovando...")
                
                if creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        
                        # Salvar token renovado
                        with open(token_file, 'w') as f:
                            f.write(creds.to_json())
                        
                        logger.info("Token renovado com sucesso")
                        return True
                    except Exception as e:
                        logger.error(f"Erro ao renovar token: {e}")
                        return False
                else:
                    logger.error("Token não tem refresh_token, renovação manual necessária")
                    return False
            else:
                logger.info("Token ainda válido")
                return True
        else:
            logger.warning("Token não tem data de expiração definida")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao verificar token: {e}")
        return False

def main():
    """Função principal do monitor"""
    # Configurações
    token_file = os.getenv('GMAIL_TOKEN_FILE', '/app/secure/token.json')
    client_secrets_file = os.getenv('GMAIL_CLIENT_SECRETS', '/app/secure/credentials.json')
    scopes = ['https://www.googleapis.com/auth/gmail.send']
    
    logger.info("Iniciando monitor de token Gmail...")
    logger.info(f"Token file: {token_file}")
    logger.info(f"Client secrets: {client_secrets_file}")
    
    # Verificar e renovar token
    success = check_token_expiry(token_file, client_secrets_file, scopes)
    
    if success:
        logger.info("Monitor de token concluído com sucesso")
        sys.exit(0)
    else:
        logger.error("Falha no monitor de token")
        sys.exit(1)

if __name__ == "__main__":
    main()
