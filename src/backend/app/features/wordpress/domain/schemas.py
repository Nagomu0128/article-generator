"""WordPress API スキーマ"""

from uuid import UUID

from pydantic import BaseModel, Field


class PublishRequest(BaseModel):
    """WordPress投稿リクエスト"""

    article_id: UUID = Field(..., description="記事ID")


class PublishResponse(BaseModel):
    """WordPress投稿レスポンス"""

    article_id: UUID = Field(..., description="記事ID")
    wp_post_id: int = Field(..., description="WordPress投稿ID")
    wp_url: str = Field(..., description="WordPress投稿URL")
    status: str = Field(..., description="投稿ステータス（draft/publish）")
