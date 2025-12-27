"""Prompt builder for article generation.

This module handles the construction of prompts for article generation,
including template variable substitution and default prompt provision.
"""
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Optional

from app.features.prompt_templates.domain.models import PromptTemplate


@dataclass
class BuiltPrompt:
    """Built prompt ready for LLM generation.

    Attributes:
        system_prompt: System-level instructions
        user_prompt: User's request with variables substituted
        variables: Dictionary of variables used in substitution
    """
    system_prompt: str
    user_prompt: str
    variables: dict[str, Any]


class PromptBuilder:
    """Builder for article generation prompts.

    This class constructs prompts from templates, substituting variables
    and providing sensible defaults when templates are not available.
    """

    # Default prompts used when no template is specified
    DEFAULT_SYSTEM = """あなたはSEOに強いWebライターです。高品質な記事を執筆してください。
- 見出し（h2, h3）を使って構造化
- 具体例を交えて説明
- 自然な日本語で読みやすく"""

    DEFAULT_USER = """「{keyword}」について記事を執筆してください。
【要件】文字数: {char_count_min}〜{char_count_max}文字、フォーマット: Markdown
【構成】タイトル（h1）、導入、本文（h2/h3）、まとめ"""

    # Default variable values
    DEFAULT_CHAR_COUNT_MIN = 3000
    DEFAULT_CHAR_COUNT_MAX = 4000

    def build(
        self,
        template: Optional[PromptTemplate],
        keyword: str,
        options: Optional[dict] = None
    ) -> BuiltPrompt:
        """Build a prompt from template and keyword.

        Args:
            template: Optional prompt template (uses defaults if None)
            keyword: Keyword/topic for article generation
            options: Optional additional variables for substitution

        Returns:
            BuiltPrompt with all variables substituted

        Examples:
            >>> builder = PromptBuilder()
            >>> prompt = builder.build(None, "AI", {"char_count_min": 2000})
            >>> print(prompt.user_prompt)
            「AI」について記事を執筆してください。...
        """
        # Initialize variables with defaults
        variables = {
            "keyword": keyword,
            "char_count_min": self.DEFAULT_CHAR_COUNT_MIN,
            "char_count_max": self.DEFAULT_CHAR_COUNT_MAX,
        }

        # Update with provided options
        if options:
            variables.update(options)

        # Use template if provided, otherwise use defaults
        system = (
            template.system_prompt if template
            else self.DEFAULT_SYSTEM
        )
        user_template = (
            template.user_prompt_template if template
            else self.DEFAULT_USER
        )

        # Substitute variables in user prompt
        user = self._substitute_variables(user_template, variables)

        return BuiltPrompt(
            system_prompt=system,
            user_prompt=user,
            variables=variables
        )

    def _substitute_variables(
        self,
        template: str,
        variables: dict[str, Any]
    ) -> str:
        """Substitute variables in template string.

        Variables are denoted by {variable_name} in the template.
        Missing variables are left unchanged.

        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variable values

        Returns:
            Template with variables substituted
        """
        def replace(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r"\{(\w+)\}", replace, template)


@lru_cache
def get_prompt_builder() -> PromptBuilder:
    """Get singleton instance of PromptBuilder.

    Returns:
        PromptBuilder instance
    """
    return PromptBuilder()
