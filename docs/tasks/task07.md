# タスク07: 記事生成パイプライン

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI Agent |
| 所要時間 | 2時間 |
| 前提条件 | タスク04, 05, 06完了 |
| 成果物 | 記事生成オーケストレーター |

---

## 📝 実装ファイル

### backend/app/services/article_generator.py

```python
"""記事生成オーケストレーター"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Article, ArticleStatus, Category, JobLog, JobStatus, JobType, PromptTemplate
from app.services.llm.base import LLMConfig
from app.services.llm.claude_service import claude_service
from app.services.prompts.prompt_builder import prompt_builder
from app.services.prompts.response_parser import response_parser
from app.services.sheets_service import sheets_service


@dataclass
class GenerationResult:
    success: bool
    article_id: UUID
    title: Optional[str]
    char_count: int
    errors: list[str]
    duration_ms: int


class ArticleGenerator:
    async def generate(
        self, db: AsyncSession, article_id: UUID, options: Optional[dict] = None
    ) -> GenerationResult:
        start = datetime.utcnow()

        # 記事取得
        article = (await db.execute(select(Article).where(Article.id == article_id))).scalar_one_or_none()
        if not article:
            return GenerationResult(False, article_id, None, 0, ["Article not found"], 0)

        # ステータス更新
        article.status = ArticleStatus.GENERATING
        await db.flush()

        try:
            # テンプレート取得
            template = None
            if article.prompt_template_id:
                template = (await db.execute(select(PromptTemplate).where(PromptTemplate.id == article.prompt_template_id))).scalar_one_or_none()
            elif article.category_id:
                result = await db.execute(
                    select(PromptTemplate)
                    .where(PromptTemplate.category_id == article.category_id)
                    .where(PromptTemplate.is_active == True)
                )
                template = result.scalar_one_or_none()

            # プロンプト構築
            built = prompt_builder.build(template, article.keyword, options)

            # LLM 生成
            config = LLMConfig()
            if options:
                if "temperature" in options:
                    config.temperature = options["temperature"]
                if "max_tokens" in options:
                    config.max_tokens = options["max_tokens"]

            llm_response = await claude_service.generate(built.system_prompt, built.user_prompt, config)

            # パース
            parsed = response_parser.parse(
                llm_response.content,
                min_chars=options.get("char_count_min", 2000) if options else 2000,
                max_chars=options.get("char_count_max", 6000) if options else 6000
            )

            # 記事更新
            article.title = parsed.title or article.keyword
            article.content = parsed.content
            article.status = ArticleStatus.REVIEW_PENDING if parsed.is_valid else ArticleStatus.FAILED
            article.prompt_template_id = template.id if template else None
            article.metadata_ = {
                "char_count": parsed.char_count,
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "model": llm_response.model,
            }

            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

            # ジョブログ
            db.add(JobLog(
                article_id=article.id,
                job_type=JobType.GENERATE,
                status=JobStatus.SUCCESS if parsed.is_valid else JobStatus.FAILED,
                error_message="; ".join(parsed.errors) if parsed.errors else None,
                duration_ms=duration_ms
            ))

            await db.flush()

            # Sheets 同期
            category = (await db.execute(select(Category).where(Category.id == article.category_id))).scalar_one_or_none()
            if category and category.sheet_id:
                try:
                    sheets_service.update_article_status(
                        category.sheet_id, article.keyword, article.status, article.title
                    )
                except Exception:
                    pass  # Sheets エラーは無視

            return GenerationResult(
                success=parsed.is_valid,
                article_id=article.id,
                title=parsed.title,
                char_count=parsed.char_count,
                errors=parsed.errors,
                duration_ms=duration_ms
            )

        except Exception as e:
            article.status = ArticleStatus.FAILED
            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            db.add(JobLog(
                article_id=article.id,
                job_type=JobType.GENERATE,
                status=JobStatus.FAILED,
                error_message=str(e),
                duration_ms=duration_ms
            ))
            await db.flush()
            return GenerationResult(False, article_id, None, 0, [str(e)], duration_ms)


article_generator = ArticleGenerator()
```

### backend/app/api/generate.py

```python
"""記事生成 API"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.dependencies import DbSession
from app.services.article_generator import article_generator

router = APIRouter(prefix="/generate", tags=["Generation"])


class GenerateRequest(BaseModel):
    article_id: UUID
    options: Optional[dict] = None


class GenerateResponse(BaseModel):
    success: bool
    article_id: UUID
    title: Optional[str]
    char_count: int
    errors: list[str]
    duration_ms: int


@router.post("", response_model=GenerateResponse)
async def generate_article(data: GenerateRequest, db: DbSession):
    result = await article_generator.generate(db, data.article_id, data.options)
    return GenerateResponse(
        success=result.success,
        article_id=result.article_id,
        title=result.title,
        char_count=result.char_count,
        errors=result.errors,
        duration_ms=result.duration_ms
    )


@router.post("/regenerate/{article_id}", response_model=GenerateResponse)
async def regenerate_article(article_id: UUID, db: DbSession, options: Optional[dict] = None):
    result = await article_generator.generate(db, article_id, options)
    return GenerateResponse(
        success=result.success,
        article_id=result.article_id,
        title=result.title,
        char_count=result.char_count,
        errors=result.errors,
        duration_ms=result.duration_ms
    )
```

### backend/app/api/__init__.py（更新）

```python
"""API ルーター集約"""
from fastapi import APIRouter
from app.api.articles import router as articles_router
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
```

---

## ✅ 完了条件

```bash
# 記事を作成
curl -X POST http://localhost:8000/api/articles \
  -H "Content-Type: application/json" \
  -d '{"category_id":"<カテゴリID>","keyword":"AI開発"}'

# 記事生成
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"article_id":"<記事ID>"}'

# レスポンスに title と content が含まれる
# データベースの記事ステータスが review_pending になる
# Google Sheets が更新される（カテゴリに紐付いている場合）
```

---

## 📌 次のタスク

タスク07完了後、**タスク08: バッチ処理実装** に進んでください。
