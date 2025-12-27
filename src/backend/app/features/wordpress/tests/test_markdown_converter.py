"""Markdown変換ユーティリティのテスト"""

import pytest

from app.shared.infrastructure.services.markdown_converter import markdown_converter


class TestMarkdownConverter:
    """MarkdownConverterのテスト"""

    def test_convert_headings(self):
        """見出しの変換をテスト"""
        markdown = "# H1\n## H2\n### H3"
        result = markdown_converter.convert(markdown)

        assert "<h1>H1</h1>" in result
        assert "<h2>H2</h2>" in result
        assert "<h3>H3</h3>" in result

    def test_convert_bold(self):
        """太字の変換をテスト"""
        markdown = "This is **bold** text"
        result = markdown_converter.convert(markdown)

        assert "<strong>bold</strong>" in result

    def test_convert_italic(self):
        """イタリックの変換をテスト"""
        markdown = "This is *italic* text"
        result = markdown_converter.convert(markdown)

        assert "<em>italic</em>" in result

    def test_convert_code(self):
        """インラインコードの変換をテスト"""
        markdown = "Use `code` here"
        result = markdown_converter.convert(markdown)

        assert "<code>code</code>" in result

    def test_convert_link(self):
        """リンクの変換をテスト"""
        markdown = "Visit [Google](https://google.com)"
        result = markdown_converter.convert(markdown)

        assert '<a href="https://google.com">Google</a>' in result

    def test_convert_complex(self):
        """複雑なMarkdownの変換をテスト"""
        markdown = """# タイトル

これは**太字**と*イタリック*を含む段落です。

## サブタイトル

[リンク](https://example.com)と`コード`も含みます。"""

        result = markdown_converter.convert(markdown)

        # 基本的な要素が含まれることを確認
        assert "<h1>タイトル</h1>" in result
        assert "<h2>サブタイトル</h2>" in result
        assert "<strong>太字</strong>" in result
        assert "<em>イタリック</em>" in result
        assert "<code>コード</code>" in result
        assert '<a href="https://example.com">リンク</a>' in result
