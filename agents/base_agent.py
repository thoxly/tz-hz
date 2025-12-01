from abc import ABC, abstractmethod
from typing import Dict, Any
import aiohttp
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, mcp_client=None):
        self.mcp_client = mcp_client
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
    
    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "deepseek-reasoner"
    ) -> str:
        """
        Call DeepSeek LLM API.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            model: Model name
        
        Returns:
            LLM response text
        """
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        
        # Log request
        logger.info(f"Calling LLM ({model}) with system prompt length: {len(system_prompt)}")
        logger.debug(f"System prompt: {system_prompt[:200]}...")
        logger.debug(f"User prompt: {user_prompt[:200]}...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    
                    # Extract response
                    response_text = data["choices"][0]["message"]["content"]
                    
                    # Log response
                    logger.info(f"LLM response length: {len(response_text)}")
                    logger.debug(f"LLM response: {response_text[:200]}...")
                    
                    return response_text
        
        except Exception as e:
            logger.error(f"Error calling LLM: {e}", exc_info=True)
            raise
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input and return output."""
        pass

