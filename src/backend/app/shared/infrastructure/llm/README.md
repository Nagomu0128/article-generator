# LLM Infrastructure

This module provides LLM (Large Language Model) service implementations for the article generator.

## Architecture

The LLM infrastructure follows Clean Architecture principles:

```
Domain Layer (shared/domain/llm/)
  └── base.py          - Abstract interfaces and data classes
Infrastructure Layer (shared/infrastructure/llm/)
  └── claude_service.py - Concrete Gemini API implementation
```

## Usage

### Basic Usage

```python
from app.shared.infrastructure.llm import get_claude_service

# Get service instance (now uses Gemini)
gemini = get_claude_service()

# Generate text
response = await gemini.generate(
    system_prompt="あなたは優秀なライターです",
    user_prompt="「AI」について100文字で説明してください"
)

print(response.content)
print(f"Tokens: {response.input_tokens} in, {response.output_tokens} out")
```

### Custom Configuration

```python
from app.shared.domain.llm import LLMConfig
from app.shared.infrastructure.llm import get_claude_service

# Create custom config
config = LLMConfig(
    model="gemini-1.5-pro",
    max_tokens=4096,
    temperature=0.5
)

# Use with service
gemini = get_claude_service()
response = await gemini.generate(
    system_prompt="システムプロンプト",
    user_prompt="ユーザープロンプト",
    config=config
)
```

## Features

- **Abstract Interface**: `BaseLLMService` allows different LLM providers
- **Automatic Retries**: Failed requests retry up to 3 times with exponential backoff
- **Error Handling**: API errors converted to `ExternalServiceError`
- **Type Safety**: Full type hints and Pydantic validation
- **Singleton Pattern**: Cached service instance via `@lru_cache`

## Testing

```bash
# Run unit tests only
pytest app/shared/infrastructure/llm/tests/ -m "not integration"

# Run all tests including integration tests (requires API key)
pytest app/shared/infrastructure/llm/tests/
```

## Configuration

Set the following environment variable:

```env
GOOGLE_API_KEY=your-google-api-key-here
```

## Implementation Details

### Retry Logic

- **Attempts**: 3 retries
- **Wait Strategy**: Exponential backoff (2s min, 30s max)
- **Handled Errors**: All exceptions from Gemini API

### Response Processing

Text content is extracted directly from the response:

```python
content = response.text
input_tokens = response.usage_metadata.prompt_token_count
output_tokens = response.usage_metadata.candidates_token_count
```

## Extending

To add a new LLM provider:

1. Create a new service class implementing `BaseLLMService`
2. Implement the `generate()` method
3. Add error handling and retry logic as needed

Example:

```python
from app.shared.domain.llm.base import BaseLLMService, LLMResponse

class NewLLMService(BaseLLMService):
    async def generate(self, system_prompt, user_prompt, config=None):
        # Implementation here
        return LLMResponse(...)
```
