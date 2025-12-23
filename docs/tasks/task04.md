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

### backend/app/api/__init__.py（更新）

```python
"""API ルーター集約"""
from fastapi import APIRouter
from app.api.articles import router as articles_router
from app.api.categories import router as categories_router
from app.api.sheets import router as sheets_router

api_router = APIRouter(prefix="/api")
api_router.include_router(categories_router)
api_router.include_router(articles_router)
api_router.include_router(sheets_router)
```

---

## ✅ 完了条件

```bash
# Google Sheets API が動作する
curl -X POST http://localhost:8000/api/sheets/create \
  -H "Content-Type: application/json" \
  -d '{"category_id":"<カテゴリID>"}'

# レスポンスに sheet_id と sheet_url が含まれる
# Google Sheets が作成され、ヘッダー行が設定されている
```

---

## 📌 次のタスク

タスク04完了後、**タスク07: 記事生成パイプライン** に進むための準備が整います。
