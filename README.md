# 記事自動生成システム

Claude API、WordPress、Google Sheetsを統合した自動記事生成・管理システム

## 🏗️ アーキテクチャ

このプロジェクトは**クリーンアーキテクチャ**と**Feature Firstアーキテクチャ**に基づいて設計されています。詳細は[AGENTS.md](./AGENTS.md)を参照してください。

## 📦 技術スタック

### バックエンド
- **Framework**: FastAPI + uvicorn
- **Database**: PostgreSQL 15 + SQLAlchemy (async)
- **Cache/Queue**: Redis + ARQ
- **External APIs**:
  - Anthropic Claude API (記事生成)
  - WordPress REST API (記事投稿)
  - Google Sheets API (進捗管理)

### フロントエンド
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **State Management**: React Query + Zustand
- **Styling**: Tailwind CSS + shadcn/ui

### インフラ
- **開発環境**: Docker Compose
- **本番環境**: Railway (Backend) + Vercel (Frontend)

## ✨ 実装済み機能

### Task 00-07: コア機能 ✅

- ✅ **カテゴリ管理**: カテゴリのCRUD操作
- ✅ **記事管理**: 記事のCRUD操作、ステータス管理
- ✅ **記事生成**: Claude APIによる自動記事生成
  - プロンプトテンプレートのカスタマイズ
  - 生成パラメータの調整（文字数、temperature等）
  - レスポンスの自動検証
- ✅ **Google Sheets連携**:
  - スプレッドシート自動作成
  - 記事ステータスの自動同期
- ✅ **WordPress連携**:
  - 下書き作成
  - 記事公開
  - Markdown → HTML変換
- ✅ **ジョブログ**: 生成履歴の記録と追跡
- ✅ **エラーハンドリング**: リトライ処理、詳細なエラーログ

### Task 08: バッチ処理 ✅

- ✅ **ARQワーカー**: バックグラウンドジョブ処理
- ✅ **バッチ生成**: 複数記事の非同期一括生成（最大100件）
- ✅ **ジョブ管理**: ジョブステータス監視、進捗確認
- ✅ **単一記事の非同期生成**: レスポンス待機不要の生成キュー

### Task 09-10: 実装予定

- ⏳ **フロントエンド**: ダッシュボード、記事管理UI
- ⏳ **デプロイ**: 本番環境設定、CI/CD

## 🚀 セットアップ

### 前提条件

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 1. 環境変数の設定

プロジェクトルートに `.env.local` ファイルを作成:

```bash
cp .env.example .env.local
```

以下の環境変数を設定（**重要**: 実際のAPIキーが必要です）:

```env
# Anthropic (Claude API) ⚠️ 必須
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

# WordPress ⚠️ 必須（記事投稿を使う場合）
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Google Sheets ⚠️ 必須（Sheets連携を使う場合）
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# Database & Redis (開発環境ではデフォルトのまま)
DATABASE_URL=postgresql://postgres:postgres@app_db:5432/article_generator
REDIS_URL=redis://redis:6379

# Application
APP_ENV=development
DEBUG=true
SECRET_KEY=your-random-secret-key-at-least-32-chars
FRONTEND_URL=http://localhost:3000
```

