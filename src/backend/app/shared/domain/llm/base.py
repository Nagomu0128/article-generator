"""LLM base classes and interfaces.

This module defines the domain-level abstractions for LLM services,
following Clean Architecture principles. The domain layer does not
depend on any infrastructure details.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Response from LLM service.

    Attributes:
        content: Generated text content
        model: Model identifier used for generation
        input_tokens: Number of tokens in the input
        output_tokens: Number of tokens in the output
    """
    content: str
    model: str
    input_tokens: int
    output_tokens: int


@dataclass
class LLMConfig:
    """Configuration for LLM generation.

    Attributes:
        model: Model identifier to use
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
    """
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 8192
    temperature: float = 0.7

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")


class BaseLLMService(ABC):
    """Abstract base class for LLM services.

    This interface defines the contract for LLM implementations,
    allowing different LLM providers to be used interchangeably.
    """

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Generate text using the LLM.

        Args:
            system_prompt: System-level instructions
            user_prompt: User's input/request
            config: Optional configuration for generation

        Returns:
            LLMResponse containing generated content and metadata

        Raises:
            ExternalServiceError: If LLM service fails
        """
        pass
