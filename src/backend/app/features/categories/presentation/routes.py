"""カテゴリAPIルート"""

from uuid import UUID

from fastapi import APIRouter, status

from app.features.categories.domain.models import Category
from app.features.categories.domain.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.features.categories.infrastructure.repository import CategoryRepository
from app.shared.domain.exceptions import NotFoundError
from app.shared.infrastructure.dependencies import DbSession

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: DbSession):
    """カテゴリ一覧取得"""
    repo = CategoryRepository(db)
    categories = await repo.find_all()
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: DbSession):
    """カテゴリ作成"""
    repo = CategoryRepository(db)
    category = Category(**data.model_dump())
    created = await repo.create(category)
    return created


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID, db: DbSession):
    """カテゴリ取得"""
    repo = CategoryRepository(db)
    category = await repo.find_by_id(category_id)
    if not category:
        raise NotFoundError("Category", str(category_id))
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: UUID, data: CategoryUpdate, db: DbSession):
    """カテゴリ更新"""
    repo = CategoryRepository(db)
    category = await repo.find_by_id(category_id)
    if not category:
        raise NotFoundError("Category", str(category_id))

    # 更新されたフィールドのみ適用
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    updated = await repo.update(category)
    return updated


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, db: DbSession):
    """カテゴリ削除"""
    repo = CategoryRepository(db)
    category = await repo.find_by_id(category_id)
    if not category:
        raise NotFoundError("Category", str(category_id))
    await repo.delete(category)
