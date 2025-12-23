"""カテゴリPydanticスキーマ"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """カテゴリ作成リクエスト"""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")


class CategoryUpdate(BaseModel):
    """カテゴリ更新リクエスト"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")


class CategoryResponse(BaseModel):
    """カテゴリレスポンス"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    sheet_id: Optional[str] = None
    sheet_url: Optional[str] = None
    sheets_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
