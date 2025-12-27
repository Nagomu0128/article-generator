"""Article generation orchestrator.

This module orchestrates the complete article generation workflow:
1. Fetch article and template from database
2. Build prompts using PromptBuilder
3. Generate content using Claude API
4. Parse and validate response
5. Update database with results
6. Sync status to Google Sheets
7. Log job execution
"""
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.articles.application.prompt_builder import get_prompt_builder
from app.features.articles.application.response_parser import get_response_parser
from app.features.articles.domain.models import Article
from app.features.categories.domain.models import Category
from app.features.job_logs.domain.models import JobLog
from app.features.prompt_templates.domain.models import PromptTemplate
from app.features.sheets.infrastructure.google_sheets_service import sheets_service
from app.shared.domain.enums import ArticleStatus, JobStatus, JobType
from app.shared.domain.llm.base import LLMConfig
from app.shared.infrastructure.llm.claude_service import get_claude_service


@dataclass
class GenerationResult:
    """Result of article generation.

    Attributes:
        success: Whether generation was successful
        article_id: UUID of the generated article
        title: Extracted article title
        char_count: Character count of generated content
        errors: List of validation errors (empty if successful)
        duration_ms: Generation duration in milliseconds
    """
    success: bool
    article_id: UUID
    title: Optional[str]
    char_count: int
    errors: list[str]
    duration_ms: int


