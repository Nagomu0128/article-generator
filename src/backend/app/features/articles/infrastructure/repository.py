"""記事リポジトリ"""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.articles.domain.models import Article
from app.shared.domain.enums import ArticleStatus


class ArticleRepository:
    """記事リポジトリ"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_all(
        self,
        category_id: Optional[UUID] = None,
        status: Optional[ArticleStatus] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Article], int]:
        """記事一覧取得（フィルタ・ページネーション対応）"""
        query = select(Article)
        count_query = select(func.count(Article.id))

        # フィルタ適用
        if category_id:
            query = query.where(Article.category_id == category_id)
            count_query = count_query.where(Article.category_id == category_id)
        if status:
            query = query.where(Article.status == status)
            count_query = count_query.where(Article.status == status)

        # 総数取得
        total = (await self.session.execute(count_query)).scalar()

        # ページネーション適用
        query = (
            query.order_by(Article.created_at.desc()).offset(offset).limit(limit)
        )
        result = await self.session.execute(query)
        articles = list(result.scalars().all())

        return articles, total

    async def find_by_id(self, article_id: UUID) -> Optional[Article]:
        """IDで記事取得"""
        result = await self.session.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()

    async def create(self, article: Article) -> Article:
        """記事作成"""
        self.session.add(article)
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def update(self, article: Article) -> Article:
        """記事更新"""
        await self.session.flush()
        await self.session.refresh(article)
        return article

    async def delete(self, article: Article) -> None:
        """記事削除"""
        await self.session.delete(article)
        await self.session.flush()
