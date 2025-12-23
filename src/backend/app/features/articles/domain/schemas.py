"""記事Pydanticスキーマ"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.domain.enums import ArticleStatus


class ArticleCreate(BaseModel):
    """記事作成リクエスト"""

    category_id: UUID
    keyword: str = Field(..., min_length=1, max_length=200)
    prompt_template_id: Optional[UUID] = None


class ArticleUpdate(BaseModel):
    """記事更新リクエスト"""

    keyword: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, max_length=300)
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None


class ArticleResponse(BaseModel):
    """記事レスポンス"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    prompt_template_id: Optional[UUID] = None
    keyword: str
    title: Optional[str] = None
    content: Optional[str] = None
    status: ArticleStatus
    wp_post_id: Optional[int] = None
    wp_url: Optional[str] = None
    wp_published_at: Optional[datetime] = None
    metadata_: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class ArticleListResponse(BaseModel):
    """記事一覧レスポンス"""

    items: list[ArticleResponse]
    total: int
    page: int
    per_page: int
