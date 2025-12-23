# タスク10: 結合テスト・デプロイ

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 🤖 AI + 👤 人間 |
| 所要時間 | 2時間 |
| 前提条件 | タスク09完了 |
| 成果物 | E2Eテスト、本番デプロイ |

---

## 🤖 AI Agent の作業

### E2E テストスクリプト

**backend/tests/test_e2e.py**

```python
"""E2E テスト"""
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_full_workflow(client: AsyncClient):
    """フルワークフローテスト"""

    # 1. カテゴリ作成
    res = await client.post("/api/categories", json={"name": "E2Eテスト", "slug": "e2e-test"})
    assert res.status_code == 201
    category_id = res.json()["id"]

    # 2. 記事作成
    res = await client.post("/api/articles", json={"category_id": category_id, "keyword": "テストKW"})
    assert res.status_code == 201
    article_id = res.json()["id"]
    assert res.json()["status"] == "pending"

    # 3. 記事取得
    res = await client.get(f"/api/articles/{article_id}")
    assert res.status_code == 200
    assert res.json()["keyword"] == "テストKW"

    # 4. カテゴリ削除（記事があるので失敗するはず）
    res = await client.delete(f"/api/categories/{category_id}")
    assert res.status_code == 409

    # 5. 記事削除
    res = await client.delete(f"/api/articles/{article_id}")
    assert res.status_code == 204

    # 6. カテゴリ削除（成功）
    res = await client.delete(f"/api/categories/{category_id}")
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
```

### GitHub Actions CI

**.github/workflows/ci.yml**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx

      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
          SECRET_KEY: test-secret-key
          ANTHROPIC_API_KEY: test-key
          WORDPRESS_URL: https://example.com
          WORDPRESS_USERNAME: test
          WORDPRESS_APP_PASSWORD: test
          GOOGLE_CREDENTIALS_JSON: '{}'
        run: |
          cd backend
          pytest -v

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install and build
        run: |
          cd frontend
          npm ci
          npm run build
```

---

## 👤 人間の作業

### 1. 本番環境変数の設定

**Railway / Render での環境変数設定:**

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
WORDPRESS_URL=https://your-production-site.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=<本番用の長いランダム文字列>
APP_ENV=production
DEBUG=false
FRONTEND_URL=https://your-frontend-domain.vercel.app
```

### 2. デプロイ手順

#### Backend (Railway)

1. [Railway](https://railway.app/) にログイン
2. 「New Project」→「Deploy from GitHub repo」
3. リポジトリを選択、`backend` ディレクトリを指定
4. 環境変数を設定
5. PostgreSQL と Redis のアドオンを追加

#### Frontend (Vercel)

1. [Vercel](https://vercel.com/) にログイン
2. 「Import Project」→ GitHub リポジトリを選択
3. Root Directory を `frontend` に設定
4. 環境変数を設定:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
   ```
5. デプロイ

### 3. 動作確認チェックリスト

- [ ] フロントエンドにアクセスできる
- [ ] ログイン/認証が動作する（実装している場合）
- [ ] カテゴリの作成・一覧表示ができる
- [ ] Google Sheets の作成・連携ができる
- [ ] 記事の作成・一覧表示ができる
- [ ] 記事生成が動作する（Claude API）
- [ ] WordPress への下書き投稿ができる
- [ ] WordPress への公開ができる
- [ ] Google Sheets に状態が反映される
- [ ] バッチ生成が動作する

### 4. 監視設定（推奨）

1. **エラー監視**: Sentry の導入
2. **ログ監視**: Railway / Render のログ確認
3. **アラート**: Slack / Discord への通知設定

---

## 📊 最終アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet                                  │
└─────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│         Vercel              │   │        Railway              │
│  ┌───────────────────────┐  │   │  ┌───────────────────────┐  │
│  │   Next.js Frontend    │  │   │  │   FastAPI Backend     │  │
│  │   (Static + SSR)      │──┼───┼─▶│   (API + Worker)      │  │
│  └───────────────────────┘  │   │  └───────────────────────┘  │
└─────────────────────────────┘   │           │                  │
                                  │           ▼                  │
                                  │  ┌───────────────────────┐  │
                                  │  │     PostgreSQL        │  │
                                  │  └───────────────────────┘  │
                                  │           │                  │
                                  │           ▼                  │
                                  │  ┌───────────────────────┐  │
                                  │  │       Redis           │  │
                                  │  └───────────────────────┘  │
                                  └─────────────────────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
          │   Claude API    │       │  Google Sheets  │       │    WordPress    │
          │   (Anthropic)   │       │      API        │       │    REST API     │
          └─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## ✅ 全体完了チェックリスト

### 事前準備（👤 人間）
- [ ] Anthropic API キー取得
- [ ] WordPress アプリケーションパスワード作成
- [ ] Google Cloud プロジェクト作成
- [ ] Google Sheets API / Drive API 有効化
- [ ] サービスアカウント作成

### バックエンド（🤖 AI）
- [ ] プロジェクト構造作成
- [ ] データベースモデル実装
- [ ] マイグレーション実行
- [ ] CRUD API 実装
- [ ] Google Sheets 連携実装
- [ ] WordPress 連携実装
- [ ] Claude API 連携実装
- [ ] 記事生成パイプライン実装
- [ ] バッチ処理実装

### フロントエンド（🤖 AI）
- [ ] Next.js プロジェクト作成
- [ ] 共通レイアウト実装
- [ ] ダッシュボード画面
- [ ] カテゴリ管理画面
- [ ] 記事管理画面
- [ ] 記事詳細・プレビュー画面

### デプロイ（🤖 AI + 👤 人間）
- [ ] E2E テスト作成
- [ ] CI/CD パイプライン設定
- [ ] 本番環境変数設定
- [ ] バックエンドデプロイ
- [ ] フロントエンドデプロイ
- [ ] 動作確認

---

## 🎉 完了

おめでとうございます！記事自動生成システムの実装が完了しました。

### 今後の拡張案

1. **RAG 機能追加**: ベクトルDBを導入し、既存記事を参照した生成
2. **認証機能**: NextAuth.js による認証追加
3. **画像生成**: DALL-E / Stable Diffusion 連携
4. **SEO 分析**: 生成記事の SEO スコア自動計算
5. **A/B テスト**: プロンプトテンプレートの効果測定

---

## 📌 注意事項

このタスクは AI Agent と人間の協力が必要です。AI Agent は技術的な実装を担当し、人間は本番環境の設定とデプロイを担当してください。
