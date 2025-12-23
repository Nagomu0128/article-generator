"""データベース接続設定"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# 非同期エンジン作成
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

# 非同期セッションメーカー
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy Base クラス"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッション依存性"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# FastAPI依存性注入用の型アノテーション
DbSession = Annotated[AsyncSession, Depends(get_db)]
