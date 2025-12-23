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
  - Anthropic Claude API
  - WordPress REST API
  - Google Sheets API

### フロントエンド
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **State Management**: React Query + Zustand
- **Styling**: Tailwind CSS

### インフラ
- **開発環境**: Docker Compose
- **本番環境**: Railway (Backend) + Vercel (Frontend)

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

以下の環境変数を設定:

```env
# Anthropic (Claude API)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# WordPress
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Google Sheets
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
- [ ] **Task 03**: FastAPI基本構造
- [ ] **Task 04**: Google Sheets連携
- [ ] **Task 05**: WordPress連携
- [ ] **Task 06**: Claude API連携
- [ ] **Task 07**: 記事生成パイプライン
- [ ] **Task 08**: バッチ処理実装
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
