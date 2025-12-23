"""カテゴリリポジトリ"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.categories.domain.models import Category
from app.shared.domain.exceptions import ConflictError, NotFoundError


class CategoryRepository:
    """カテゴリリポジトリ"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_all(self) -> list[Category]:
        """全カテゴリ取得"""
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def find_by_id(self, category_id: UUID) -> Optional[Category]:
        """IDでカテゴリ取得"""
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def find_by_slug(self, slug: str) -> Optional[Category]:
        """スラッグでカテゴリ取得"""
        result = await self.session.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create(self, category: Category) -> Category:
        """カテゴリ作成"""
        self.session.add(category)
        try:
            await self.session.flush()
            await self.session.refresh(category)
            return category
        except IntegrityError as e:
            raise ConflictError(f"Category already exists: {category.name}")

    async def update(self, category: Category) -> Category:
        """カテゴリ更新"""
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        """カテゴリ削除"""
        await self.session.delete(category)
        await self.session.flush()
