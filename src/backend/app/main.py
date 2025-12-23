"""FastAPI アプリケーション エントリーポイント"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

# すべてのモデルをインポート（SQLAlchemyリレーションシップ解決のため）
from app.shared.domain import models  # noqa

from app.features.articles.presentation.routes import router as articles_router
from app.features.categories.presentation.routes import router as categories_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting application in {settings.app_env} mode")
    yield
    print("Shutting down application")


app = FastAPI(
    title="記事自動生成システム API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "env": settings.app_env}


# APIルーター登録
app.include_router(categories_router, prefix="/api")
app.include_router(articles_router, prefix="/api")