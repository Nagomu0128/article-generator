"""Claude API service implementation.

This module provides the concrete implementation of the LLM service
using Anthropic's Claude API. It includes retry logic and error handling.
"""
from functools import lru_cache
from typing import Optional

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.shared.domain.exceptions import ExternalServiceError
from app.shared.domain.llm.base import BaseLLMService, LLMConfig, LLMResponse

settings = get_settings()


class ClaudeService(BaseLLMService):
    """Claude API service implementation.

    This class implements the BaseLLMService interface using
    Anthropic's Claude API. It handles API calls, retries,
    and error conversion.

    Attributes:
        client: Async Anthropic API client
        default_config: Default configuration for generation
    """

    def __init__(self):
        """Initialize Claude service with API client."""
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key
        )
        self.default_config = LLMConfig()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30)
    )
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Generate text using Claude API.

        This method calls the Claude API with retry logic.
        Failed requests are retried up to 3 times with exponential backoff.

        Args:
            system_prompt: System-level instructions
            user_prompt: User's input/request
            config: Optional configuration (uses default if not provided)

        Returns:
            LLMResponse containing generated content and metadata

        Raises:
            ExternalServiceError: If API call fails after retries
        """
        cfg = config or self.default_config

        try:
            response = await self.client.messages.create(
                model=cfg.model,
                max_tokens=cfg.max_tokens,
                temperature=cfg.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Extract text content from response
            content = "".join(
                block.text for block in response.content
                if block.type == "text"
            )

            return LLMResponse(
                content=content,
                model=response.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens
            )

        except anthropic.APIError as e:
            raise ExternalServiceError("Claude API", str(e))


@lru_cache
def get_claude_service() -> ClaudeService:
    """Get singleton instance of Claude service.

    Returns:
        ClaudeService instance
    """
    return ClaudeService()
