"""Tests for article generator.

This module contains tests for the article generation orchestrator,
verifying the complete workflow from prompt building to database updates.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.features.articles.application.article_generator import (
    ArticleGenerator,
    GenerationResult,
)
from app.features.articles.domain.models import Article
from app.features.categories.domain.models import Category
from app.shared.domain.enums import ArticleStatus
from app.shared.domain.llm.base import LLMResponse


@pytest.fixture
def article_generator():
    """Create article generator instance."""
    return ArticleGenerator()


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = AsyncMock()
    db.flush = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def sample_article():
    """Create sample article."""
    article_id = uuid4()
    category_id = uuid4()

    article = Article(
        id=article_id,
        category_id=category_id,
        keyword="AI開発入門",
        status=ArticleStatus.PENDING
    )
    return article


@pytest.fixture
def sample_category():
    """Create sample category."""
    category = Category(
        id=uuid4(),
        name="AI開発",
        slug="ai-dev"
    )
    return category


@pytest.mark.asyncio
async def test_generate_article_not_found(article_generator, mock_db):
    """Test generation when article doesn't exist."""
    # Mock database to return None
    mock_db.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    )

    article_id = uuid4()
    result = await article_generator.generate(mock_db, article_id)

    assert result.success is False
    assert result.article_id == article_id
    assert "Article not found" in result.errors


@pytest.mark.asyncio
async def test_generate_successful(
    article_generator,
    mock_db,
    sample_article,
    sample_category
):
    """Test successful article generation."""
    # Mock database responses
    async def mock_execute(query):
        result = MagicMock()
        # First call: get article
        # Second call: get template (None)
        # Third call: get category
        if not hasattr(mock_execute, 'call_count'):
            mock_execute.call_count = 0

        mock_execute.call_count += 1

        if mock_execute.call_count == 1:
            result.scalar_one_or_none = MagicMock(return_value=sample_article)
        elif mock_execute.call_count == 2:
            result.scalar_one_or_none = MagicMock(return_value=None)
        else:
            result.scalar_one_or_none = MagicMock(return_value=sample_category)

        return result

    mock_db.execute = mock_execute

    # Mock Claude API response
    mock_llm_response = LLMResponse(
        content="# AI開発入門\n\nAI開発について解説します。" + "本文内容。" * 100,
        model="claude-sonnet-4-5",
        input_tokens=100,
        output_tokens=500
    )

    with patch.object(
        article_generator.claude_service,
        'generate',
        return_value=mock_llm_response
    ):
        result = await article_generator.generate(
            mock_db,
            sample_article.id,
            {"char_count_min": 100, "char_count_max": 2000}
        )

    assert result.success is True
    assert result.article_id == sample_article.id
    assert result.title == "AI開発入門"
    assert result.char_count > 0
    assert len(result.errors) == 0
    assert result.duration_ms > 0

    # Verify article was updated
    assert sample_article.title == "AI開発入門"
    assert sample_article.content is not None
    assert sample_article.status == ArticleStatus.REVIEW_PENDING


@pytest.mark.asyncio
async def test_generate_with_validation_errors(
    article_generator,
    mock_db,
    sample_article,
    sample_category
):
    """Test generation with validation errors (too short)."""
    async def mock_execute(query):
        result = MagicMock()
        if not hasattr(mock_execute, 'call_count'):
            mock_execute.call_count = 0

        mock_execute.call_count += 1

        if mock_execute.call_count == 1:
            result.scalar_one_or_none = MagicMock(return_value=sample_article)
        elif mock_execute.call_count == 2:
            result.scalar_one_or_none = MagicMock(return_value=None)
        else:
            result.scalar_one_or_none = MagicMock(return_value=sample_category)

        return result

    mock_db.execute = mock_execute

    # Mock Claude API response with short content
    mock_llm_response = LLMResponse(
        content="# タイトル\n\n短い内容",
        model="claude-sonnet-4-5",
        input_tokens=50,
        output_tokens=20
    )

    with patch.object(
        article_generator.claude_service,
        'generate',
        return_value=mock_llm_response
    ):
        result = await article_generator.generate(
            mock_db,
            sample_article.id,
            {"char_count_min": 1000, "char_count_max": 2000}
        )

    assert result.success is False
    assert len(result.errors) > 0
    assert sample_article.status == ArticleStatus.FAILED


@pytest.mark.asyncio
async def test_generate_handles_exception(
    article_generator,
    mock_db,
    sample_article
):
    """Test generation handles exceptions properly."""
    # Mock database to return article
    mock_db.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value=sample_article)
        )
    )

    # Mock Claude service to raise exception
    with patch.object(
        article_generator.claude_service,
        'generate',
        side_effect=Exception("API Error")
    ):
        result = await article_generator.generate(mock_db, sample_article.id)

    assert result.success is False
    assert "API Error" in result.errors
    assert sample_article.status == ArticleStatus.FAILED
