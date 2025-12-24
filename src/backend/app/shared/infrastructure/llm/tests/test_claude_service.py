"""Tests for Claude service.

Note: These tests require a valid Anthropic API key in .env
Some tests are marked with pytest.mark.integration and can be skipped.
"""
import os

import pytest

from app.shared.domain.llm.base import LLMConfig
from app.shared.infrastructure.llm.claude_service import ClaudeService


class TestClaudeService:
    """Test cases for ClaudeService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ClaudeService()

    def test_initialization(self):
        """Test service initialization."""
        assert self.service.client is not None
        assert self.service.default_config is not None
        assert isinstance(self.service.default_config, LLMConfig)

    def test_default_config_values(self):
        """Test default configuration values."""
        config = self.service.default_config

        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tokens == 8192
        assert config.temperature == 0.7

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_simple(self):
        """Test simple text generation (integration test).

        This test requires a valid API key and makes a real API call.
        Skip with: pytest -m "not integration"
        """
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        system = "あなたは簡潔に答えるアシスタントです。"
        user = "「AI」を一言で説明してください。"

        response = await self.service.generate(system, user)

        assert response.content is not None
        assert len(response.content) > 0
        assert response.model is not None
        assert response.input_tokens > 0
        assert response.output_tokens > 0

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_generate_with_custom_config(self):
        """Test generation with custom config (integration test)."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        config = LLMConfig(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            temperature=0.5
        )

        system = "簡潔に答えてください。"
        user = "こんにちは"

        response = await self.service.generate(system, user, config)

        assert response.content is not None
        assert response.output_tokens <= 100

    def test_config_validation(self):
        """Test LLMConfig validation."""
        # Valid config
        config = LLMConfig(max_tokens=100, temperature=0.5)
        assert config.max_tokens == 100

        # Invalid max_tokens
        with pytest.raises(ValueError, match="max_tokens must be positive"):
            LLMConfig(max_tokens=0)

        # Invalid temperature (too low)
        with pytest.raises(ValueError, match="temperature must be between"):
            LLMConfig(temperature=-0.1)

        # Invalid temperature (too high)
        with pytest.raises(ValueError, match="temperature must be between"):
            LLMConfig(temperature=1.1)
