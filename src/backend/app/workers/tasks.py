"""ARQ worker tasks for background job processing.

This module defines background tasks that run asynchronously
using ARQ (Async Redis Queue) for article generation and
batch processing operations.
"""
from typing import Any, Optional
from uuid import UUID

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.features.articles.application.article_generator import get_article_generator
from app.shared.infrastructure.database import async_session_maker

settings = get_settings()


async def generate_article_task(
    ctx: dict,
    article_id: str,
    options: Optional[dict] = None
) -> dict:
    """Background task for generating a single article.

    This task is executed by ARQ workers and generates article
    content using Claude API. The task is idempotent and can be
    safely retried.

    Args:
        ctx: ARQ context dictionary
        article_id: UUID string of the article to generate
        options: Optional generation options (temperature, char_count, etc.)

    Returns:
        Dictionary with generation results:
        - success: bool
        - article_id: str
        - title: str | None
        - errors: list[str]

    Example:
        >>> await pool.enqueue_job(
        ...     'generate_article_task',
        ...     '123e4567-e89b-12d3-a456-426614174000',
        ...     {'temperature': 0.7}
        ... )
    """
    async with async_session_maker() as db:
        generator = get_article_generator()
        result = await generator.generate(db, UUID(article_id), options)
        await db.commit()

        return {
            "success": result.success,
            "article_id": str(result.article_id),
            "title": result.title,
            "char_count": result.char_count,
            "errors": result.errors,
            "duration_ms": result.duration_ms
        }


async def batch_generate_task(
    ctx: dict,
    article_ids: list[str],
    options: Optional[dict] = None
) -> dict:
    """Background task for batch article generation.

    Generates multiple articles sequentially. Each article is
    generated independently, so partial success is possible.

    Args:
        ctx: ARQ context dictionary
        article_ids: List of article UUID strings to generate
        options: Optional generation options applied to all articles

    Returns:
        Dictionary with batch results:
        - total: int - Total number of articles
        - success: int - Number of successful generations
        - failed: int - Number of failed generations
        - results: list[dict] - Individual article results

    Example:
        >>> await pool.enqueue_job(
        ...     'batch_generate_task',
        ...     ['uuid1', 'uuid2', 'uuid3'],
        ...     {'char_count_min': 2000}
        ... )
    """
    results = []

    for article_id in article_ids:
        try:
            result = await generate_article_task(ctx, article_id, options)
            results.append(result)
        except Exception as e:
            # Record error but continue processing other articles
            results.append({
                "success": False,
                "article_id": article_id,
                "title": None,
                "char_count": 0,
                "errors": [str(e)],
                "duration_ms": 0
            })

    success_count = sum(1 for r in results if r["success"])

    return {
        "total": len(article_ids),
        "success": success_count,
        "failed": len(article_ids) - success_count,
        "results": results
    }


class WorkerSettings:
    """ARQ worker configuration.

    This class defines the worker settings for ARQ, including
    which functions to execute and Redis connection details.

    Attributes:
        functions: List of task functions to register
        redis_settings: Redis connection settings
        max_jobs: Maximum concurrent jobs
        job_timeout: Maximum execution time per job (seconds)
        keep_result: How long to keep job results (seconds)
    """

    functions = [generate_article_task, batch_generate_task]
    redis_settings = RedisSettings.from_dsn(str(settings.redis_url))
    max_jobs = 10
    job_timeout = 300  # 5 minutes
    keep_result = 3600  # 1 hour


# Helper function to create Redis pool
async def get_redis_pool():
    """Create and return Redis pool for ARQ.

    Returns:
        ARQ Redis pool

    Example:
        >>> pool = await get_redis_pool()
        >>> await pool.enqueue_job('generate_article_task', 'uuid')
        >>> await pool.close()
    """
    return await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))
