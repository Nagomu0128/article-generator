# タスク06: Claude API連携

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1時間 |
| 前提条件 | タスク03完了 |
| 成果物 | Claude サービス、プロンプトビルダー |

---

## 📝 実装ファイル

### backend/app/services/llm/base.py

```python
"""LLM 基底クラス"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int


@dataclass
class LLMConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 8192
    temperature: float = 0.7


class BaseLLMService(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        pass
```

### backend/app/services/llm/claude_service.py

```python
"""Claude API サービス"""
from typing import Optional
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.services.llm.base import BaseLLMService, LLMConfig, LLMResponse

settings = get_settings()


class ClaudeService(BaseLLMService):
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.default_config = LLMConfig()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def generate(self, system_prompt: str, user_prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        cfg = config or self.default_config
        try:
            response = await self.client.messages.create(
                model=cfg.model, max_tokens=cfg.max_tokens, temperature=cfg.temperature,
                system=system_prompt, messages=[{"role": "user", "content": user_prompt}]
            )
            content = "".join(b.text for b in response.content if b.type == "text")
            return LLMResponse(content=content, model=response.model, input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)
        except anthropic.APIError as e:
            raise ExternalServiceError("Claude API", str(e))


claude_service = ClaudeService()
```

### backend/app/services/prompts/prompt_builder.py

```python
"""プロンプトビルダー"""
import re
from dataclasses import dataclass
from typing import Any, Optional
from app.db.models import PromptTemplate


@dataclass
class BuiltPrompt:
    system_prompt: str
    user_prompt: str
    variables: dict[str, Any]


class PromptBuilder:
    DEFAULT_SYSTEM = """あなたはSEOに強いWebライターです。高品質な記事を執筆してください。
- 見出し（h2, h3）を使って構造化
- 具体例を交えて説明
- 自然な日本語で読みやすく"""

    DEFAULT_USER = """「{keyword}」について記事を執筆してください。
【要件】文字数: {char_count_min}〜{char_count_max}文字、フォーマット: Markdown
【構成】タイトル（h1）、導入、本文（h2/h3）、まとめ"""

    def build(self, template: Optional[PromptTemplate], keyword: str, options: Optional[dict] = None) -> BuiltPrompt:
        variables = {"keyword": keyword, "char_count_min": 3000, "char_count_max": 4000}
        if options:
            variables.update(options)

        system = template.system_prompt if template else self.DEFAULT_SYSTEM
        user_tpl = template.user_prompt_template if template else self.DEFAULT_USER
        user = re.sub(r"\{(\w+)\}", lambda m: str(variables.get(m.group(1), m.group(0))), user_tpl)
        return BuiltPrompt(system_prompt=system, user_prompt=user, variables=variables)


prompt_builder = PromptBuilder()
```

### backend/app/services/prompts/response_parser.py

```python
"""レスポンスパーサー"""
import re
from dataclasses import dataclass


@dataclass
class ParsedArticle:
    title: str
    content: str
    char_count: int
    is_valid: bool
    errors: list[str]


class ResponseParser:
    def parse(self, response: str, min_chars: int = 2000, max_chars: int = 6000) -> ParsedArticle:
        content = re.sub(r"^```(?:markdown)?\n?|```$", "", response, flags=re.MULTILINE).strip()
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ""

        plain = re.sub(r"^#+\s+", "", content, flags=re.MULTILINE)
        plain = re.sub(r"\*\*(.+?)\*\*", r"\1", plain)
        char_count = len(plain)

        errors = []
        if not title:
            errors.append("タイトルが見つかりません")
        if char_count < min_chars:
            errors.append(f"文字数不足: {char_count}/{min_chars}")

        return ParsedArticle(title=title, content=content, char_count=char_count, is_valid=len(errors) == 0, errors=errors)


response_parser = ResponseParser()
```

---

## ✅ 完了条件

```python
# Claude API の動作確認（Python REPL）
from app.services.llm.claude_service import claude_service
import asyncio

async def test():
    response = await claude_service.generate(
        "あなたは優秀なライターです",
        "「AI」について100文字で説明してください"
    )
    print(response.content)

asyncio.run(test())
```

---

## 📌 次のタスク

タスク06完了後、**タスク07: 記事生成パイプライン** に進んでください。
