"""Alembic環境設定"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Alembic Config object
config = context.config

# Python loggingの設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# アプリケーション設定とモデルのインポート
from app.core.config import get_settings
from app.shared.infrastructure.database import Base

# すべてのモデルをインポート（自動生成に必要）
from app.features.categories.domain.models import Category  # noqa
from app.features.prompt_templates.domain.models import PromptTemplate  # noqa
from app.features.articles.domain.models import Article  # noqa
from app.features.job_logs.domain.models import JobLog  # noqa

# メタデータ設定
target_metadata = Base.metadata

# 設定取得
settings = get_settings()


def get_url():
    """データベースURL取得"""
    # Alembicはsyncドライバーのpsycopgを使用
    return str(settings.database_url)


def run_migrations_offline() -> None:
    """オフラインモードでマイグレーション実行"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """オンラインモードでマイグレーション実行"""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
