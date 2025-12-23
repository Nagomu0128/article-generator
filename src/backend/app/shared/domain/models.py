"""すべてのドメインモデルを集約"""

# すべてのモデルをインポート（SQLAlchemyのリレーションシップ解決のため）
from app.features.categories.domain.models import Category
from app.features.prompt_templates.domain.models import PromptTemplate
from app.features.articles.domain.models import Article
from app.features.job_logs.domain.models import JobLog

__all__ = ["Category", "PromptTemplate", "Article", "JobLog"]
