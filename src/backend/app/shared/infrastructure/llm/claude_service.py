"""Gemini API service implementation.

This module provides the concrete implementation of the LLM service
using Google's Gemini API. It includes retry logic and error handling.
"""
from functools import lru_cache
from typing import Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.shared.domain.exceptions import ExternalServiceError
from app.shared.domain.llm.base import BaseLLMService, LLMConfig, LLMResponse

settings = get_settings()


class ClaudeService(BaseLLMService):
    """Gemini API service implementation.

    This class implements the BaseLLMService interface using
    Google's Gemini API. It handles API calls, retries,
    and error conversion.

    Note: The class name is kept as ClaudeService for backward compatibility.

    Attributes:
        model: Generative model instance
        default_config: Default configuration for generation
    """

    def __init__(self):
        """Initialize Gemini service with API client."""
        genai.configure(api_key=settings.google_api_key)
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
        """Generate text using Gemini API.

        This method calls the Gemini API with retry logic.
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
            # Initialize model with configuration
            model = genai.GenerativeModel(
                model_name=cfg.model,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=cfg.max_tokens,
                    temperature=cfg.temperature,
                ),
                system_instruction=system_prompt
            )

            # Generate content
            response = await model.generate_content_async(user_prompt)

            # Extract token usage information
            input_tokens = response.usage_metadata.prompt_token_count
            output_tokens = response.usage_metadata.candidates_token_count

            return LLMResponse(
                content=response.text,
                model=cfg.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

        except Exception as e:
            raise ExternalServiceError("Gemini API", str(e))


@lru_cache
def get_claude_service() -> ClaudeService:
    """Get singleton instance of Gemini service.

    Note: Function name is kept as get_claude_service for backward compatibility.

    Returns:
        ClaudeService instance (which now uses Gemini)
    """
    return ClaudeService()
