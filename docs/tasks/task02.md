# タスク02: データベース設計

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1時間 |
| 前提条件 | タスク01完了 |
| 成果物 | SQLAlchemy モデル、Alembic マイグレーション |

---

## 📊 ER図

```
CATEGORY ||--o{ PROMPT_TEMPLATE : "has many"
CATEGORY ||--o{ ARTICLE : "contains"
PROMPT_TEMPLATE ||--o{ ARTICLE : "generates"
ARTICLE ||--o{ JOB_LOG : "has history"
```

---

## 📝 実装ファイル

### backend/app/db/database.py

```python
"""データベース接続"""
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.async_database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### backend/app/db/models.py

```python
"""SQLAlchemy モデル"""
import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class ArticleStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    FAILED = "failed"
    REVIEW_PENDING = "review_pending"
    REVIEWED = "reviewed"
    PUBLISHED = "published"


class JobType(str, enum.Enum):
    GENERATE = "generate"
    PUBLISH = "publish"
    SYNC_SHEETS = "sync_sheets"


class JobStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    sheet_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sheet_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sheets_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    prompt_templates: Mapped[list["PromptTemplate"]] = relationship(back_populates="category", cascade="all, delete-orphan")
    articles: Mapped[list["Article"]] = relationship(back_populates="category")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    options: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    category: Mapped["Category"] = relationship(back_populates="prompt_templates")
    articles: Mapped[list["Article"]] = relationship(back_populates="prompt_template")


class Article(Base):
    __tablename__ = "articles"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    prompt_template_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("prompt_templates.id", ondelete="SET NULL"), nullable=True)
    keyword: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ArticleStatus] = mapped_column(Enum(ArticleStatus), default=ArticleStatus.PENDING)
    wp_post_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wp_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    wp_published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    category: Mapped["Category"] = relationship(back_populates="articles")
    prompt_template: Mapped[Optional["PromptTemplate"]] = relationship(back_populates="articles")
    job_logs: Mapped[list["JobLog"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class JobLog(Base):
    __tablename__ = "job_logs"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    article_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    job_type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    article: Mapped["Article"] = relationship(back_populates="job_logs")
```

### backend/app/models/schemas.py

```python
"""Pydantic スキーマ"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.db.models import ArticleStatus, JobStatus, JobType


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    sheet_id: Optional[str] = None
    sheet_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ArticleCreate(BaseModel):
    category_id: UUID
    keyword: str = Field(..., min_length=1, max_length=200)


class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    category_id: UUID
    keyword: str
    title: Optional[str] = None
    content: Optional[str] = None
    status: ArticleStatus
    wp_post_id: Optional[int] = None
    wp_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int
    per_page: int
```

### Alembic 設定

```bash
cd backend
alembic init alembic
```

**backend/alembic/env.py** の修正:

```python
from app.core.config import get_settings
from app.db.database import Base
from app.db.models import Category, PromptTemplate, Article, JobLog  # noqa

settings = get_settings()
target_metadata = Base.metadata

def get_url():
    return settings.async_database_url
```

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## ✅ 完了条件

```bash
# マイグレーション成功
alembic upgrade head

# テーブル確認
docker compose exec db psql -U postgres -d article_generator -c "\dt"
# categories, prompt_templates, articles, job_logs が表示
```

---

## 📌 次のタスク

タスク02完了後、**タスク03: FastAPI基本構造** に進んでください。
