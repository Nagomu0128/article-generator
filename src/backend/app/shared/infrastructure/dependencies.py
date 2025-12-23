"""共通依存性"""

from typing import Annotated

from fastapi import Depends, Query

from app.shared.infrastructure.database import AsyncSession, get_db

# データベースセッション依存性
DbSession = Annotated[AsyncSession, Depends(get_db)]


class PaginationParams:
    """ページネーションパラメータ"""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="ページ番号"),
        per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    ):
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page


# ページネーション依存性
Pagination = Annotated[PaginationParams, Depends()]
