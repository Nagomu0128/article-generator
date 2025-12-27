"""Batch processing API routes.

This module provides endpoints for batch article generation
and job status monitoring using ARQ background workers.
"""
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.features.batch.domain.schemas import (
    BatchGenerateRequest,
    BatchResponse,
    JobStatusResponse,
)
from app.workers.tasks import get_redis_pool

settings = get_settings()
router = APIRouter(prefix="/batch", tags=["Batch"])


@router.post("/generate", response_model=BatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def batch_generate(data: BatchGenerateRequest):
    """
    バッチ記事生成を開始

    複数の記事を非同期バッチ処理で生成します。
    ジョブIDが返却されるので、/batch/status/{job_id}で進捗を確認できます。

    Args:
        data: バッチ生成リクエスト

    Returns:
        ジョブID、記事数、メッセージ

    Raises:
        HTTPException: Redis接続エラーの場合

    Example:
        POST /api/batch/generate
        {
            "article_ids": [
                "123e4567-e89b-12d3-a456-426614174000",
                "234e5678-e89b-12d3-a456-426614174001"
            ],
            "options": {
                "temperature": 0.7,
                "char_count_min": 2000,
                "char_count_max": 4000
            }
        }

        Response:
        {
            "job_id": "abc123...",
            "total": 2,
            "message": "Batch job started for 2 articles"
        }
    """
    try:
        pool = await get_redis_pool()
        job_id = str(uuid4())

        # Enqueue batch job
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue batch job: {str(e)}"
        )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_batch_status(job_id: str):
    """
    バッチジョブのステータスを取得

    Args:
        job_id: ジョブID（batch_generateのレスポンスから取得）

    Returns:
        ジョブステータス（queued/in_progress/complete/not_found）と結果

    Example:
        GET /api/batch/status/abc123...

        Response (processing):
        {
            "job_id": "abc123...",
            "status": "in_progress",
            "result": null
        }

        Response (complete):
        {
            "job_id": "abc123...",
            "status": "complete",
            "result": {
                "total": 2,
                "success": 2,
                "failed": 0,
                "results": [...]
            }
        }
    """
    try:
        from arq.jobs import Job
        from arq.constants import job_key_prefix

        pool = await get_redis_pool()

        # Get job info from Redis
        job_key = job_key_prefix + job_id
        job_exists = await pool.exists(job_key)

        if not job_exists:
            await pool.close()
            return JobStatusResponse(
                job_id=job_id,
                status="not_found",
                result=None
            )

        # Create job instance
        job = Job(job_id=job_id, redis=pool)
        info = await job.info()

        job_status = "unknown"
        result = None

        if info:
            # Map ARQ job status to our status
            if info.success is True:
                job_status = "complete"
                try:
                    result = await job.result()
                except Exception:
                    pass
            elif info.success is False:
                job_status = "failed"
            elif info.job_try and info.job_try > 0:
                job_status = "in_progress"
            else:
                job_status = "queued"

        await pool.close()

        return JobStatusResponse(
            job_id=job_id,
            status=job_status,
            result=result
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.post("/generate/single/{article_id}", response_model=BatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_single_generation(article_id: str):
    """
    単一記事の非同期生成をエンキュー

    1件の記事をバックグラウンドで生成します。
    同期的な生成が不要な場合に使用します。

    Args:
        article_id: 記事UUID

    Returns:
        ジョブID、記事数、メッセージ

    Example:
        POST /api/batch/generate/single/123e4567-e89b-12d3-a456-426614174000
    """
    try:
        pool = await get_redis_pool()
        job_id = str(uuid4())

        await pool.enqueue_job(
            "generate_article_task",
            article_id,
            None,  # No options
            _job_id=job_id
        )
        await pool.close()

        return BatchResponse(
            job_id=job_id,
            total=1,
            message=f"Article generation job started"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue job: {str(e)}"
        )
