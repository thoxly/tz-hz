"""
LLM Client - клиент для работы с языковыми моделями.
"""
import logging
from typing import Optional, Dict, Any, List
import json
import os
from pathlib import Path

# Загружаем переменные из .env если есть
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv не обязателен, если переменные установлены в системе

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Клиент для работы с языковыми моделями (OpenAI, Anthropic и т.д.).
    """
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Инициализация LLM клиента.
        
        Args:
            provider: Провайдер LLM ("openai", "anthropic", "deepseek", "ollama")
                     Если None, берется из переменных окружения или config
            model: Название модели (если None, используется по умолчанию)
        """
        # Если provider не указан, берем из переменных окружения
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "ollama")
        
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self.logger = logging.getLogger(__name__)
        
        # Инициализация клиента в зависимости от провайдера
        self.client = self._init_client(provider)
    
    def _get_default_model(self, provider: str) -> str:
        """Возвращает модель по умолчанию для провайдера."""
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-haiku-20240307",
            "deepseek": "deepseek-chat",
            "ollama": "llama3",  # или другая локальная модель
            "local": "local"
        }
        return defaults.get(provider, "gpt-4o-mini")
    
    def _init_client(self, provider: str):
        """Инициализирует клиент для выбранного провайдера."""
        if provider == "openai":
            try:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    self.logger.warning("OPENAI_API_KEY не установлен. LLM будет работать в режиме заглушки.")
                    return None
                return openai.OpenAI(api_key=api_key)
            except ImportError:
                self.logger.warning("openai не установлен. Установите: pip install openai")
                return None
        
        elif provider == "anthropic":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    self.logger.warning("ANTHROPIC_API_KEY не установлен. LLM будет работать в режиме заглушки.")
                    return None
                return anthropic.Anthropic(api_key=api_key)
            except ImportError:
                self.logger.warning("anthropic не установлен. Установите: pip install anthropic")
                return None
        
        elif provider == "deepseek":
            try:
                import openai
                # DeepSeek использует OpenAI-совместимый API
                # Пробуем загрузить из переменных окружения или из config
                from app.config import settings
                api_key = os.getenv("DEEPSEEK_API_KEY") or settings.DEEPSEEK_API_KEY
                base_url = os.getenv("DEEPSEEK_BASE_URL") or settings.DEEPSEEK_BASE_URL
                if not api_key:
                    self.logger.warning("DEEPSEEK_API_KEY не установлен. LLM будет работать в режиме заглушки.")
                    return None
                return openai.OpenAI(api_key=api_key, base_url=base_url)
            except ImportError:
                self.logger.warning("openai не установлен. Установите: pip install openai")
                return None
        
        elif provider == "ollama":
            # Ollama работает локально, не требует API ключа
            self.logger.info("Используется Ollama (локальная модель)")
            return "ollama"  # Специальный маркер для Ollama
        
        else:
            self.logger.warning(f"Провайдер {provider} не поддерживается. Используется режим заглушки.")
            return None
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Генерирует ответ от LLM.
        
        Args:
            system_prompt: Системный промпт
            user_prompt: Пользовательский промпт
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов
            response_format: Формат ответа (например, {"type": "json_object"})
            
        Returns:
            Ответ от LLM
        """
        if not self.client:
            # Режим заглушки для разработки
            self.logger.warning("LLM клиент не инициализирован. Возвращаем заглушку.")
            return self._generate_stub_response(system_prompt, user_prompt)
        
        try:
            if self.provider == "openai":
                return await self._generate_openai(
                    system_prompt, user_prompt, temperature, max_tokens, response_format
                )
            elif self.provider == "anthropic":
                return await self._generate_anthropic(
                    system_prompt, user_prompt, temperature, max_tokens
                )
            elif self.provider == "deepseek":
                return await self._generate_deepseek(
                    system_prompt, user_prompt, temperature, max_tokens, response_format
                )
            elif self.provider == "ollama":
                return await self._generate_ollama(
                    system_prompt, user_prompt, temperature, max_tokens
                )
            else:
                return self._generate_stub_response(system_prompt, user_prompt)
        except Exception as e:
            self.logger.error(f"Ошибка при генерации ответа от LLM: {e}", exc_info=True)
            return self._generate_stub_response(system_prompt, user_prompt)
    
    async def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]]
    ) -> str:
        """Генерация через OpenAI API."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    async def _generate_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Генерация через Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    
    async def _generate_deepseek(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]]
    ) -> str:
        """Генерация через DeepSeek API (OpenAI-совместимый)."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    async def _generate_ollama(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Генерация через Ollama (локальная модель)."""
        try:
            import aiohttp
            import json as json_lib
            
            # Ollama API endpoint
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            url = f"{ollama_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                },
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("message", {}).get("content", "")
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Ollama API error: {error_text}")
                        return self._generate_stub_response(system_prompt, user_prompt)
        except ImportError:
            self.logger.error("aiohttp не установлен. Установите: pip install aiohttp")
            return self._generate_stub_response(system_prompt, user_prompt)
        except Exception as e:
            self.logger.error(f"Ошибка при обращении к Ollama: {e}")
            return self._generate_stub_response(system_prompt, user_prompt)
    
    def _generate_stub_response(self, system_prompt: str, user_prompt: str) -> str:
        """Заглушка для разработки без LLM."""
        return json.dumps({
            "error": "LLM не настроен",
            "message": "Установите API ключ или используйте Ollama для локальных моделей",
            "available_providers": ["openai", "anthropic", "deepseek", "ollama"],
            "system_prompt_length": len(system_prompt),
            "user_prompt_length": len(user_prompt)
        }, ensure_ascii=False, indent=2)
    
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Генерирует JSON ответ от LLM.
        
        Args:
            system_prompt: Системный промпт
            user_prompt: Пользовательский промпт
            temperature: Температура генерации
            max_tokens: Максимальное количество токенов
            
        Returns:
            Распарсенный JSON ответ
        """
        response_format = {"type": "json_object"}
        response_text = await self.generate(
            system_prompt, user_prompt, temperature, max_tokens, response_format
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            # Пытаемся извлечь JSON из текста
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Не удалось распарсить JSON из ответа: {response_text[:200]}")

