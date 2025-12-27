"""Google Sheetsドメインスキーマ"""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateSheetRequest(BaseModel):
    """スプレッドシート作成リクエスト"""

    category_id: UUID = Field(..., description="カテゴリID")


class CreateSheetResponse(BaseModel):
    """スプレッドシート作成レスポンス"""

    category_id: UUID
    sheet_id: str
    sheet_url: str


class LinkSheetRequest(BaseModel):
    """手動作成したスプレッドシートをリンクするリクエスト"""

    category_id: UUID = Field(..., description="カテゴリID")
    sheet_id: str = Field(..., description="スプレッドシートID")
    sheet_url: str = Field(..., description="スプレッドシートURL")


class UpdateArticleStatusRequest(BaseModel):
    """記事ステータス更新リクエスト"""

    sheet_id: str = Field(..., description="スプレッドシートID")
    keyword: str = Field(..., description="キーワード")
    status: str = Field(..., description="ステータス")
    title: str | None = Field(None, description="記事タイトル")
    wp_url: str | None = Field(None, description="WordPress URL")
    wp_post_id: int | None = Field(None, description="WordPress投稿ID")
