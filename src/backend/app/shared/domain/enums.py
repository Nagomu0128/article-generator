"""共通Enum定義"""

import enum


class ArticleStatus(str, enum.Enum):
    """記事ステータス"""

    PENDING = "pending"
    GENERATING = "generating"
    FAILED = "failed"
    REVIEW_PENDING = "review_pending"
    REVIEWED = "reviewed"
    PUBLISHED = "published"


class JobType(str, enum.Enum):
    """ジョブタイプ"""

    GENERATE = "generate"
    PUBLISH = "publish"
    SYNC_SHEETS = "sync_sheets"


class JobStatus(str, enum.Enum):
    """ジョブステータス"""

    SUCCESS = "success"
    FAILED = "failed"
