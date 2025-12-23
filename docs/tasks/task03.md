# タスク03: FastAPI基本構造

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1時間 |
| 前提条件 | タスク02完了 |
| 成果物 | カテゴリ・記事の CRUD API |

---

## 📝 実装ファイル

### backend/app/core/exceptions.py

```python
"""カスタム例外"""
from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, resource: str, id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found: {id}")


class ConflictError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class ExternalServiceError(HTTPException):
    def __init__(self, service: str, message: str):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"{service}: {message}")
```

### backend/app/core/dependencies.py

```python
"""依存関係"""
from typing import Annotated
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
    ):
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page


Pagination = Annotated[PaginationParams, Depends()]
```

### backend/app/api/categories.py

```python
"""カテゴリ API"""
from uuid import UUID
from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.core.dependencies import DbSession
from app.core.exceptions import ConflictError, NotFoundError
from app.db.models import Category
from app.models.schemas import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: DbSession):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: DbSession):
    category = Category(**data.model_dump())
    db.add(category)
    try:
        await db.flush()
    except IntegrityError:
        raise ConflictError(f"Category already exists: {data.name}")
    await db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID, db: DbSession):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise NotFoundError("Category", str(category_id))
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, db: DbSession):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise NotFoundError("Category", str(category_id))
    await db.delete(category)
```

### backend/app/api/articles.py

```python
"""記事 API"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Query, status
from sqlalchemy import func, select
from app.core.dependencies import DbSession, Pagination
from app.core.exceptions import NotFoundError
from app.db.models import Article, ArticleStatus, Category
from app.models.schemas import ArticleCreate, ArticleListResponse, ArticleResponse

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    db: DbSession,
    pagination: Pagination,
    category_id: Optional[UUID] = None,
    status: Optional[ArticleStatus] = None,
):
    query = select(Article)
    count_query = select(func.count(Article.id))

    if category_id:
        query = query.where(Article.category_id == category_id)
        count_query = count_query.where(Article.category_id == category_id)
    if status:
        query = query.where(Article.status == status)
        count_query = count_query.where(Article.status == status)

    total = (await db.execute(count_query)).scalar()
    query = query.order_by(Article.created_at.desc()).offset(pagination.offset).limit(pagination.per_page)
    articles = (await db.execute(query)).scalars().all()

    return ArticleListResponse(
        items=[ArticleResponse.model_validate(a) for a in articles],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(data: ArticleCreate, db: DbSession):
    category = (await db.execute(select(Category).where(Category.id == data.category_id))).scalar_one_or_none()
    if not category:
        raise NotFoundError("Category", str(data.category_id))
    article = Article(**data.model_dump())
    db.add(article)
    await db.flush()
    await db.refresh(article)
    return article


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: UUID, db: DbSession):
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise NotFoundError("Article", str(article_id))
    return article
```

### backend/app/api/__init__.py

```python
"""API ルーター集約"""
from fastapi import APIRouter
from app.api.articles import router as articles_router
from app.api.categories import router as categories_router

api_router = APIRouter(prefix="/api")
api_router.include_router(categories_router)
api_router.include_router(articles_router)
```

### backend/app/main.py（更新）

```python
from app.api import api_router
# ... 既存コード ...
app.include_router(api_router)
```

---

## ✅ 完了条件

```bash
# API ドキュメント確認
# http://localhost:8000/docs

# カテゴリ作成
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name":"AI開発","slug":"ai-dev"}'

# 記事作成
curl -X POST http://localhost:8000/api/articles \
  -H "Content-Type: application/json" \
  -d '{"category_id":"<カテゴリID>","keyword":"RAG"}'
```

---

## 📌 次のタスク

タスク03完了後、以下のタスクに並行して進めます:
- **タスク04: Google Sheets連携**
- **タスク05: WordPress連携**
- **タスク06: Claude API連携**
