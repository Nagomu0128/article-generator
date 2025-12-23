"""ジョブログPydanticスキーマ"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.domain.enums import JobStatus, JobType


class JobLogCreate(BaseModel):
    """ジョブログ作成リクエスト"""

    article_id: UUID
    job_type: JobType
    status: JobStatus
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None


class JobLogResponse(BaseModel):
    """ジョブログレスポンス"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    article_id: UUID
    job_type: JobType
    status: JobStatus
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime
