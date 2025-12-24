# Article Application Layer

This module contains the application logic for article generation, including prompt building and response parsing.

## Components

### PromptBuilder

Constructs prompts for LLM article generation with variable substitution.

**Usage:**

```python
from app.features.articles.application import get_prompt_builder
from app.features.prompt_templates.domain.models import PromptTemplate

builder = get_prompt_builder()

# Build with default template
prompt = builder.build(None, keyword="AI")

# Build with custom template
template = PromptTemplate(
    system_prompt="カスタムシステムプロンプト",
    user_prompt_template="「{keyword}」について{char_count_min}文字で書いてください"
)
prompt = builder.build(template, keyword="機械学習", options={"char_count_min": 2000})

# Use the built prompt
print(prompt.system_prompt)
print(prompt.user_prompt)
print(prompt.variables)
```

**Features:**

- Default prompts when no template provided
- Variable substitution with `{variable_name}` syntax
- Custom options override default values
- Type-safe with dataclasses

### ResponseParser

Parses and validates LLM responses into structured article data.

**Usage:**

```python
from app.features.articles.application import get_response_parser

parser = get_response_parser()

# Parse LLM response
llm_response = "# AI入門\n\nAIとは...\n\n## 基礎知識\n\n..."
result = parser.parse(llm_response, min_chars=2000, max_chars=5000)

# Check validation
if result.is_valid:
    print(f"Title: {result.title}")
    print(f"Characters: {result.char_count}")
    print(f"Content: {result.content[:100]}...")
else:
    print(f"Validation errors: {result.errors}")
```

**Features:**

- Markdown fence removal (``` markers)
- Title extraction from h1 headings
- Character counting (excluding markup)
- Validation against min/max requirements
- Detailed error messages

## Workflow

Typical article generation workflow:

```python
from app.shared.infrastructure.llm import get_claude_service
from app.features.articles.application import (
    get_prompt_builder,
    get_response_parser
)

# 1. Build prompt
builder = get_prompt_builder()
prompt = builder.build(None, keyword="機械学習", options={
    "char_count_min": 3000,
    "char_count_max": 4000
})

# 2. Generate with LLM
claude = get_claude_service()
llm_response = await claude.generate(
    prompt.system_prompt,
    prompt.user_prompt
)

# 3. Parse and validate
parser = get_response_parser()
article = parser.parse(
    llm_response.content,
    min_chars=prompt.variables["char_count_min"],
    max_chars=prompt.variables["char_count_max"]
)

# 4. Use result
if article.is_valid:
    # Save to database
    save_article(
        title=article.title,
        content=article.content,
        metadata={
            "char_count": article.char_count,
            "tokens": {
                "input": llm_response.input_tokens,
                "output": llm_response.output_tokens
            }
        }
    )
else:
    print(f"Generation failed: {article.errors}")
```

## Testing

```bash
# Run application layer tests
pytest app/features/articles/tests/
```

## Default Values

### PromptBuilder Defaults

- `DEFAULT_SYSTEM`: SEO-focused web writer prompt
- `DEFAULT_USER`: Article writing request template
- `DEFAULT_CHAR_COUNT_MIN`: 3000
- `DEFAULT_CHAR_COUNT_MAX`: 4000

### ResponseParser Defaults

- `DEFAULT_MIN_CHARS`: 2000
- `DEFAULT_MAX_CHARS`: 6000

## Validation Rules

The ResponseParser validates:

1. **Title presence**: Article must have an h1 heading
2. **Minimum length**: Content must meet minimum character count
3. **Maximum length**: Content must not exceed maximum character count

All validation errors are collected and returned in `ParsedArticle.errors`.
