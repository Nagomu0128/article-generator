"""WordPress API ルート"""

from datetime import datetime

from fastapi import APIRouter, status

from app.features.articles.infrastructure.repository import ArticleRepository
from app.features.job_logs.domain.models import JobLog
from app.features.wordpress.domain.schemas import PublishRequest, PublishResponse
from app.shared.domain.enums import ArticleStatus, JobStatus, JobType
from app.shared.domain.exceptions import NotFoundError, ValidationError
from app.shared.infrastructure.dependencies import DbSession
from app.shared.infrastructure.services.markdown_converter import markdown_converter
from app.shared.infrastructure.services.wordpress_service import (
    PostStatus,
    wordpress_service,
)

router = APIRouter(prefix="/wordpress", tags=["WordPress"])


@router.post("/draft", response_model=PublishResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(data: PublishRequest, db: DbSession):
    """WordPress下書き作成

    記事をWordPressに下書きとして投稿します。
    記事にコンテンツが存在し、まだWordPress投稿IDが割り当てられていない必要があります。
    """
    repo = ArticleRepository(db)
    article = await repo.find_by_id(data.article_id)

    if not article:
        raise NotFoundError("Article", str(data.article_id))

    if not article.content:
        raise ValidationError("Article has no content")

    if article.wp_post_id:
        raise ValidationError("Article already has WordPress post")

    # Markdown → HTML変換
    html_content = markdown_converter.convert(article.content)

    # WordPress投稿作成
    wp_post = await wordpress_service.create_post(
        title=article.title or article.keyword,
        content=html_content,
        status=PostStatus.DRAFT,
    )

    # 記事情報更新
    article.wp_post_id = wp_post.id
    article.wp_url = wp_post.link

    # ジョブログ記録
    job_log = JobLog(
        article_id=article.id,
        job_type=JobType.PUBLISH,
        status=JobStatus.SUCCESS,
    )
    db.add(job_log)

    await db.flush()
    await db.refresh(article)

    return PublishResponse(
        article_id=article.id,
        wp_post_id=wp_post.id,
        wp_url=wp_post.link,
        status=wp_post.status,
    )


@router.post("/publish", response_model=PublishResponse)
async def publish_article(data: PublishRequest, db: DbSession):
    """WordPress記事公開

    WordPress下書きを公開状態に変更します。
    事前に下書きが作成されている必要があります。
    """
    repo = ArticleRepository(db)
    article = await repo.find_by_id(data.article_id)

    if not article:
        raise NotFoundError("Article", str(data.article_id))

    if not article.wp_post_id:
        raise ValidationError("Create draft first")

    # WordPress投稿公開
    wp_post = await wordpress_service.publish_post(article.wp_post_id)

    # 記事ステータス更新
    article.status = ArticleStatus.PUBLISHED
    article.wp_url = wp_post.link
    article.wp_published_at = datetime.utcnow()

    # TODO: タスク04完了後、Google Sheetsへの同期を追加
    # if category and category.sheet_id:
    #     sheets_service.update_article_status(...)

    await db.flush()
    await db.refresh(article)

    return PublishResponse(
        article_id=article.id,
        wp_post_id=wp_post.id,
        wp_url=wp_post.link,
        status=wp_post.status,
    )
