"""カテゴリドメインモデル"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.database import Base

if TYPE_CHECKING:
    from app.features.articles.domain.models import Article
    from app.features.prompt_templates.domain.models import PromptTemplate


class Category(Base):
    """カテゴリモデル"""

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    sheet_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sheet_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sheets_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # リレーション
    prompt_templates: Mapped[list["PromptTemplate"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )
    articles: Mapped[list["Article"]] = relationship(back_populates="category")
