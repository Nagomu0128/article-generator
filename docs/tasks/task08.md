# タスク08: バッチ処理実装

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 1.5時間 |
| 前提条件 | タスク07完了 |
| 成果物 | Redis キュー、ARQ ワーカー |

---

## 📝 実装ファイル

### backend/app/workers/tasks.py

```python
"""ARQ ワーカータスク"""
from typing import Any, Optional
from uuid import UUID
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import get_settings
from app.db.database import async_session_maker
from app.services.article_generator import article_generator

settings = get_settings()


async def generate_article_task(ctx: dict, article_id: str, options: Optional[dict] = None) -> dict:
    """記事生成タスク"""
    async with async_session_maker() as db:
        result = await article_generator.generate(db, UUID(article_id), options)
        await db.commit()
        return {
            "success": result.success,
            "article_id": str(result.article_id),
            "title": result.title,
            "errors": result.errors
        }


async def batch_generate_task(ctx: dict, article_ids: list[str], options: Optional[dict] = None) -> dict:
    """バッチ生成タスク"""
    results = []
    for article_id in article_ids:
        result = await generate_article_task(ctx, article_id, options)
        results.append(result)

    success_count = sum(1 for r in results if r["success"])
    return {
        "total": len(article_ids),
        "success": success_count,
        "failed": len(article_ids) - success_count,
        "results": results
    }


class WorkerSettings:
    """ARQ ワーカー設定"""
    functions = [generate_article_task, batch_generate_task]
    redis_settings = RedisSettings.from_dsn(str(settings.redis_url))
    max_jobs = 10
    job_timeout = 300  # 5分
```

### backend/app/api/batch.py

```python
"""バッチ処理 API"""
from uuid import UUID, uuid4
from fastapi import APIRouter
from pydantic import BaseModel, Field
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/batch", tags=["Batch"])


class BatchGenerateRequest(BaseModel):
    article_ids: list[UUID] = Field(..., min_length=1, max_length=100)
    options: dict | None = None


class BatchResponse(BaseModel):
    job_id: str
    total: int
    message: str


@router.post("/generate", response_model=BatchResponse)
async def batch_generate(data: BatchGenerateRequest):
    pool = await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))
    job_id = str(uuid4())

    await pool.enqueue_job(
        "batch_generate_task",
        [str(aid) for aid in data.article_ids],
        data.options,
        _job_id=job_id
    )
    await pool.close()

    return BatchResponse(
        job_id=job_id,
        total=len(data.article_ids),
        message=f"Batch job started for {len(data.article_ids)} articles"
    )


@router.get("/status/{job_id}")
async def get_batch_status(job_id: str):
    pool = await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))
    job = await pool.job(job_id)
    await pool.close()

    if not job:
        return {"job_id": job_id, "status": "not_found"}

    info = await job.info()
    return {
        "job_id": job_id,
        "status": info.status if info else "unknown",
        "result": await job.result() if info and info.status == "complete" else None
    }
```

### backend/app/api/__init__.py（更新）

```python
"""API ルーター集約"""
from fastapi import APIRouter
from app.api.articles import router as articles_router
from app.api.batch import router as batch_router
from app.api.categories import router as categories_router
from app.api.generate import router as generate_router
from app.api.sheets import router as sheets_router
from app.api.wordpress import router as wordpress_router

api_router = APIRouter(prefix="/api")
api_router.include_router(categories_router)
api_router.include_router(articles_router)
api_router.include_router(sheets_router)
api_router.include_router(wordpress_router)
api_router.include_router(generate_router)
api_router.include_router(batch_router)
```

### docker-compose.yml（ワーカー追加）

```yaml
  worker:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/article_generator
      - REDIS_URL=redis://redis:6379
    env_file:
      - .env
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis
    command: arq app.workers.tasks.WorkerSettings
```

---

## ✅ 完了条件

```bash
# ワーカーを起動
docker compose up -d worker

# バッチ生成をリクエスト
curl -X POST http://localhost:8000/api/batch/generate \
  -H "Content-Type: application/json" \
  -d '{"article_ids":["<記事ID1>","<記事ID2>"]}'

# ジョブステータスを確認
curl http://localhost:8000/api/batch/status/<JOB_ID>

# ワーカーログで処理を確認
docker compose logs -f worker
```

---

## 📌 次のタスク

タスク08完了後、**タスク09: フロントエンド実装** に進んでください。