**⚠️ 重要な注意事項:**
- `ANTHROPIC_API_KEY`: [Anthropic Console](https://console.anthropic.com/) で取得
- `WORDPRESS_APP_PASSWORD`: WordPressの「アプリケーションパスワード」で生成
- `GOOGLE_CREDENTIALS_JSON`: Google Cloud Console でサービスアカウントを作成し、JSON形式で取得
- APIキーが設定されていないと記事生成は失敗します

### 2. Docker環境の起動

```bash
# データベースとRedisを起動
docker compose up -d app_db redis

# バックエンドを起動
docker compose up -d backend_app
```

### 3. フロントエンドの起動

```bash
cd src/frontend
npm install
npm run dev
```

## ✅ 動作確認

- **バックエンド**: http://localhost:8000/health
- **API ドキュメント**: http://localhost:8000/docs
- **フロントエンド**: http://localhost:3000

### ヘルスチェック

```bash
# バックエンド
curl http://localhost:8000/health
# => {"status":"healthy","env":"development"}

# フロントエンド
curl -I http://localhost:3000
# => HTTP/1.1 200 OK
```

## 🚀 使い方

### 記事生成の基本フロー

```bash
# 1. カテゴリを作成
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name":"AI開発","slug":"ai-dev"}'
# => {"id":"<CATEGORY_ID>",...}

# 2. 記事を作成
curl -X POST http://localhost:8000/api/articles \
  -H "Content-Type: application/json" \
  -d '{"category_id":"<CATEGORY_ID>","keyword":"Claude API入門"}'
# => {"id":"<ARTICLE_ID>","status":"pending",...}

# 3. 記事を生成（Claude APIが記事を自動生成）
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "article_id":"<ARTICLE_ID>",
    "options":{
      "char_count_min":2000,
      "char_count_max":4000,
      "temperature":0.7
    }
  }'
# => {"success":true,"title":"Claude API入門ガイド","char_count":3245,...}

# 4. WordPress下書き作成
curl -X POST http://localhost:8000/api/wordpress/draft \
  -H "Content-Type: application/json" \
  -d '{"article_id":"<ARTICLE_ID>"}'
# => {"wp_post_id":123,"wp_url":"https://...",...}

# 5. WordPress公開
curl -X POST http://localhost:8000/api/wordpress/publish \
  -H "Content-Type: application/json" \
  -d '{"article_id":"<ARTICLE_ID>"}'
# => {"status":"publish",...}
```

### 主要APIエンドポイント

#### カテゴリ管理
- `GET /api/categories` - カテゴリ一覧
- `POST /api/categories` - カテゴリ作成
- `GET /api/categories/{id}` - カテゴリ取得
- `PATCH /api/categories/{id}` - カテゴリ更新
- `DELETE /api/categories/{id}` - カテゴリ削除

#### 記事管理
- `GET /api/articles` - 記事一覧（ページネーション、フィルタ対応）
- `POST /api/articles` - 記事作成
- `GET /api/articles/{id}` - 記事取得
- `PATCH /api/articles/{id}` - 記事更新
- `DELETE /api/articles/{id}` - 記事削除

#### 記事生成
- `POST /api/generate` - 記事生成（同期）
- `POST /api/generate/regenerate/{id}` - 記事再生成（同期）

#### バッチ処理
- `POST /api/batch/generate` - バッチ記事生成（非同期）
- `GET /api/batch/status/{job_id}` - ジョブステータス確認
- `POST /api/batch/generate/single/{id}` - 単一記事の非同期生成

#### Google Sheets連携
- `POST /api/sheets/create` - スプレッドシート作成

#### WordPress連携
- `POST /api/wordpress/draft` - 下書き作成
- `POST /api/wordpress/publish` - 記事公開

詳細なAPIドキュメントは http://localhost:8000/docs で確認できます。

## 📂 ディレクトリ構造

```
article-generator/
├── src/
│   ├── backend/              # FastAPI バックエンド
│   │   ├── app/
│   │   │   ├── core/        # 設定・共通ロジック
│   │   │   ├── shared/      # 共通モジュール
│   │   │   ├── features/    # 機能別実装 (Task02以降)
│   │   │   └── main.py      # アプリケーションエントリーポイント
│   │   ├── alembic/         # データベースマイグレーション
│   │   ├── tests/           # テスト
│   │   └── requirements.txt
│   └── frontend/            # Next.js フロントエンド
│       ├── app/             # App Router
│       ├── components/      # Reactコンポーネント
│       ├── lib/             # ユーティリティ
│       └── package.json
├── docker/                  # Dockerfile
├── docs/                    # タスクドキュメント
├── docker-compose.yml
├── AGENTS.md               # AI Agent開発ガイドライン
└── README.md
```

## 📋 実装タスク

実装は以下のタスクに従って進めます：

- [x] **Task 00**: 事前準備（API キー取得）
- [x] **Task 01**: プロジェクト初期化
- [x] **Task 02**: データベース設計
- [x] **Task 03**: FastAPI基本構造（CRUD API）
- [x] **Task 04**: Google Sheets連携
- [x] **Task 05**: WordPress連携
- [x] **Task 06**: Claude API連携
- [x] **Task 07**: 記事生成パイプライン
- [x] **Task 08**: バッチ処理実装
- [ ] **Task 09**: フロントエンド実装
- [ ] **Task 10**: 結合テスト・デプロイ

詳細は [docs/tasks/](./docs/tasks/) を参照してください。

## 🧪 テスト

```bash
# バックエンドテスト
cd src/backend
pytest

# フロントエンドテスト
cd src/frontend
npm test
```

## 📝 開発ガイドライン

AI Agentが本プロジェクトでコードを実装する際は、[AGENTS.md](./AGENTS.md)のガイドラインに従ってください。

### 主要原則

1. **クリーンアーキテクチャ（DDD思想）**
2. **Feature First アーキテクチャ**
3. **変数名の一貫性**
4. **ファイル分割（100行以内）**
5. **DRY原則**
6. **拡張性の確保**
7. **重要箇所へのテスト記述**

## 🔗 リンク

- [タスク依存関係](./docs/tasks/DEPENDENCIES.md)
- [開発ガイドライン](./AGENTS.md)

## 📄 ライセンス

MIT License
