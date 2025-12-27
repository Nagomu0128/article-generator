"""Google Sheets APIルート"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, status
from sqlalchemy import select

from app.features.categories.domain.models import Category
from app.features.sheets.domain.schemas import (
    CreateSheetRequest,
    CreateSheetResponse,
    LinkSheetRequest,
)
from app.features.sheets.infrastructure.google_sheets_service import sheets_service
from app.shared.domain.exceptions import NotFoundError, ValidationError
from app.shared.infrastructure.dependencies import DbSession

router = APIRouter(prefix="/sheets", tags=["Google Sheets"])


@router.post(
    "/create", response_model=CreateSheetResponse, status_code=status.HTTP_201_CREATED
)
async def create_sheet(data: CreateSheetRequest, db: DbSession):
    """
    カテゴリ用のGoogle Sheetsスプレッドシートを作成

    Args:
        data: 作成リクエスト
        db: データベースセッション

    Returns:
        作成されたスプレッドシート情報
    """
    # カテゴリ存在確認
    result = await db.execute(select(Category).where(Category.id == data.category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise NotFoundError("Category", str(data.category_id))

    # 既にスプレッドシートが存在する場合はエラー
    if category.sheet_id:
        raise ValidationError(f"Sheet already exists: {category.sheet_url}")

    # スプレッドシート作成
    sheet_id, sheet_url = sheets_service.create_spreadsheet(
        f"[{category.name}] 記事管理"
    )

    # カテゴリ情報更新
    category.sheet_id = sheet_id
    category.sheet_url = sheet_url
    category.sheets_synced_at = datetime.utcnow()
    await db.flush()

    return CreateSheetResponse(
        category_id=category.id, sheet_id=sheet_id, sheet_url=sheet_url
    )


@router.post(
    "/link", response_model=CreateSheetResponse, status_code=status.HTTP_200_OK
)
async def link_sheet(data: LinkSheetRequest, db: DbSession):
    """
    手動で作成したスプレッドシートをカテゴリにリンク

    Args:
        data: リンクリクエスト
        db: データベースセッション

    Returns:
        リンクされたスプレッドシート情報
    """
    # カテゴリ存在確認
    result = await db.execute(select(Category).where(Category.id == data.category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise NotFoundError("Category", str(data.category_id))

    # 既にスプレッドシートが存在する場合はエラー
    if category.sheet_id:
        raise ValidationError(f"Sheet already exists: {category.sheet_url}")

    # スプレッドシートIDとURLを検証
    if not data.sheet_id or not data.sheet_url:
        raise ValidationError("sheet_id and sheet_url are required")

    # カテゴリ情報更新
    category.sheet_id = data.sheet_id
    category.sheet_url = data.sheet_url
    category.sheets_synced_at = datetime.utcnow()
    await db.flush()

    return CreateSheetResponse(
        category_id=category.id, sheet_id=data.sheet_id, sheet_url=data.sheet_url
    )
