"""Markdown → HTML 変換ユーティリティ"""

import re


class MarkdownConverter:
    """Markdown to HTML converter

    シンプルなMarkdown構文をHTMLに変換します。
    本格的な変換が必要な場合は、python-markdownなどのライブラリを使用してください。
    """

    @staticmethod
    def convert(markdown: str) -> str:
        """MarkdownをHTMLに変換

        Args:
            markdown: Markdown形式のテキスト

        Returns:
            HTML形式のテキスト
        """
        html = markdown

        # 見出し（h6 → h1の順で処理）
        for i in range(6, 0, -1):
            pattern = rf"^{'#' * i}\s+(.+)$"
            replacement = rf"<h{i}>\1</h{i}>"
            html = re.sub(pattern, replacement, html, flags=re.MULTILINE)

        # 太字
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)

        # イタリック
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # インラインコード
        html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

        # リンク
        html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)

        # 改行を<br>に変換（2つ以上の改行は段落として扱う）
        html = re.sub(r"\n\n+", "</p><p>", html)
        html = f"<p>{html}</p>"

        return html


# シングルトンインスタンス
markdown_converter = MarkdownConverter()
