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

### backend/app/api/__init__.py（更新）

```python
"""API ルーター集約"""
from fastapi import APIRouter
from app.api.articles import router as articles_router
from app.api.categories import router as categories_router
from app.api.sheets import router as sheets_router
from app.api.wordpress import router as wordpress_router

api_router = APIRouter(prefix="/api")
api_router.include_router(categories_router)
api_router.include_router(articles_router)
api_router.include_router(sheets_router)
api_router.include_router(wordpress_router)
```

---

## ✅ 完了条件

```bash
# WordPress 下書き作成
curl -X POST http://localhost:8000/api/wordpress/draft \
  -H "Content-Type: application/json" \
  -d '{"article_id":"<記事ID>"}'

# WordPress 公開
curl -X POST http://localhost:8000/api/wordpress/publish \
  -H "Content-Type: application/json" \
  -d '{"article_id":"<記事ID>"}'

# WordPress 管理画面で下書き・公開が確認できる
```

---

## 📌 次のタスク

タスク05完了後、**タスク07: 記事生成パイプライン** に進むための準備が整います。
