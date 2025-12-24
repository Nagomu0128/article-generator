"""Response parser for article generation.

This module parses LLM responses into structured article data,
validating content and extracting metadata.
"""
import re
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class ParsedArticle:
    """Parsed article from LLM response.

    Attributes:
        title: Extracted article title
        content: Full article content (Markdown)
        char_count: Character count (excluding markup)
        is_valid: Whether the article meets validation criteria
        errors: List of validation error messages
    """
    title: str
    content: str
    char_count: int
    is_valid: bool
    errors: list[str]


class ResponseParser:
    """Parser for article generation responses.

    This class parses and validates LLM-generated articles,
    extracting titles, counting characters, and checking
    against specified criteria.
    """

    # Default validation thresholds
    DEFAULT_MIN_CHARS = 2000
    DEFAULT_MAX_CHARS = 6000

    def parse(
        self,
        response: str,
        min_chars: int = DEFAULT_MIN_CHARS,
        max_chars: int = DEFAULT_MAX_CHARS
    ) -> ParsedArticle:
        """Parse and validate LLM response.

        Args:
            response: Raw response from LLM
            min_chars: Minimum required character count
            max_chars: Maximum allowed character count

        Returns:
            ParsedArticle with validation results

        Examples:
            >>> parser = ResponseParser()
            >>> result = parser.parse("# AI入門\\n\\n本文...", 100, 1000)
            >>> print(result.title)
            AI入門
        """
        # Remove markdown code block markers
        content = self._clean_markdown_fences(response)

        # Extract title
        title = self._extract_title(content)

        # Calculate character count
        char_count = self._count_characters(content)

        # Validate content
        errors = self._validate(title, char_count, min_chars, max_chars)

        return ParsedArticle(
            title=title,
            content=content,
            char_count=char_count,
            is_valid=len(errors) == 0,
            errors=errors
        )

    def _clean_markdown_fences(self, text: str) -> str:
        """Remove markdown code block fences.

        Args:
            text: Text possibly containing ```markdown``` fences

        Returns:
            Text with fences removed
        """
        # Remove opening and closing markdown fences
        cleaned = re.sub(
            r"^```(?:markdown)?\n?",
            "",
            text,
            flags=re.MULTILINE
        )
        cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE)
        return cleaned.strip()

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content.

        Looks for the first h1 heading (# Title).

        Args:
            content: Markdown content

        Returns:
            Extracted title or empty string if not found
        """
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else ""

    def _count_characters(self, content: str) -> int:
        """Count characters excluding markdown syntax.

        Removes headings markers, bold/italic markers to get
        approximate plain text character count.

        Args:
            content: Markdown content

        Returns:
            Approximate character count
        """
        # Remove heading markers
        plain = re.sub(r"^#+\s+", "", content, flags=re.MULTILINE)

        # Remove bold markers
        plain = re.sub(r"\*\*(.+?)\*\*", r"\1", plain)

        # Remove italic markers
        plain = re.sub(r"\*(.+?)\*", r"\1", plain)

        # Remove inline code markers
        plain = re.sub(r"`(.+?)`", r"\1", plain)

        return len(plain)

    def _validate(
        self,
        title: str,
        char_count: int,
        min_chars: int,
        max_chars: int
    ) -> list[str]:
        """Validate parsed article content.

        Args:
            title: Extracted title
            char_count: Character count
            min_chars: Minimum required characters
            max_chars: Maximum allowed characters

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if not title:
            errors.append("タイトルが見つかりません")

        if char_count < min_chars:
            errors.append(f"文字数不足: {char_count}/{min_chars}")

        if char_count > max_chars:
            errors.append(f"文字数超過: {char_count}/{max_chars}")

        return errors


@lru_cache
def get_response_parser() -> ResponseParser:
    """Get singleton instance of ResponseParser.

    Returns:
        ResponseParser instance
    """
    return ResponseParser()