class ArticleGenerator:
    """Orchestrator for article generation workflow.

    This class coordinates all steps of article generation,
    from prompt building to database updates and external
    service synchronization.
    """

    def __init__(self):
        """Initialize article generator with dependencies."""
        self.prompt_builder = get_prompt_builder()
        self.response_parser = get_response_parser()
        self.claude_service = get_claude_service()

    async def generate(
        self,
        db: AsyncSession,
        article_id: UUID,
        options: Optional[dict] = None
    ) -> GenerationResult:
        """Generate article content using Claude API.

        This method orchestrates the complete generation workflow:
        1. Fetch article from database
        2. Update status to GENERATING
        3. Get active prompt template for category
        4. Build prompts with keyword and options
        5. Call Claude API to generate content
        6. Parse and validate response
        7. Update article in database
        8. Create job log entry
        9. Sync status to Google Sheets (if configured)

        Args:
            db: Database session
            article_id: UUID of article to generate
            options: Optional generation options (temperature, char_count, etc.)

        Returns:
            GenerationResult with success status and metadata

        Example:
            >>> generator = ArticleGenerator()
            >>> result = await generator.generate(
            ...     db, article_id,
            ...     {"temperature": 0.8, "char_count_min": 2000}
            ... )
            >>> print(result.success, result.title)
            True "AI開発入門ガイド"
        """
        start = datetime.utcnow()

        # Step 1: Fetch article
        article = await self._fetch_article(db, article_id)
        if not article:
            return GenerationResult(
                success=False,
                article_id=article_id,
                title=None,
                char_count=0,
                errors=["Article not found"],
                duration_ms=0
            )

        # Step 2: Update status to GENERATING
        article.status = ArticleStatus.GENERATING
        await db.flush()

        try:
            # Step 3: Get prompt template
            template = await self._get_template(db, article)

            # Step 4: Build prompts
            built_prompt = self.prompt_builder.build(
                template,
                article.keyword,
                options
            )

            # Step 5: Generate with Claude API
            llm_config = self._build_llm_config(options)
            llm_response = await self.claude_service.generate(
                built_prompt.system_prompt,
                built_prompt.user_prompt,
                llm_config
            )

            # Step 6: Parse and validate
            min_chars = options.get("char_count_min", 2000) if options else 2000
            max_chars = options.get("char_count_max", 6000) if options else 6000
            parsed = self.response_parser.parse(
                llm_response.content,
                min_chars=min_chars,
                max_chars=max_chars
            )

            # Step 7: Update article
            article.title = parsed.title or article.keyword
            article.content = parsed.content
            article.status = (
                ArticleStatus.REVIEW_PENDING if parsed.is_valid
                else ArticleStatus.FAILED
            )
            article.prompt_template_id = template.id if template else None
            article.metadata_ = {
                "char_count": parsed.char_count,
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "model": llm_response.model,
            }

            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

            # Step 8: Create job log
            db.add(JobLog(
                article_id=article.id,
                job_type=JobType.GENERATE,
                status=JobStatus.SUCCESS if parsed.is_valid else JobStatus.FAILED,
                error_message="; ".join(parsed.errors) if parsed.errors else None,
                duration_ms=duration_ms
            ))

            await db.flush()

            # Step 9: Sync to Google Sheets
            await self._sync_to_sheets(db, article)

            return GenerationResult(
                success=parsed.is_valid,
                article_id=article.id,
                title=parsed.title,
                char_count=parsed.char_count,
                errors=parsed.errors,
                duration_ms=duration_ms
            )

        except Exception as e:
            # Handle generation errors
            return await self._handle_error(db, article, start, e)

    async def _fetch_article(
        self,
        db: AsyncSession,
        article_id: UUID
    ) -> Optional[Article]:
        """Fetch article from database.

        Args:
            db: Database session
            article_id: Article UUID

        Returns:
            Article or None if not found
        """
        result = await db.execute(
            select(Article).where(Article.id == article_id)
        )
        return result.scalar_one_or_none()

    async def _get_template(
        self,
        db: AsyncSession,
        article: Article
    ) -> Optional[PromptTemplate]:
        """Get prompt template for article.

        Priority:
        1. Article's specific template (if set)
        2. Category's active template
        3. None (uses default prompts)

        Args:
            db: Database session
            article: Article to get template for

        Returns:
            PromptTemplate or None
        """
        # Check for article-specific template
        if article.prompt_template_id:
            result = await db.execute(
                select(PromptTemplate)
                .where(PromptTemplate.id == article.prompt_template_id)
            )
            return result.scalar_one_or_none()

        # Check for category's active template
        if article.category_id:
            result = await db.execute(
                select(PromptTemplate)
                .where(PromptTemplate.category_id == article.category_id)
                .where(PromptTemplate.is_active == True)  # noqa: E712
            )
            return result.scalar_one_or_none()

        return None

    def _build_llm_config(self, options: Optional[dict]) -> LLMConfig:
        """Build LLM configuration from options.

        Args:
            options: Optional configuration overrides

        Returns:
            LLMConfig with merged settings
        """
        config = LLMConfig()

        if options:
            if "temperature" in options:
                config.temperature = options["temperature"]
            if "max_tokens" in options:
                config.max_tokens = options["max_tokens"]
            if "model" in options:
                config.model = options["model"]

        return config

    async def _sync_to_sheets(
        self,
        db: AsyncSession,
        article: Article
    ) -> None:
        """Sync article status to Google Sheets.

        Args:
            db: Database session
            article: Article to sync

        Note:
            Errors are silently ignored to prevent
            Sheets issues from blocking generation.
        """
        try:
            # Get category to check for sheet_id
            result = await db.execute(
                select(Category).where(Category.id == article.category_id)
            )
            category = result.scalar_one_or_none()

            if category and category.sheet_id:
                sheets_service.update_article_status(
                    category.sheet_id,
                    article.keyword,
                    article.status,
                    article.title
                )
        except Exception:
            # Silently ignore Sheets errors
            pass

    async def _handle_error(
        self,
        db: AsyncSession,
        article: Article,
        start: datetime,
        error: Exception
    ) -> GenerationResult:
        """Handle generation error.

        Args:
            db: Database session
            article: Article being generated
            start: Generation start time
            error: Exception that occurred

        Returns:
            GenerationResult indicating failure
        """
        article.status = ArticleStatus.FAILED
        duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

        # Create error job log
        db.add(JobLog(
            article_id=article.id,
            job_type=JobType.GENERATE,
            status=JobStatus.FAILED,
            error_message=str(error),
            duration_ms=duration_ms
        ))

        await db.flush()

        return GenerationResult(
            success=False,
            article_id=article.id,
            title=None,
            char_count=0,
            errors=[str(error)],
            duration_ms=duration_ms
        )


@lru_cache
def get_article_generator() -> ArticleGenerator:
    """Get singleton instance of ArticleGenerator.

    Returns:
        ArticleGenerator instance
    """
    return ArticleGenerator()
