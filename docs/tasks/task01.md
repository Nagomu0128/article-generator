# タスク01: プロジェクト初期化

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 30分 |
| 前提条件 | タスク00完了 |
| 成果物 | プロジェクトディレクトリ構造、Docker設定 |

---

## 🎯 ゴール

1. モノレポ構造のプロジェクトディレクトリを作成
2. バックエンド（Python/FastAPI）の依存関係を設定
3. フロントエンド（Next.js/TypeScript）の依存関係を設定
4. Docker Compose による開発環境を構築

---

## 📁 作成するディレクトリ構造

```
article-generator/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── db/
│   │   └── core/
│   │       └── config.py
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── (Next.js project)
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 📝 実装ファイル

### backend/requirements.txt

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1

# Redis / Task Queue
redis==5.0.1
arq==0.25.0

# External APIs
anthropic==0.18.1
gspread==6.0.2
google-auth==2.27.0
httpx==0.26.0

# Validation & Settings
pydantic==2.6.0
pydantic-settings==2.1.0

# Utilities
python-dotenv==1.0.1
tenacity==8.2.3
structlog==24.1.0
```

### backend/app/core/config.py

```python
"""アプリケーション設定"""
from functools import lru_cache
from typing import Optional
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(...)
    database_url: PostgresDsn = Field(...)
    redis_url: RedisDsn = Field(...)
    anthropic_api_key: str = Field(...)
    wordpress_url: str = Field(...)
    wordpress_username: str = Field(...)
    wordpress_app_password: str = Field(...)
    google_credentials_json: str = Field(...)
    frontend_url: str = Field(default="http://localhost:3000")

    @property
    def async_database_url(self) -> str:
        return str(self.database_url).replace("postgresql://", "postgresql+asyncpg://")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### backend/app/main.py

```python
"""FastAPI アプリケーション エントリーポイント"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

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
```

### backend/Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: article_generator
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/article_generator
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### フロントエンドの作成

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend
npm install @tanstack/react-query zustand axios lucide-react
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input label table tabs badge dialog select textarea toast
```

---

## ✅ 完了条件

```bash
# Docker Compose が起動する
docker compose up -d db redis
docker compose ps  # healthy 状態を確認

# バックエンドが起動する
cd backend && uvicorn app.main:app --reload
# http://localhost:8000/health → {"status": "healthy"}

# フロントエンドが起動する
cd frontend && npm run dev
# http://localhost:3000 → Next.js ページ表示
```

---

## 📌 次のタスク

タスク01完了後、**タスク02: データベース設計** に進んでください。
