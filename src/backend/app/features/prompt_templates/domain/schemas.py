"""プロンプトテンプレートPydanticスキーマ"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PromptTemplateCreate(BaseModel):
    """プロンプトテンプレート作成リクエスト"""

    category_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    system_prompt: str = Field(..., min_length=1)
    user_prompt_template: str = Field(..., min_length=1)
    is_active: bool = False
    options: Optional[dict] = None


class PromptTemplateUpdate(BaseModel):
    """プロンプトテンプレート更新リクエスト"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    system_prompt: Optional[str] = Field(None, min_length=1)
    user_prompt_template: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None
    options: Optional[dict] = None


class PromptTemplateResponse(BaseModel):
    """プロンプトテンプレートレスポンス"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    name: str
    system_prompt: str
    user_prompt_template: str
    is_active: bool
    version: int
    options: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
