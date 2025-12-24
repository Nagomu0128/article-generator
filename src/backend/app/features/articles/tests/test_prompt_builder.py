"""Tests for prompt builder."""
import pytest

from app.features.articles.application.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """Test cases for PromptBuilder."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = PromptBuilder()

    def test_build_with_defaults(self):
        """Test building prompt with default template."""
        result = self.builder.build(None, "AI")

        assert result.system_prompt == self.builder.DEFAULT_SYSTEM
        assert "AI" in result.user_prompt
        assert result.variables["keyword"] == "AI"
        assert result.variables["char_count_min"] == 3000
        assert result.variables["char_count_max"] == 4000

    def test_build_with_custom_options(self):
        """Test building prompt with custom options."""
        result = self.builder.build(
            None,
            "機械学習",
            {"char_count_min": 2000, "char_count_max": 3000}
        )

        assert "機械学習" in result.user_prompt
        assert "2000" in result.user_prompt
        assert "3000" in result.user_prompt
        assert result.variables["char_count_min"] == 2000

    def test_substitute_variables(self):
        """Test variable substitution."""
        template = "Hello {name}, you are {age} years old"
        variables = {"name": "Alice", "age": 30}

        result = self.builder._substitute_variables(template, variables)

        assert result == "Hello Alice, you are 30 years old"

    def test_substitute_missing_variables(self):
        """Test substitution with missing variables."""
        template = "Hello {name}, you are {age} years old"
        variables = {"name": "Bob"}

        result = self.builder._substitute_variables(template, variables)

        assert result == "Hello Bob, you are {age} years old"

    def test_substitute_no_variables(self):
        """Test substitution with no placeholders."""
        template = "Hello world"
        variables = {"name": "Charlie"}

        result = self.builder._substitute_variables(template, variables)

        assert result == "Hello world"
