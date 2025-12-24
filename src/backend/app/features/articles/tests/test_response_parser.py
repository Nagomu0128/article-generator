"""Tests for response parser."""
import pytest

from app.features.articles.application.response_parser import ResponseParser


class TestResponseParser:
    """Test cases for ResponseParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ResponseParser()

    def test_parse_valid_article(self):
        """Test parsing a valid article."""
        content = """# テスト記事

これはテスト記事です。

## セクション1

内容1

## セクション2

内容2
""" * 50  # Repeat to meet minimum char count

        result = self.parser.parse(content, min_chars=100, max_chars=10000)

        assert result.title == "テスト記事"
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.char_count > 100

    def test_parse_missing_title(self):
        """Test parsing article without title."""
        content = "これはタイトルのない記事です。" * 100

        result = self.parser.parse(content, min_chars=100, max_chars=10000)

        assert result.title == ""
        assert result.is_valid is False
        assert "タイトルが見つかりません" in result.errors

    def test_parse_too_short(self):
        """Test parsing article that's too short."""
        content = "# 短い記事\n\n短いです。"

        result = self.parser.parse(content, min_chars=100, max_chars=10000)

        assert result.is_valid is False
        assert any("文字数不足" in error for error in result.errors)

    def test_parse_too_long(self):
        """Test parsing article that's too long."""
        content = "# 長い記事\n\n" + "あ" * 10000

        result = self.parser.parse(content, min_chars=100, max_chars=1000)

        assert result.is_valid is False
        assert any("文字数超過" in error for error in result.errors)

    def test_clean_markdown_fences(self):
        """Test removing markdown code fences."""
        content = "```markdown\n# タイトル\n\n内容\n```"

        result = self.parser._clean_markdown_fences(content)

        assert result == "# タイトル\n\n内容"
        assert "```" not in result

    def test_extract_title(self):
        """Test title extraction."""
        content = "# メインタイトル\n\n## サブタイトル"

        result = self.parser._extract_title(content)

        assert result == "メインタイトル"

    def test_extract_title_not_found(self):
        """Test title extraction when no title present."""
        content = "タイトルなしのテキスト"

        result = self.parser._extract_title(content)

        assert result == ""

    def test_count_characters(self):
        """Test character counting."""
        content = "# タイトル\n\n**太字**と*斜体*と`コード`"

        result = self.parser._count_characters(content)

        # Markdown syntax should be removed for counting
        assert result > 0
        # Should not count markdown markers
        assert result < len(content)

    def test_validate_all_valid(self):
        """Test validation with valid content."""
        errors = self.parser._validate(
            title="タイトル",
            char_count=3000,
            min_chars=2000,
            max_chars=5000
        )

        assert len(errors) == 0

    def test_validate_multiple_errors(self):
        """Test validation with multiple errors."""
        errors = self.parser._validate(
            title="",
            char_count=100,
            min_chars=2000,
            max_chars=5000
        )

        assert len(errors) == 2
        assert "タイトルが見つかりません" in errors
        assert any("文字数不足" in error for error in errors)
