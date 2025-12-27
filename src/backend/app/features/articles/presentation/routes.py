"""記事APIルート"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from sqlalchemy import select

from app.features.articles.domain.models import Article
from app.features.articles.domain.schemas import (
    ArticleCreate,
    ArticleListResponse,
    ArticleResponse,
    ArticleUpdate,
)
from app.features.articles.infrastructure.repository import ArticleRepository
from app.features.categories.domain.models import Category
from app.features.categories.infrastructure.repository import CategoryRepository
from app.features.sheets.infrastructure.google_sheets_service import sheets_service
from app.shared.domain.enums import ArticleStatus
from app.shared.domain.exceptions import NotFoundError, ValidationError
from app.shared.infrastructure.dependencies import DbSession, Pagination

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    db: DbSession,
    pagination: Pagination,
    category_id: Optional[UUID] = Query(None, description="カテゴリIDでフィルタ"),
    status: Optional[ArticleStatus] = Query(None, description="ステータスでフィルタ"),
):
    """記事一覧取得"""
    repo = ArticleRepository(db)
    articles, total = await repo.find_all(
        category_id=category_id,
        status=status,
        offset=pagination.offset,
        limit=pagination.per_page,
    )

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in articles],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(data: ArticleCreate, db: DbSession):
    """記事作成"""
    # カテゴリ存在確認
    category_repo = CategoryRepository(db)
    category = await category_repo.find_by_id(data.category_id)
    if not category:
        raise NotFoundError("Category", str(data.category_id))

    # 記事作成
    article_repo = ArticleRepository(db)
    article = Article(**data.model_dump())
    created = await article_repo.create(article)
    return created


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: UUID, db: DbSession):
    """記事取得"""
    repo = ArticleRepository(db)
    article = await repo.find_by_id(article_id)
    if not article:
        raise NotFoundError("Article", str(article_id))
    return article


@router.patch("/{article_id}", response_model=ArticleResponse)
async def update_article(article_id: UUID, data: ArticleUpdate, db: DbSession):
    """記事更新"""
    repo = ArticleRepository(db)
    article = await repo.find_by_id(article_id)
    if not article:
        raise NotFoundError("Article", str(article_id))

    # 更新されたフィールドのみ適用
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)

    updated = await repo.update(article)

    # Google Sheetsに同期
    await _sync_to_sheets(db, updated)

    return updated


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(article_id: UUID, db: DbSession):
    """記事削除"""
    repo = ArticleRepository(db)
    article = await repo.find_by_id(article_id)
    if not article:
        raise NotFoundError("Article", str(article_id))
    await repo.delete(article)


async def _sync_to_sheets(db: DbSession, article: Article) -> None:
    """Google Sheetsに記事ステータスを同期

    Args:
        db: データベースセッション
        article: 同期する記事

    Note:
        エラーは無視して処理を継続
    """
    try:
        # カテゴリを取得してsheet_idを確認
        result = await db.execute(
            select(Category).where(Category.id == article.category_id)
        )
        category = result.scalar_one_or_none()

        if category and category.sheet_id:
            sheets_service.update_article_status(
                category.sheet_id,
                article.keyword,
                article.status,
                article.title,
                article.wp_url,
                article.wp_post_id
            )
    except Exception:
        # Sheetsのエラーは無視して処理を継続
        pass
