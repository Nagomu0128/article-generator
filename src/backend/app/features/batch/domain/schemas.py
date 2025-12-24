"""Batch processing Pydantic schemas.

This module defines request and response schemas for
batch job processing endpoints.
"""
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BatchGenerateRequest(BaseModel):
    """Batch article generation request.

    Attributes:
        article_ids: List of article UUIDs to generate (1-100)
        options: Optional generation options applied to all articles
    """

    article_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="記事IDリスト（最大100件）"
    )
    options: Optional[dict] = Field(
        None,
        description="生成オプション（全記事に適用）"
    )


class BatchResponse(BaseModel):
    """Batch job creation response.

    Attributes:
        job_id: UUID of the created batch job
        total: Total number of articles in the batch
        message: Human-readable status message
    """

    job_id: str = Field(..., description="バッチジョブID")
    total: int = Field(..., description="処理対象記事数")
    message: str = Field(..., description="ステータスメッセージ")


class JobStatusResponse(BaseModel):
    """Job status response.

    Attributes:
        job_id: UUID of the job
        status: Current job status (queued/in_progress/complete/not_found)
        result: Job result (only available when complete)
    """

    job_id: str = Field(..., description="ジョブID")
    status: str = Field(..., description="ジョブステータス")
    result: Optional[dict] = Field(None, description="ジョブ結果")


class BatchResultDetail(BaseModel):
    """Individual article generation result in batch.

    Attributes:
        success: Whether generation succeeded
        article_id: Article UUID
        title: Generated article title
        char_count: Character count
        errors: List of error messages
        duration_ms: Generation duration in milliseconds
    """

    success: bool
    article_id: str
    title: Optional[str]
    char_count: int
    errors: list[str]
    duration_ms: int


class BatchJobResult(BaseModel):
    """Complete batch job result.

    Attributes:
        total: Total number of articles processed
        success: Number of successful generations
        failed: Number of failed generations
        results: List of individual article results
    """

    total: int = Field(..., description="処理記事総数")
    success: int = Field(..., description="成功件数")
    failed: int = Field(..., description="失敗件数")
    results: list[BatchResultDetail] = Field(..., description="個別結果")
