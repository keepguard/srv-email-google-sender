"""Token Manager Client Factory."""

import logging
from typing import Optional

from app.infrastructure.token_manager.token_manager_client import TokenManagerClient, TokenManagerConfig

logger = logging.getLogger(__name__)


class TokenManagerClientFactory:
    """Factory for creating TokenManagerClient instances."""
    
    _instance: Optional[TokenManagerClient] = None
    
    @classmethod
    def get_client(cls, base_url: str = "http://srv-token-manager:8700") -> TokenManagerClient:
        """Get singleton TokenManagerClient instance."""
        if cls._instance is None:
            config = TokenManagerConfig(
                base_url=base_url,
                timeout=10,
                retry_attempts=3
            )
            cls._instance = TokenManagerClient(config)
            logger.info(f"TokenManagerClient created with base_url: {base_url}")
        
        return cls._instance
    
    @classmethod
    async def close_client(cls):
        """Close the singleton client."""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
            logger.info("TokenManagerClient closed")
