# 記事自動生成システム

キーワードを入力すると、Claude APIが記事を自動生成します。WordPressへの投稿やGoogle Sheetsでの進捗管理もできます。

## 機能

- キーワードから2000〜6000文字の記事を自動生成
- 最大100件の記事を一括生成
- 生成した記事をWordPressに自動投稿（オプション）
- Google Sheetsで進捗を管理（オプション）

## セットアップ

### 必要なもの

- Docker Desktop
- Node.js 18以上
- Claude API Key（[Anthropic Console](https://console.anthropic.com/)で取得）

### インストール

```bash
git clone https://github.com/your-username/article-generator.git
cd article-generator
cp .env.example .env
```

### 環境変数

`.env` ファイルを編集：

```env
# 必須
ANTHROPIC_API_KEY=sk-ant-api03-...
SECRET_KEY=ランダムな32文字以上の文字列

# WordPress連携を使う場合
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Google Sheets連携を使う場合
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

- **ANTHROPIC_API_KEY**: [Anthropic Console](https://console.anthropic.com/)で取得
- **SECRET_KEY**: `openssl rand -hex 32` で生成
- **WORDPRESS_APP_PASSWORD**: WordPress管理画面 → ユーザー → プロフィール → アプリケーションパスワード
- **GOOGLE_CREDENTIALS_JSON**: [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md)を参照

### 起動

```bash
# バックエンド
docker-compose up -d
docker-compose exec backend_app alembic upgrade head

# フロントエンド
cd src/frontend
npm install
npm run dev
```

http://localhost:3000 を開く

## 使い方

1. カテゴリを作成
2. 記事を作成してキーワードを入力
3. 生成ボタンをクリック
4. 生成された記事を確認・編集
5. 必要に応じてWordPressに投稿

## WordPress連携

WordPressに自動投稿する場合は [WORDPRESS_SETUP.md](./WORDPRESS_SETUP.md) を参照。

注意: WordPress.com無料プランでは動作しません。セルフホストWordPressまたはWordPress.com Businessプラン以上が必要です。

## Google Sheets連携

スプレッドシートで進捗管理する場合は [GOOGLE_SHEETS_SETUP.md](./GOOGLE_SHEETS_SETUP.md) を参照。

## トラブルシューティング

記事生成が失敗する場合:

```bash
cat .env | grep ANTHROPIC_API_KEY  # APIキー確認
docker-compose restart backend_app  # 再起動
docker-compose logs backend_app     # ログ確認
```

バックエンドが起動しない場合:

```bash
docker-compose down
docker-compose up -d
docker-compose ps
```

フロントエンドが起動しない場合:

```bash
cd src/frontend
rm -rf node_modules
npm install
npm run dev
```

## 技術構成

- バックエンド: FastAPI + PostgreSQL + Redis
- フロントエンド: Next.js 16 + TypeScript + Tailwind CSS
- AI: Anthropic Claude API
- 外部連携: WordPress REST API, Google Sheets API

## ライセンス

MIT License
