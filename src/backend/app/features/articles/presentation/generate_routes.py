"""Article generation API routes.

This module provides endpoints for generating article content
using Claude API, including single generation and regeneration.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, status

from app.features.articles.application.article_generator import get_article_generator
from app.features.articles.domain.schemas import GenerateRequest, GenerateResponse
from app.shared.infrastructure.dependencies import DbSession

router = APIRouter(prefix="/generate", tags=["Generation"])


@router.post("", response_model=GenerateResponse, status_code=status.HTTP_200_OK)
async def generate_article(data: GenerateRequest, db: DbSession):
    """
    記事を生成する

    Claude APIを使用して記事のコンテンツを生成します。
    生成された記事は自動的にデータベースに保存され、
    Google Sheetsにも同期されます（設定されている場合）。

    Args:
        data: 生成リクエスト（article_id、options）
        db: データベースセッション

    Returns:
        生成結果（タイトル、文字数、エラーなど）

    Example:
        POST /api/generate
        {
            "article_id": "123e4567-e89b-12d3-a456-426614174000",
            "options": {
                "temperature": 0.8,
                "char_count_min": 2000,
                "char_count_max": 4000
            }
        }
    """
    generator = get_article_generator()
    result = await generator.generate(db, data.article_id, data.options)

    return GenerateResponse(
        success=result.success,
        article_id=result.article_id,
        title=result.title,
        char_count=result.char_count,
        errors=result.errors,
        duration_ms=result.duration_ms
    )


@router.post(
    "/regenerate/{article_id}",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK
)
async def regenerate_article(
    article_id: UUID,
    db: DbSession,
    options: Optional[dict] = None
):
    """
    記事を再生成する

    既存の記事を再度生成します。前回の内容は上書きされます。
    パスパラメータで記事IDを指定できるため、
    URLから直接呼び出すことが可能です。

    Args:
        article_id: 記事ID（パスパラメータ）
        db: データベースセッション
        options: 生成オプション（クエリパラメータ、省略可）

    Returns:
        生成結果

    Example:
        POST /api/generate/regenerate/123e4567-e89b-12d3-a456-426614174000
        {
            "temperature": 0.7,
            "char_count_min": 3000
        }
    """
    generator = get_article_generator()
    result = await generator.generate(db, article_id, options)

    return GenerateResponse(
        success=result.success,
        article_id=result.article_id,
        title=result.title,
        char_count=result.char_count,
        errors=result.errors,
        duration_ms=result.duration_ms
    )
