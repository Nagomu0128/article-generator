"""記事ドメインモデル"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.domain.enums import ArticleStatus
from app.shared.infrastructure.database import Base

if TYPE_CHECKING:
    from app.features.categories.domain.models import Category
    from app.features.job_logs.domain.models import JobLog
    from app.features.prompt_templates.domain.models import PromptTemplate


class Article(Base):
    """記事モデル"""

    __tablename__ = "articles"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    category_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    prompt_template_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    keyword: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus), default=ArticleStatus.PENDING
    )
    wp_post_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wp_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    wp_published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # リレーション
    category: Mapped["Category"] = relationship(back_populates="articles")
    prompt_template: Mapped[Optional["PromptTemplate"]] = relationship(
        back_populates="articles"
    )
    job_logs: Mapped[list["JobLog"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
