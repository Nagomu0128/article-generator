# Changelog

このファイルは、記事自動生成システムの重要な変更を記録します。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいており、
バージョニングは [Semantic Versioning](https://semver.org/lang/ja/) に従います。

## [Unreleased]

### Task 08 完了 - 2025-12-24

#### 追加
- ARQワーカーシステム（`app/workers/tasks.py`）
  - `generate_article_task` - 単一記事の非同期生成タスク
  - `batch_generate_task` - バッチ記事生成タスク
  - `WorkerSettings` - ARQワーカー設定
  - `get_redis_pool` - Redis接続プールヘルパー
- バッチ処理API（`features/batch/`）
  - `POST /api/batch/generate` - バッチ生成エンドポイント（最大100件）
  - `GET /api/batch/status/{job_id}` - ジョブステータス監視
  - `POST /api/batch/generate/single/{article_id}` - 単一記事の非同期生成
- バッチ処理スキーマ（`BatchGenerateRequest`, `BatchResponse`, `JobStatusResponse`）
- Docker Composeワーカーサービス

#### 変更
- docker-compose.yml: ARQワーカーサービス追加
- main.py: バッチAPIルーター追加
- README.md: Task 08完了マーク、バッチAPIエンドポイント追加

#### 統合
- Task 07 (記事生成パイプライン) との統合
- Redis + ARQによる非同期ジョブキュー

---

### Task 07 完了 - 2025-12-24

#### 追加
- 記事生成パイプライン（`ArticleGenerator`）の実装
- `POST /api/generate` エンドポイント - 記事生成API
- `POST /api/generate/regenerate/{article_id}` エンドポイント - 記事再生成API
- 記事生成リクエスト/レスポンススキーマ（`GenerateRequest`, `GenerateResponse`）
- 記事生成オーケストレーター（353行）
  - Claude APIによるコンテンツ生成
  - プロンプトテンプレートの自動適用
  - レスポンスの解析と検証
  - データベースへの自動保存
  - Google Sheetsへの自動同期
  - ジョブログの自動記録
  - エラーハンドリングとリトライ処理
- ユニットテスト（`test_article_generator.py`）
  - 正常系テスト
  - エラーハンドリングテスト
  - バリデーションテスト

#### 変更
- README.md: 使い方セクション追加
- README.md: 主要APIエンドポイント一覧追加
- README.md: 実装済み機能の詳細追加
- README.md: Task 07を完了済みにマーク
- `main.py`: 生成APIルーターを追加

#### 統合
- Task 06 (Claude API) との統合
- Task 05 (WordPress) との統合
- Task 04 (Google Sheets) との統合
- Task 03 (FastAPI) との統合
- Task 02 (Database) との統合

---

### Task 06 完了 - 2025-12-24

#### 追加
- Claude API連携サービス（`claude_service.py`）
- プロンプトビルダー（`prompt_builder.py`）
- レスポンスパーサー（`response_parser.py`）
- LLM基底クラス（`BaseLLMService`, `LLMConfig`, `LLMResponse`）
- リトライ処理（tenacity使用）

---

### Task 05 完了 - 2025-12-24

#### 追加
- WordPress連携サービス（`wordpress_service.py`）
- Markdown → HTML変換（`markdown_converter.py`）
- `POST /api/wordpress/draft` エンドポイント - 下書き作成
- `POST /api/wordpress/publish` エンドポイント - 記事公開
- WordPress投稿スキーマ（`PublishRequest`, `PublishResponse`）

---

### Task 04 完了 - 2025-12-24

#### 追加
- Google Sheets連携サービス（`google_sheets_service.py`）
- `POST /api/sheets/create` エンドポイント - スプレッドシート作成
- スプレッドシート作成スキーマ（`CreateSheetRequest`, `CreateSheetResponse`）
- ステータス同期機能

---

### Task 03 完了 - 2025-12-23

#### 追加
- FastAPI基本構造
- カテゴリCRUD API（`/api/categories`）
- 記事CRUD API（`/api/articles`）
- ページネーション機能
- ステータスフィルタリング

---

### Task 02 完了 - 2025-12-23

#### 追加
- データベース設計（SQLAlchemy + PostgreSQL）
- Alembicマイグレーション
- モデル定義（Category, Article, PromptTemplate, JobLog）
- Feature First アーキテクチャ採用

---

### Task 01 完了 - 2025-12-23

#### 追加
- プロジェクト初期構造
- Docker Compose環境
- Next.jsフロントエンド基本構造
- FastAPIバックエンド基本構造

---

### Task 00 完了 - 2025-12-23

#### 追加
- 環境変数設定
- APIキー取得手順
