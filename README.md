# 記事自動生成システム

キーワードを入力するだけで、Google Gemini AIが自動的にブログ記事を生成するシステムです。

## 🎯 できること

- **記事自動生成**: キーワードから2000〜6000文字の記事を自動生成
- **一括生成**: 最大100件の記事をまとめて生成
- **WordPress自動投稿**: 生成した記事をWordPressに自動投稿（オプション）
- **進捗管理**: Google Sheetsで記事の状態を管理（オプション）

## 🚀 クイックスタート

### 必要なもの

1. **Docker Desktop** - [ダウンロード](https://www.docker.com/products/docker-desktop/)
2. **Node.js 18以上** - [ダウンロード](https://nodejs.org/)
3. **Google Gemini API キー**（無料） - [取得はこちら](https://makersuite.google.com/app/apikey)

### セットアップ（5分）

```bash
# 1. プロジェクトをダウンロード
git clone https://github.com/your-username/article-generator.git
cd article-generator

# 2. 環境変数ファイルを作成
cp .env.example .env

# 3. .envファイルを開いて、Google Gemini API キーを設定
# GOOGLE_API_KEY=your-api-key-here

# 4. バックエンドを起動
docker-compose up -d

# 5. データベースをセットアップ
docker-compose exec backend_app alembic upgrade head

# 6. フロントエンドを起動
cd src/frontend
npm install
npm run dev
```

### 使い方（3ステップ）

1. **ブラウザで開く**: http://localhost:3000
2. **カテゴリを作成**: 「カテゴリ管理」→「カテゴリを作成」
3. **記事を生成**: 「記事一覧」→「記事を作成」→ キーワード入力 → 「生成」

## 📋 環境変数の設定

`.env` ファイルで以下を設定してください：

```env
# 【必須】記事生成に必要
GOOGLE_API_KEY=your-google-api-key-here
SECRET_KEY=any-random-32-character-string

# 【オプション】WordPress連携を使う場合
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx

# 【オプション】Google Sheets連携を使う場合
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

### 環境変数の取得方法

| 変数 | 取得方法 |
|------|---------|
| `GOOGLE_API_KEY` | [Google AI Studio](https://makersuite.google.com/app/apikey)で「Create API Key」をクリック |
| `SECRET_KEY` | `openssl rand -hex 32` で生成、または任意の32文字以上の文字列 |
| `WORDPRESS_APP_PASSWORD` | WordPress管理画面 → ユーザー → プロフィール → アプリケーションパスワード |
| `GOOGLE_CREDENTIALS_JSON` | [詳細ガイド](./GOOGLE_SHEETS_SETUP.md)を参照 |

## 🔌 オプション機能の設定

### WordPress連携

WordPressに自動投稿したい場合は、[WORDPRESS_SETUP.md](./WORDPRESS_SETUP.md)を参照してください。

**重要**: WordPress.com無料サイトでは動作しません。セルフホストWordPressまたはWordPress.com Businessプラン以上が必要です。

### Google Sheets連携

記事の進捗をスプレッドシートで管理したい場合は、[GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)を参照してください。

## 🔧 トラブルシューティング

### 記事生成が失敗する

```bash
# APIキーを確認
cat .env | grep GOOGLE_API_KEY

# バックエンドを再起動
docker-compose restart backend_app

# ログを確認
docker-compose logs backend_app --tail=50
```

### バックエンドが起動しない

```bash
# コンテナを再起動
docker-compose down
docker-compose up -d

# 状態を確認
docker-compose ps
```

### フロントエンドが起動しない

```bash
cd src/frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### その他のエラー

- **データベース接続エラー**: `docker-compose up -d app_db` でDBを起動
- **WordPress接続エラー**: [WORDPRESS_SETUP.md](./WORDPRESS_SETUP.md)を確認
- **Google Sheets接続エラー**: [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)を確認

## 📖 詳細ドキュメント

- **[GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)** - Google Sheets連携の設定方法
- **[WORDPRESS_SETUP.md](./WORDPRESS_SETUP.md)** - WordPress連携の設定方法
- **[AGENTS.md](./AGENTS.md)** - 開発者向けガイドライン

## 🛠 技術スタック

- **バックエンド**: FastAPI + PostgreSQL + Redis
- **フロントエンド**: Next.js 16 + TypeScript + Tailwind CSS
- **AI**: Google Gemini API
- **外部連携**: WordPress REST API, Google Sheets API

## 📂 ディレクトリ構造

```
article-generator/
├── src/
│   ├── backend/          # FastAPI バックエンド
│   └── frontend/         # Next.js フロントエンド
├── docker-compose.yml    # Docker設定
├── .env                  # 環境変数（自分で作成）
├── .env.example          # 環境変数テンプレート
└── README.md             # このファイル
```

## 🆘 サポート

問題が発生した場合:

1. [トラブルシューティング](#トラブルシューティング)を確認
2. `docker-compose logs backend_app` でログを確認
3. [GitHub Issues](https://github.com/your-username/article-generator/issues)で質問

## 📄 ライセンス

MIT License
