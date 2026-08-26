"""Token Manager Client for srv-token-manager communication."""

import httpx
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenManagerConfig:
    """Token Manager configuration."""
    base_url: str
    timeout: int = 10
    retry_attempts: int = 3


class TokenManagerClient:
    """Client for communicating with srv-token-manager service."""
    
    def __init__(self, config: TokenManagerConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client instance."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def get_token(self, email: str) -> Dict[str, Any]:
        """Get valid token for email."""
        async with httpx.AsyncClient(base_url=self.config.base_url, timeout=self.config.timeout) as client:
            for attempt in range(self.config.retry_attempts):
                try:
                    logger.debug(f"Getting token for {email} (attempt {attempt + 1})")
                    
                    response = await client.get(f"/api/v1/tokens/gmail/{email}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.debug(f"Token retrieved successfully for {email}")
                        return data.get("token", {})
                    
                    elif response.status_code == 404:
                        logger.error(f"Token not found for {email}")
                        raise TokenManagerError(f"Token not found for email: {email}")
                    
                    elif response.status_code == 410:
                        logger.warning(f"Token expired for {email}, attempting refresh")
                        return await self.refresh_token(email)
                    
                    else:
                        logger.warning(f"Unexpected status code {response.status_code} for {email}")
                        
                except httpx.RequestError as e:
                    logger.warning(f"Request error getting token for {email} (attempt {attempt + 1}): {e}")
                    if attempt == self.config.retry_attempts - 1:
                        raise TokenManagerError(f"Failed to connect to TokenManager: {e}") from e
                        
                except TokenManagerError:
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error getting token for {email}: {e}")
                    if attempt == self.config.retry_attempts - 1:
                        raise TokenManagerError(f"Unexpected error: {e}") from e
            
            raise TokenManagerError(f"Failed to get token for {email} after {self.config.retry_attempts} attempts")
    
    async def refresh_token(self, email: str) -> Dict[str, Any]:
        """Refresh token for email."""
        async with httpx.AsyncClient(base_url=self.config.base_url, timeout=self.config.timeout) as client:
            try:
                logger.debug(f"Refreshing token for {email}")
                
                response = await client.post(f"/api/v1/tokens/gmail/{email}/refresh")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Token refreshed successfully for {email}")
                    return data.get("token", {})
                
                elif response.status_code == 404:
                    logger.error(f"Token not found for refresh: {email}")
                    raise TokenManagerError(f"Token not found for refresh: {email}")
                
                else:
                    logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                    raise TokenManagerError(f"Failed to refresh token: {response.status_code}")
                    
            except httpx.RequestError as e:
                logger.error(f"Request error refreshing token for {email}: {e}")
                raise TokenManagerError(f"Failed to refresh token: {e}") from e
    
    async def get_token_status(self, email: str) -> Dict[str, Any]:
        """Get token status for email."""
        client = await self._get_client()
        
        try:
            logger.debug(f"Getting token status for {email}")
            
            response = await client.get(f"/api/v1/tokens/gmail/{email}/status")
            
            if response.status_code == 200:
                logger.debug(f"Token status retrieved for {email}")
                return response.json()
            
            elif response.status_code == 404:
                logger.warning(f"Token not found for status check: {email}")
                return {"email": email, "is_valid": False, "is_expired": True}
            
            else:
                logger.error(f"Failed to get token status: {response.status_code} - {response.text}")
                raise TokenManagerError(f"Failed to get token status: {response.status_code}")
                
        except httpx.RequestError as e:
            logger.error(f"Request error getting token status for {email}: {e}")
            raise TokenManagerError(f"Failed to get token status: {e}")
    
    async def health_check(self) -> bool:
        """Check if token manager service is healthy."""
        client = await self._get_client()
        
        try:
            response = await client.get("/health/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


class TokenManagerError(Exception):
    """Token Manager Client error."""
    pass
