# 記事自動生成システム 完全実装ガイド

## 📚 目次

1. [概要](#概要)
2. [タスク00: 事前準備（人間作業）](#タスク00-事前準備人間作業)
3. [タスク01: プロジェクト初期化](#タスク01-プロジェクト初期化)
4. [タスク02: データベース設計](#タスク02-データベース設計)
5. [タスク03: FastAPI基本構造](#タスク03-fastapi基本構造)
6. [タスク04: Google Sheets連携](#タスク04-google-sheets連携)
7. [タスク05: WordPress連携](#タスク05-wordpress連携)
8. [タスク06: Claude API連携](#タスク06-claude-api連携)
9. [タスク07: 記事生成パイプライン](#タスク07-記事生成パイプライン)
10. [タスク08: バッチ処理実装](#タスク08-バッチ処理実装)
11. [タスク09: フロントエンド実装](#タスク09-フロントエンド実装)
12. [タスク10: 結合テスト・デプロイ](#タスク10-結合テストデプロイ)

---

## 概要

### システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                    記事自動生成システム                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js)  ←→  Backend (FastAPI)  ←→  PostgreSQL  │
│                              ↓                              │
│              ┌───────────────┼───────────────┐              │
│              ↓               ↓               ↓              │
│        Claude API    Google Sheets    WordPress             │
└─────────────────────────────────────────────────────────────┘
```

### タスク依存関係

```mermaid
flowchart TB
    T00[00: 事前準備<br/>👤 人間] --> T01[01: プロジェクト初期化<br/>🤖 AI]
    T01 --> T02[02: データベース<br/>🤖 AI]
    T02 --> T03[03: FastAPI基本<br/>🤖 AI]
    T03 --> T04[04: Google Sheets<br/>🤖 AI]
    T03 --> T05[05: WordPress<br/>🤖 AI]
    T03 --> T06[06: Claude API<br/>🤖 AI]
    T04 --> T07[07: 記事生成PL<br/>🤖 AI]
    T05 --> T07
    T06 --> T07
    T07 --> T08[08: バッチ処理<br/>🤖 AI]
    T08 --> T09[09: フロントエンド<br/>🤖 AI]
    T09 --> T10[10: 結合・デプロイ<br/>🤖 + 👤]
```

### 所要時間目安

| タスク | 担当 | 時間 |
|--------|------|------|
| 00: 事前準備 | 👤 人間 | 1-2時間 |
| 01: プロジェクト初期化 | 🤖 AI | 30分 |
| 02: データベース | 🤖 AI | 1時間 |
| 03: FastAPI基本 | 🤖 AI | 1時間 |
| 04: Google Sheets | 🤖 AI | 1時間 |
| 05: WordPress | 🤖 AI | 1時間 |
| 06: Claude API | 🤖 AI | 1時間 |
| 07: 記事生成PL | 🤖 AI | 2時間 |
| 08: バッチ処理 | 🤖 AI | 1.5時間 |
| 09: フロントエンド | 🤖 AI | 3時間 |
| 10: 結合・デプロイ | 🤖+👤 | 2時間 |
| **合計** | | **約15-17時間** |

---

# タスク00: 事前準備（人間作業）

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 👤 人間（あなた） |
| 所要時間 | 1-2時間 |
| 前提条件 | なし |
| 成果物 | `.env` ファイルに記載する各種認証情報 |

---

## 🔑 1. Anthropic API キーの取得

### 手順

1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウントを作成またはログイン
3. 左メニューから「API Keys」を選択
4. 「Create Key」をクリック
5. キー名を入力（例：`article-generator`）
6. 生成されたキーをコピー

### 取得する値

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🌐 2. WordPress 設定

### 2.1 アプリケーションパスワードの作成

1. WordPress 管理画面にログイン
2. 「ユーザー」→「プロフィール」に移動
3. ページ下部の「アプリケーションパスワード」セクションを探す
4. 「新しいアプリケーションパスワードの名前」に `article-generator` と入力
5. 「新しいアプリケーションパスワードを追加」をクリック
6. 表示されたパスワードをコピー

### 2.2 REST API の動作確認

```bash
curl https://your-site.com/wp-json/wp/v2/posts
```

### 取得する値

```
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your-admin-username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

---

## 📊 3. Google Cloud / Sheets API 設定

### 3.1 プロジェクト作成と API 有効化

1. [Google Cloud Console](https://console.cloud.google.com/) で新しいプロジェクトを作成
2. 以下の API を有効化:
   - Google Sheets API
   - Google Drive API

### 3.2 サービスアカウントの作成

1. 「API とサービス」→「認証情報」→「認証情報を作成」→「サービスアカウント」
2. サービスアカウント名：`article-generator-sa`
3. 「キー」タブ →「鍵を追加」→「新しい鍵を作成」→ JSON
4. ダウンロードした JSON を1行にして環境変数に設定

### 取得する値

```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key":"..."}
```

---

## 📝 4. 環境変数ファイルの作成

以下の内容で `.env.example` ファイルを作成:

```env
# ===========================================
# 記事自動生成システム 環境変数
# ===========================================

# ----- Anthropic (Claude API) -----
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# ----- WordPress -----
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# ----- Google Sheets -----
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# ----- Database -----
DATABASE_URL=postgresql://postgres:postgres@db:5432/article_generator

# ----- Redis -----
REDIS_URL=redis://redis:6379

# ----- Application -----
APP_ENV=development
DEBUG=true
SECRET_KEY=your-random-secret-key-at-least-32-chars
FRONTEND_URL=http://localhost:3000
```

---

## ✅ 完了チェックリスト

- [ ] Anthropic API キーを取得した
- [ ] WordPress アプリケーションパスワードを作成した
- [ ] Google Cloud プロジェクトを作成し、API を有効化した
- [ ] サービスアカウントを作成し、JSON キーをダウンロードした
- [ ] `.env.example` ファイルを作成した

---

# タスク01: プロジェクト初期化

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 30分 |
| 前提条件 | タスク00完了 |
| 成果物 | プロジェクトディレクトリ構造、Docker設定 |

---

## 🎯 ゴール

1. モノレポ構造のプロジェクトディレクトリを作成
2. バックエンド（Python/FastAPI）の依存関係を設定
3. フロントエンド（Next.js/TypeScript）の依存関係を設定
4. Docker Compose による開発環境を構築

---

## 📁 作成するディレクトリ構造

```
article-generator/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── db/
│   │   └── core/
│   │       └── config.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── (Next.js project)
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 📝 実装ファイル

### backend/requirements.txt

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Redis / Task Queue
redis==5.0.1
arq==0.25.0

# External APIs
anthropic==0.18.1
gspread==6.0.2
google-auth==2.27.0
httpx==0.26.0

# Validation & Settings
pydantic==2.6.0
pydantic-settings==2.1.0

# Utilities
python-dotenv==1.0.1
tenacity==8.2.3
structlog==24.1.0
```

### backend/app/core/config.py

```python
"""アプリケーション設定"""
from functools import lru_cache
from typing import Optional
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(...)
    database_url: PostgresDsn = Field(...)
    redis_url: RedisDsn = Field(...)
    anthropic_api_key: str = Field(...)
    wordpress_url: str = Field(...)
    wordpress_username: str = Field(...)
    wordpress_app_password: str = Field(...)
    google_credentials_json: str = Field(...)
    frontend_url: str = Field(default="http://localhost:3000")

    @property
    def async_database_url(self) -> str:
        return str(self.database_url).replace("postgresql://", "postgresql+asyncpg://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### backend/app/main.py

```python
"""FastAPI アプリケーション エントリーポイント"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting application in {settings.app_env} mode")
    yield
    print("Shutting down application")


app = FastAPI(
    title="記事自動生成システム API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "env": settings.app_env}
```

### backend/Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: article_generator
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/article_generator
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### フロントエンドの作成

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend
npm install @tanstack/react-query zustand axios lucide-react
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input label table tabs badge dialog select textarea toast
```

---

## ✅ 完了条件

```bash
# Docker Compose が起動する
docker compose up -d db redis
docker compose ps  # healthy 状態を確認

# バックエンドが起動する
cd backend && uvicorn app.main:app --reload
# http://localhost:8000/health → {"status": "healthy"}

# フロントエンドが起動する
cd frontend && npm run dev
# http://localhost:3000 → Next.js ページ表示
```

---

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

# タスク04: Google Sheets連携

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1時間 |
| 前提条件 | タスク03完了 |
| 成果物 | Sheets サービス、同期 API |

---

## 📝 実装ファイル

### backend/app/services/sheets_service.py

```python
"""Google Sheets 連携サービス"""
import json
from datetime import datetime
from typing import Any, Optional
import gspread
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.db.models import ArticleStatus

settings = get_settings()
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_HEADERS = ["KW", "記事タイトル", "ステータス", "公開URL", "WP投稿ID", "生成日時", "更新日時", "備考"]
STATUS_DISPLAY = {
    ArticleStatus.PENDING: "未生成",
    ArticleStatus.GENERATING: "生成中",
    ArticleStatus.FAILED: "生成失敗",
    ArticleStatus.REVIEW_PENDING: "レビュー待ち",
    ArticleStatus.REVIEWED: "レビュー済み",
    ArticleStatus.PUBLISHED: "公開済み",
}


class GoogleSheetsService:
    def __init__(self):
        self._client: Optional[gspread.Client] = None

    @property
    def client(self) -> gspread.Client:
        if self._client is None:
            credentials = Credentials.from_service_account_info(
                json.loads(settings.google_credentials_json), scopes=SCOPES
            )
            self._client = gspread.authorize(credentials)
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_spreadsheet(self, title: str) -> tuple[str, str]:
        spreadsheet = self.client.create(title)
        worksheet = spreadsheet.sheet1
        worksheet.update("A1:H1", [SHEET_HEADERS])
        worksheet.format("A1:H1", {"textFormat": {"bold": True}})
        return spreadsheet.id, spreadsheet.url

    def update_article_status(
        self, sheet_id: str, keyword: str, status: ArticleStatus,
        title: Optional[str] = None, wp_url: Optional[str] = None, wp_post_id: Optional[int] = None
    ) -> bool:
        spreadsheet = self.client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        try:
            cell = worksheet.find(keyword, in_column=1)
        except gspread.CellNotFound:
            worksheet.append_row([keyword, "", STATUS_DISPLAY.get(status, ""), "", "", "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ""])
            cell = worksheet.find(keyword, in_column=1)
        
        row = cell.row
        updates = [{"range": f"C{row}", "values": [[STATUS_DISPLAY.get(status, str(status))]]}]
        if title:
            updates.append({"range": f"B{row}", "values": [[title]]})
        if wp_url:
            updates.append({"range": f"D{row}", "values": [[wp_url]]})
        if wp_post_id:
            updates.append({"range": f"E{row}", "values": [[str(wp_post_id)]]})
        updates.append({"range": f"G{row}", "values": [[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]]})
        worksheet.batch_update(updates)
        return True


sheets_service = GoogleSheetsService()
```

### backend/app/api/sheets.py

```python
"""Google Sheets API"""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, status
from pydantic import BaseModel
from sqlalchemy import select
from app.core.dependencies import DbSession
from app.core.exceptions import NotFoundError, ValidationError
from app.db.models import Article, Category
from app.services.sheets_service import sheets_service

router = APIRouter(prefix="/sheets", tags=["Google Sheets"])


class CreateSheetRequest(BaseModel):
    category_id: UUID


class CreateSheetResponse(BaseModel):
    category_id: UUID
    sheet_id: str
    sheet_url: str


@router.post("/create", response_model=CreateSheetResponse, status_code=status.HTTP_201_CREATED)
async def create_sheet(data: CreateSheetRequest, db: DbSession):
    category = (await db.execute(select(Category).where(Category.id == data.category_id))).scalar_one_or_none()
    if not category:
        raise NotFoundError("Category", str(data.category_id))
    if category.sheet_id:
        raise ValidationError(f"Sheet already exists: {category.sheet_url}")
    
    sheet_id, sheet_url = sheets_service.create_spreadsheet(f"[{category.name}] 記事管理")
    category.sheet_id = sheet_id
    category.sheet_url = sheet_url
    category.sheets_synced_at = datetime.utcnow()
    await db.flush()
    return CreateSheetResponse(category_id=category.id, sheet_id=sheet_id, sheet_url=sheet_url)
```

---

# タスク05: WordPress連携

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1時間 |
| 前提条件 | タスク03完了 |
| 成果物 | WordPress サービス、投稿 API |

---

## 📝 実装ファイル

### backend/app/services/wordpress_service.py

```python
"""WordPress REST API サービス"""
import base64
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

settings = get_settings()


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISH = "publish"


@dataclass
class WordPressPost:
    id: int
    title: str
    status: str
    link: str


class WordPressService:
    def __init__(self):
        self.base_url = settings.wordpress_url.rstrip("/")
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def auth_header(self) -> str:
        credentials = f"{settings.wordpress_username}:{settings.wordpress_app_password}"
        return f"Basic {base64.b64encode(credentials.encode()).decode()}"

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={"Authorization": self.auth_header, "Content-Type": "application/json"},
                timeout=30.0
            )
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def create_post(self, title: str, content: str, status: PostStatus = PostStatus.DRAFT) -> WordPressPost:
        client = await self.get_client()
        response = await client.post(f"{self.api_url}/posts", json={"title": title, "content": content, "status": status.value})
        if response.status_code >= 400:
            raise ExternalServiceError("WordPress", f"Create failed: {response.text}")
        data = response.json()
        return WordPressPost(id=data["id"], title=data["title"]["rendered"], status=data["status"], link=data["link"])

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def publish_post(self, post_id: int) -> WordPressPost:
        client = await self.get_client()
        response = await client.post(f"{self.api_url}/posts/{post_id}", json={"status": "publish"})
        if response.status_code >= 400:
            raise ExternalServiceError("WordPress", f"Publish failed: {response.text}")
        data = response.json()
        return WordPressPost(id=data["id"], title=data["title"]["rendered"], status=data["status"], link=data["link"])


wordpress_service = WordPressService()
```

### backend/app/services/markdown_converter.py

```python
"""Markdown → HTML 変換"""
import re


def markdown_to_html(markdown: str) -> str:
    html = markdown
    for i in range(6, 0, -1):
        html = re.sub(rf"^{'#' * i}\s+(.+)$", rf"<h{i}>\1</h{i}>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)
    html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)
    return html
```

### backend/app/api/wordpress.py

```python
"""WordPress API"""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, status
from pydantic import BaseModel
from sqlalchemy import select
from app.core.dependencies import DbSession
from app.core.exceptions import NotFoundError, ValidationError
from app.db.models import Article, ArticleStatus, Category, JobLog, JobStatus, JobType
from app.services.markdown_converter import markdown_to_html
from app.services.sheets_service import sheets_service
from app.services.wordpress_service import PostStatus, wordpress_service

router = APIRouter(prefix="/wordpress", tags=["WordPress"])


class PublishRequest(BaseModel):
    article_id: UUID


class PublishResponse(BaseModel):
    article_id: UUID
    wp_post_id: int
    wp_url: str
    status: str


@router.post("/draft", response_model=PublishResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(data: PublishRequest, db: DbSession):
    article = (await db.execute(select(Article).where(Article.id == data.article_id))).scalar_one_or_none()
    if not article:
        raise NotFoundError("Article", str(data.article_id))
    if not article.content:
        raise ValidationError("Article has no content")
    if article.wp_post_id:
        raise ValidationError("Article already has WordPress post")

    html = markdown_to_html(article.content)
    wp_post = await wordpress_service.create_post(article.title or article.keyword, html, PostStatus.DRAFT)
    article.wp_post_id = wp_post.id
    article.wp_url = wp_post.link
    db.add(JobLog(article_id=article.id, job_type=JobType.PUBLISH, status=JobStatus.SUCCESS))
    await db.flush()
    return PublishResponse(article_id=article.id, wp_post_id=wp_post.id, wp_url=wp_post.link, status=wp_post.status)


@router.post("/publish", response_model=PublishResponse)
async def publish_article(data: PublishRequest, db: DbSession):
    article = (await db.execute(select(Article).where(Article.id == data.article_id))).scalar_one_or_none()
    if not article:
        raise NotFoundError("Article", str(data.article_id))
    if not article.wp_post_id:
        raise ValidationError("Create draft first")

    wp_post = await wordpress_service.publish_post(article.wp_post_id)
    article.status = ArticleStatus.PUBLISHED
    article.wp_url = wp_post.link
    article.wp_published_at = datetime.utcnow()
    
    category = (await db.execute(select(Category).where(Category.id == article.category_id))).scalar_one_or_none()
    if category and category.sheet_id:
        sheets_service.update_article_status(category.sheet_id, article.keyword, article.status, article.title, article.wp_url, article.wp_post_id)
    
    await db.flush()
    return PublishResponse(article_id=article.id, wp_post_id=wp_post.id, wp_url=wp_post.link, status=wp_post.status)
```

---

# タスク06: Claude API連携

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1時間 |
| 前提条件 | タスク03完了 |
| 成果物 | Claude サービス、プロンプトビルダー |

---

## 📝 実装ファイル

### backend/app/services/llm/base.py

```python
"""LLM 基底クラス"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int


@dataclass
class LLMConfig:
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 8192
    temperature: float = 0.7


class BaseLLMService(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        pass
```

### backend/app/services/llm/claude_service.py

```python
"""Claude API サービス"""
from typing import Optional
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.services.llm.base import BaseLLMService, LLMConfig, LLMResponse

settings = get_settings()


class ClaudeService(BaseLLMService):
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.default_config = LLMConfig()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def generate(self, system_prompt: str, user_prompt: str, config: Optional[LLMConfig] = None) -> LLMResponse:
        cfg = config or self.default_config
        try:
            response = await self.client.messages.create(
                model=cfg.model, max_tokens=cfg.max_tokens, temperature=cfg.temperature,
                system=system_prompt, messages=[{"role": "user", "content": user_prompt}]
            )
            content = "".join(b.text for b in response.content if b.type == "text")
            return LLMResponse(content=content, model=response.model, input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)
        except anthropic.APIError as e:
            raise ExternalServiceError("Claude API", str(e))


claude_service = ClaudeService()
```

### backend/app/services/prompts/prompt_builder.py

```python
"""プロンプトビルダー"""
import re
from dataclasses import dataclass
from typing import Any, Optional
from app.db.models import PromptTemplate


@dataclass
class BuiltPrompt:
    system_prompt: str
    user_prompt: str
    variables: dict[str, Any]


class PromptBuilder:
    DEFAULT_SYSTEM = """あなたはSEOに強いWebライターです。高品質な記事を執筆してください。
- 見出し（h2, h3）を使って構造化
- 具体例を交えて説明
- 自然な日本語で読みやすく"""

    DEFAULT_USER = """「{keyword}」について記事を執筆してください。
【要件】文字数: {char_count_min}〜{char_count_max}文字、フォーマット: Markdown
【構成】タイトル（h1）、導入、本文（h2/h3）、まとめ"""

    def build(self, template: Optional[PromptTemplate], keyword: str, options: Optional[dict] = None) -> BuiltPrompt:
        variables = {"keyword": keyword, "char_count_min": 3000, "char_count_max": 4000}
        if options:
            variables.update(options)
        
        system = template.system_prompt if template else self.DEFAULT_SYSTEM
        user_tpl = template.user_prompt_template if template else self.DEFAULT_USER
        user = re.sub(r"\{(\w+)\}", lambda m: str(variables.get(m.group(1), m.group(0))), user_tpl)
        return BuiltPrompt(system_prompt=system, user_prompt=user, variables=variables)


prompt_builder = PromptBuilder()
```

### backend/app/services/prompts/response_parser.py

```python
"""レスポンスパーサー"""
import re
from dataclasses import dataclass


@dataclass
class ParsedArticle:
    title: str
    content: str
    char_count: int
    is_valid: bool
    errors: list[str]


class ResponseParser:
    def parse(self, response: str, min_chars: int = 2000, max_chars: int = 6000) -> ParsedArticle:
        content = re.sub(r"^```(?:markdown)?\n?|```$", "", response, flags=re.MULTILINE).strip()
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ""
        
        plain = re.sub(r"^#+\s+", "", content, flags=re.MULTILINE)
        plain = re.sub(r"\*\*(.+?)\*\*", r"\1", plain)
        char_count = len(plain)
        
        errors = []
        if not title:
            errors.append("タイトルが見つかりません")
        if char_count < min_chars:
            errors.append(f"文字数不足: {char_count}/{min_chars}")
        
        return ParsedArticle(title=title, content=content, char_count=char_count, is_valid=len(errors) == 0, errors=errors)


response_parser = ResponseParser()
```

---

# タスク07: 記事生成パイプライン

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 2時間 |
| 前提条件 | タスク04-06完了 |
| 成果物 | 記事生成オーケストレーター |

---

## 📝 実装ファイル

### backend/app/services/article_generator.py

```python
"""記事生成オーケストレーター"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Article, ArticleStatus, Category, JobLog, JobStatus, JobType, PromptTemplate
from app.services.llm.base import LLMConfig
from app.services.llm.claude_service import claude_service
from app.services.prompts.prompt_builder import prompt_builder
from app.services.prompts.response_parser import response_parser
from app.services.sheets_service import sheets_service


@dataclass
class GenerationResult:
    success: bool
    article_id: UUID
    title: Optional[str]
    char_count: int
    errors: list[str]
    duration_ms: int


class ArticleGenerator:
    async def generate(
        self, db: AsyncSession, article_id: UUID, options: Optional[dict] = None
    ) -> GenerationResult:
        start = datetime.utcnow()
        
        # 記事取得
        article = (await db.execute(select(Article).where(Article.id == article_id))).scalar_one_or_none()
        if not article:
            return GenerationResult(False, article_id, None, 0, ["Article not found"], 0)
        
        # ステータス更新
        article.status = ArticleStatus.GENERATING
        await db.flush()
        
        try:
            # テンプレート取得
            template = None
            if article.prompt_template_id:
                template = (await db.execute(select(PromptTemplate).where(PromptTemplate.id == article.prompt_template_id))).scalar_one_or_none()
            elif article.category_id:
                result = await db.execute(
                    select(PromptTemplate)
                    .where(PromptTemplate.category_id == article.category_id)
                    .where(PromptTemplate.is_active == True)
                )
                template = result.scalar_one_or_none()
            
            # プロンプト構築
            built = prompt_builder.build(template, article.keyword, options)
            
            # LLM 生成
            config = LLMConfig()
            if options:
                if "temperature" in options:
                    config.temperature = options["temperature"]
                if "max_tokens" in options:
                    config.max_tokens = options["max_tokens"]
            
            llm_response = await claude_service.generate(built.system_prompt, built.user_prompt, config)
            
            # パース
            parsed = response_parser.parse(
                llm_response.content,
                min_chars=options.get("char_count_min", 2000) if options else 2000,
                max_chars=options.get("char_count_max", 6000) if options else 6000
            )
            
            # 記事更新
            article.title = parsed.title or article.keyword
            article.content = parsed.content
            article.status = ArticleStatus.REVIEW_PENDING if parsed.is_valid else ArticleStatus.FAILED
            article.prompt_template_id = template.id if template else None
            article.metadata_ = {
                "char_count": parsed.char_count,
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "model": llm_response.model,
            }
            
            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            
            # ジョブログ
            db.add(JobLog(
                article_id=article.id,
                job_type=JobType.GENERATE,
                status=JobStatus.SUCCESS if parsed.is_valid else JobStatus.FAILED,
                error_message="; ".join(parsed.errors) if parsed.errors else None,
                duration_ms=duration_ms
            ))
            
            await db.flush()
            
            # Sheets 同期
            category = (await db.execute(select(Category).where(Category.id == article.category_id))).scalar_one_or_none()
            if category and category.sheet_id:
                try:
                    sheets_service.update_article_status(
                        category.sheet_id, article.keyword, article.status, article.title
                    )
                except Exception:
                    pass  # Sheets エラーは無視
            
            return GenerationResult(
                success=parsed.is_valid,
                article_id=article.id,
                title=parsed.title,
                char_count=parsed.char_count,
                errors=parsed.errors,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            article.status = ArticleStatus.FAILED
            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            db.add(JobLog(
                article_id=article.id,
                job_type=JobType.GENERATE,
                status=JobStatus.FAILED,
                error_message=str(e),
                duration_ms=duration_ms
            ))
            await db.flush()
            return GenerationResult(False, article_id, None, 0, [str(e)], duration_ms)


article_generator = ArticleGenerator()
```

### backend/app/api/generate.py

```python
"""記事生成 API"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.dependencies import DbSession
from app.services.article_generator import article_generator

router = APIRouter(prefix="/generate", tags=["Generation"])


class GenerateRequest(BaseModel):
    article_id: UUID
    options: Optional[dict] = None


class GenerateResponse(BaseModel):
    success: bool
    article_id: UUID
    title: Optional[str]
    char_count: int
    errors: list[str]
    duration_ms: int


@router.post("", response_model=GenerateResponse)
async def generate_article(data: GenerateRequest, db: DbSession):
    result = await article_generator.generate(db, data.article_id, data.options)
    return GenerateResponse(
        success=result.success,
        article_id=result.article_id,
        title=result.title,
        char_count=result.char_count,
        errors=result.errors,
        duration_ms=result.duration_ms
    )


@router.post("/regenerate/{article_id}", response_model=GenerateResponse)
async def regenerate_article(article_id: UUID, db: DbSession, options: Optional[dict] = None):
    result = await article_generator.generate(db, article_id, options)
    return GenerateResponse(
        success=result.success,
        article_id=result.article_id,
        title=result.title,
        char_count=result.char_count,
        errors=result.errors,
        duration_ms=result.duration_ms
    )
```

---

# タスク08: バッチ処理実装

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1.5時間 |
| 前提条件 | タスク07完了 |
| 成果物 | Redis キュー、ARQ ワーカー |

---

## 📝 実装ファイル

### backend/app/workers/tasks.py

```python
"""ARQ ワーカータスク"""
from typing import Any, Optional
from uuid import UUID
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import get_settings
from app.db.database import async_session_maker
from app.services.article_generator import article_generator

settings = get_settings()


async def generate_article_task(ctx: dict, article_id: str, options: Optional[dict] = None) -> dict:
    """記事生成タスク"""
    async with async_session_maker() as db:
        result = await article_generator.generate(db, UUID(article_id), options)
        await db.commit()
        return {
            "success": result.success,
            "article_id": str(result.article_id),
            "title": result.title,
            "errors": result.errors
        }


async def batch_generate_task(ctx: dict, article_ids: list[str], options: Optional[dict] = None) -> dict:
    """バッチ生成タスク"""
    results = []
    for article_id in article_ids:
        result = await generate_article_task(ctx, article_id, options)
        results.append(result)
    
    success_count = sum(1 for r in results if r["success"])
    return {
        "total": len(article_ids),
        "success": success_count,
        "failed": len(article_ids) - success_count,
        "results": results
    }


class WorkerSettings:
    """ARQ ワーカー設定"""
    functions = [generate_article_task, batch_generate_task]
    redis_settings = RedisSettings.from_dsn(str(settings.redis_url))
    max_jobs = 10
    job_timeout = 300  # 5分
```

### backend/app/api/batch.py

```python
"""バッチ処理 API"""
from uuid import UUID, uuid4
from fastapi import APIRouter
from pydantic import BaseModel, Field
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/batch", tags=["Batch"])


class BatchGenerateRequest(BaseModel):
    article_ids: list[UUID] = Field(..., min_length=1, max_length=100)
    options: dict | None = None


class BatchResponse(BaseModel):
    job_id: str
    total: int
    message: str


@router.post("/generate", response_model=BatchResponse)
async def batch_generate(data: BatchGenerateRequest):
    pool = await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))
    job_id = str(uuid4())
    
    await pool.enqueue_job(
        "batch_generate_task",
        [str(aid) for aid in data.article_ids],
        data.options,
        _job_id=job_id
    )
    await pool.close()
    
    return BatchResponse(
        job_id=job_id,
        total=len(data.article_ids),
        message=f"Batch job started for {len(data.article_ids)} articles"
    )


@router.get("/status/{job_id}")
async def get_batch_status(job_id: str):
    pool = await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))
    job = await pool.job(job_id)
    await pool.close()
    
    if not job:
        return {"job_id": job_id, "status": "not_found"}
    
    info = await job.info()
    return {
        "job_id": job_id,
        "status": info.status if info else "unknown",
        "result": await job.result() if info and info.status == "complete" else None
    }
```

### docker-compose.yml（ワーカー追加）

```yaml
  worker:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/article_generator
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    depends_on:
      - db
      - redis
    command: arq app.workers.tasks.WorkerSettings
```

---

# タスク09: フロントエンド実装

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 3時間 |
| 前提条件 | タスク08完了 |
| 成果物 | Next.js 全画面 |

---

## 📁 ディレクトリ構造

```
frontend/src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                 # ダッシュボード
│   ├── categories/
│   │   ├── page.tsx             # カテゴリ一覧
│   │   └── [id]/page.tsx        # カテゴリ詳細
│   └── articles/
│       ├── page.tsx             # 記事一覧
│       └── [id]/page.tsx        # 記事詳細
├── components/
│   ├── layout/
│   │   ├── header.tsx
│   │   └── sidebar.tsx
│   ├── articles/
│   │   ├── article-list.tsx
│   │   └── article-card.tsx
│   └── categories/
│       └── category-card.tsx
├── lib/
│   ├── api.ts
│   └── utils.ts
├── hooks/
│   └── use-api.ts
└── types/
    └── index.ts
```

---

## 📝 実装ファイル

### frontend/src/lib/api.ts

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
});

export interface Category {
  id: string;
  name: string;
  slug: string;
  sheet_url?: string;
  created_at: string;
}

export interface Article {
  id: string;
  category_id: string;
  keyword: string;
  title?: string;
  content?: string;
  status: 'pending' | 'generating' | 'failed' | 'review_pending' | 'reviewed' | 'published';
  wp_url?: string;
  created_at: string;
}

export const categoriesApi = {
  list: () => api.get<Category[]>('/categories'),
  create: (data: { name: string; slug: string }) => api.post<Category>('/categories', data),
  get: (id: string) => api.get<Category>(`/categories/${id}`),
  delete: (id: string) => api.delete(`/categories/${id}`),
};

export const articlesApi = {
  list: (params?: { category_id?: string; status?: string; page?: number }) =>
    api.get<{ items: Article[]; total: number }>('/articles', { params }),
  create: (data: { category_id: string; keyword: string }) => api.post<Article>('/articles', data),
  get: (id: string) => api.get<Article>(`/articles/${id}`),
  generate: (id: string, options?: object) => api.post(`/generate`, { article_id: id, options }),
  batchGenerate: (ids: string[]) => api.post('/batch/generate', { article_ids: ids }),
};

export const wordpressApi = {
  draft: (articleId: string) => api.post('/wordpress/draft', { article_id: articleId }),
  publish: (articleId: string) => api.post('/wordpress/publish', { article_id: articleId }),
};

export default api;
```

### frontend/src/types/index.ts

```typescript
export type ArticleStatus = 'pending' | 'generating' | 'failed' | 'review_pending' | 'reviewed' | 'published';

export const STATUS_LABELS: Record<ArticleStatus, string> = {
  pending: '未生成',
  generating: '生成中',
  failed: '生成失敗',
  review_pending: 'レビュー待ち',
  reviewed: 'レビュー済み',
  published: '公開済み',
};

export const STATUS_COLORS: Record<ArticleStatus, string> = {
  pending: 'bg-gray-100 text-gray-800',
  generating: 'bg-blue-100 text-blue-800',
  failed: 'bg-red-100 text-red-800',
  review_pending: 'bg-yellow-100 text-yellow-800',
  reviewed: 'bg-green-100 text-green-800',
  published: 'bg-purple-100 text-purple-800',
};
```

### frontend/src/app/layout.tsx

```typescript
import './globals.css';
import { Inter } from 'next/font/google';
import { Toaster } from '@/components/ui/toaster';
import { QueryProvider } from '@/components/providers/query-provider';
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <QueryProvider>
          <div className="flex h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col">
              <Header />
              <main className="flex-1 overflow-auto p-6 bg-gray-50">
                {children}
              </main>
            </div>
          </div>
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}
```

### frontend/src/components/layout/sidebar.tsx

```typescript
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, FolderOpen, FileText, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'ダッシュボード', href: '/', icon: Home },
  { name: 'カテゴリ', href: '/categories', icon: FolderOpen },
  { name: '記事', href: '/articles', icon: FileText },
  { name: '設定', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  
  return (
    <div className="w-64 bg-white border-r">
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold">記事生成システム</h1>
      </div>
      <nav className="p-4 space-y-1">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-md text-sm',
              pathname === item.href
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            <item.icon className="w-5 h-5" />
            {item.name}
          </Link>
        ))}
      </nav>
    </div>
  );
}
```

### frontend/src/app/page.tsx（ダッシュボード）

```typescript
'use client';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { articlesApi, categoriesApi } from '@/lib/api';
import { STATUS_LABELS } from '@/types';

export default function DashboardPage() {
  const { data: articles } = useQuery({
    queryKey: ['articles'],
    queryFn: () => articlesApi.list({ page: 1 }),
  });
  
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesApi.list(),
  });
  
  const stats = articles?.data.items.reduce((acc, a) => {
    acc[a.status] = (acc[a.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">ダッシュボード</h1>
      
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">総記事数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{articles?.data.total || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">レビュー待ち</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-yellow-600">{stats.review_pending || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">公開済み</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{stats.published || 0}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500">カテゴリ数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{categories?.data.length || 0}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### frontend/src/app/articles/page.tsx（記事一覧）

```typescript
'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { articlesApi, categoriesApi } from '@/lib/api';
import { STATUS_LABELS, STATUS_COLORS, ArticleStatus } from '@/types';
import { useToast } from '@/components/ui/use-toast';
import Link from 'next/link';

export default function ArticlesPage() {
  const [selected, setSelected] = useState<string[]>([]);
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const { data: articles, isLoading } = useQuery({
    queryKey: ['articles'],
    queryFn: () => articlesApi.list(),
  });
  
  const generateMutation = useMutation({
    mutationFn: (id: string) => articlesApi.generate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      toast({ title: '生成を開始しました' });
    },
  });
  
  const batchMutation = useMutation({
    mutationFn: (ids: string[]) => articlesApi.batchGenerate(ids),
    onSuccess: () => {
      setSelected([]);
      toast({ title: 'バッチ生成を開始しました' });
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">記事一覧</h1>
        <div className="space-x-2">
          {selected.length > 0 && (
            <Button onClick={() => batchMutation.mutate(selected)}>
              選択した{selected.length}件を生成
            </Button>
          )}
        </div>
      </div>
      
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-12">
              <input
                type="checkbox"
                onChange={(e) => setSelected(e.target.checked ? articles?.data.items.map(a => a.id) || [] : [])}
              />
            </TableHead>
            <TableHead>キーワード</TableHead>
            <TableHead>タイトル</TableHead>
            <TableHead>ステータス</TableHead>
            <TableHead>操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {articles?.data.items.map((article) => (
            <TableRow key={article.id}>
              <TableCell>
                <input
                  type="checkbox"
                  checked={selected.includes(article.id)}
                  onChange={(e) => setSelected(
                    e.target.checked
                      ? [...selected, article.id]
                      : selected.filter(id => id !== article.id)
                  )}
                />
              </TableCell>
              <TableCell>{article.keyword}</TableCell>
              <TableCell>{article.title || '-'}</TableCell>
              <TableCell>
                <Badge className={STATUS_COLORS[article.status as ArticleStatus]}>
                  {STATUS_LABELS[article.status as ArticleStatus]}
                </Badge>
              </TableCell>
              <TableCell>
                <div className="space-x-2">
                  <Link href={`/articles/${article.id}`}>
                    <Button variant="outline" size="sm">詳細</Button>
                  </Link>
                  {article.status === 'pending' && (
                    <Button size="sm" onClick={() => generateMutation.mutate(article.id)}>
                      生成
                    </Button>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

### frontend/src/components/providers/query-provider.tsx

```typescript
'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: { staleTime: 60 * 1000 },
    },
  }));
  
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

---

# タスク10: 結合テスト・デプロイ

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI + 👤 人間 |
| 所要時間 | 2時間 |
| 前提条件 | タスク09完了 |
| 成果物 | E2Eテスト、本番デプロイ |

---

## 🤖 AI Agent の作業

### E2E テストスクリプト

**backend/tests/test_e2e.py**

```python
"""E2E テスト"""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_full_workflow(client: AsyncClient):
    """フルワークフローテスト"""
    
    # 1. カテゴリ作成
    res = await client.post("/api/categories", json={"name": "E2Eテスト", "slug": "e2e-test"})
    assert res.status_code == 201
    category_id = res.json()["id"]
    
    # 2. 記事作成
    res = await client.post("/api/articles", json={"category_id": category_id, "keyword": "テストKW"})
    assert res.status_code == 201
    article_id = res.json()["id"]
    assert res.json()["status"] == "pending"
    
    # 3. 記事取得
    res = await client.get(f"/api/articles/{article_id}")
    assert res.status_code == 200
    assert res.json()["keyword"] == "テストKW"
    
    # 4. カテゴリ削除（記事があるので失敗するはず）
    res = await client.delete(f"/api/categories/{category_id}")
    assert res.status_code == 409
    
    # 5. 記事削除
    res = await client.delete(f"/api/articles/{article_id}")
    assert res.status_code == 204
    
    # 6. カテゴリ削除（成功）
    res = await client.delete(f"/api/categories/{category_id}")
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
```

### GitHub Actions CI

**.github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
          SECRET_KEY: test-secret-key
          ANTHROPIC_API_KEY: test-key
          WORDPRESS_URL: https://example.com
          WORDPRESS_USERNAME: test
          WORDPRESS_APP_PASSWORD: test
          GOOGLE_CREDENTIALS_JSON: '{}'
        run: |
          cd backend
          pytest -v

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install and build
        run: |
          cd frontend
          npm ci
          npm run build
```

---

## 👤 人間の作業

### 1. 本番環境変数の設定

**Railway / Render での環境変数設定:**

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
WORDPRESS_URL=https://your-production-site.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=<本番用の長いランダム文字列>
APP_ENV=production
DEBUG=false
FRONTEND_URL=https://your-frontend-domain.vercel.app
```

### 2. デプロイ手順

#### Backend (Railway)

1. [Railway](https://railway.app/) にログイン
2. 「New Project」→「Deploy from GitHub repo」
3. リポジトリを選択、`backend` ディレクトリを指定
4. 環境変数を設定
5. PostgreSQL と Redis のアドオンを追加

#### Frontend (Vercel)

1. [Vercel](https://vercel.com/) にログイン
2. 「Import Project」→ GitHub リポジトリを選択
3. Root Directory を `frontend` に設定
4. 環境変数を設定:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
   ```
5. デプロイ

### 3. 動作確認チェックリスト

- [ ] フロントエンドにアクセスできる
- [ ] ログイン/認証が動作する（実装している場合）
- [ ] カテゴリの作成・一覧表示ができる
- [ ] Google Sheets の作成・連携ができる
- [ ] 記事の作成・一覧表示ができる
- [ ] 記事生成が動作する（Claude API）
- [ ] WordPress への下書き投稿ができる
- [ ] WordPress への公開ができる
- [ ] Google Sheets に状態が反映される
- [ ] バッチ生成が動作する

### 4. 監視設定（推奨）

1. **エラー監視**: Sentry の導入
2. **ログ監視**: Railway / Render のログ確認
3. **アラート**: Slack / Discord への通知設定

---

## 📊 最終アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet                                  │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│         Vercel              │   │        Railway              │
│  ┌───────────────────────┐  │   │  ┌───────────────────────┐  │
│  │   Next.js Frontend    │  │   │  │   FastAPI Backend     │  │
│  │   (Static + SSR)      │──┼───┼─▶│   (API + Worker)      │  │
│  └───────────────────────┘  │   │  └───────────────────────┘  │
└─────────────────────────────┘   │           │                  │
                                  │           ▼                  │
                                  │  ┌───────────────────────┐  │
                                  │  │     PostgreSQL        │  │
                                  │  └───────────────────────┘  │
                                  │           │                  │
                                  │           ▼                  │
                                  │  ┌───────────────────────┐  │
                                  │  │       Redis           │  │
                                  │  └───────────────────────┘  │
                                  └─────────────────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
          │   Claude API    │       │  Google Sheets  │       │    WordPress    │
          │   (Anthropic)   │       │      API        │       │    REST API     │
          └─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## ✅ 全体完了チェックリスト

### 事前準備（👤 人間）
- [ ] Anthropic API キー取得
- [ ] WordPress アプリケーションパスワード作成
- [ ] Google Cloud プロジェクト作成
- [ ] Google Sheets API / Drive API 有効化
- [ ] サービスアカウント作成

### バックエンド（🤖 AI）
- [ ] プロジェクト構造作成
- [ ] データベースモデル実装
- [ ] マイグレーション実行
- [ ] CRUD API 実装
- [ ] Google Sheets 連携実装
- [ ] WordPress 連携実装
- [ ] Claude API 連携実装
- [ ] 記事生成パイプライン実装
- [ ] バッチ処理実装

### フロントエンド（🤖 AI）
- [ ] Next.js プロジェクト作成
- [ ] 共通レイアウト実装
- [ ] ダッシュボード画面
- [ ] カテゴリ管理画面
- [ ] 記事管理画面
- [ ] 記事詳細・プレビュー画面

### デプロイ（🤖 AI + 👤 人間）
- [ ] E2E テスト作成
- [ ] CI/CD パイプライン設定
- [ ] 本番環境変数設定
- [ ] バックエンドデプロイ
- [ ] フロントエンドデプロイ
- [ ] 動作確認

---

## 🎉 完了

おめでとうございます！記事自動生成システムの実装が完了しました。

### 今後の拡張案

1. **RAG 機能追加**: ベクトルDBを導入し、既存記事を参照した生成
2. **認証機能**: NextAuth.js による認証追加
3. **画像生成**: DALL-E / Stable Diffusion 連携
4. **SEO 分析**: 生成記事の SEO スコア自動計算
5. **A/B テスト**: プロンプトテンプレートの効果測定

---

*このドキュメントは AI Agent が実装を進めるための完全ガイドです。各タスクの完了条件を満たしながら順番に進めてください。*
