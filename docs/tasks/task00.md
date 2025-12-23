# タスク00: 事前準備（人間作業）

## 📋 概要

| 項目 | 内容 |
|------|------|
| 担当 | 👤 人間（あなた） |
| 所要時間 | 1-2時間 |
| 前提条件 | なし |
| 成果物 | `.env` ファイルに記載する各種認証情報 |

---

## 🔑 1. Anthropic API キーの取得

### 手順

1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウントを作成またはログイン
3. 左メニューから「API Keys」を選択
4. 「Create Key」をクリック
5. キー名を入力（例：`article-generator`）
6. 生成されたキーをコピー

### 取得する値

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🌐 2. WordPress 設定

### 2.1 アプリケーションパスワードの作成

1. WordPress 管理画面にログイン
2. 「ユーザー」→「プロフィール」に移動
3. ページ下部の「アプリケーションパスワード」セクションを探す
4. 「新しいアプリケーションパスワードの名前」に `article-generator` と入力
5. 「新しいアプリケーションパスワードを追加」をクリック
6. 表示されたパスワードをコピー

### 2.2 REST API の動作確認

```bash
curl https://your-site.com/wp-json/wp/v2/posts
```

### 取得する値

```
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your-admin-username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

---

## 📊 3. Google Cloud / Sheets API 設定

### 3.1 プロジェクト作成と API 有効化

1. [Google Cloud Console](https://console.cloud.google.com/) で新しいプロジェクトを作成
2. 以下の API を有効化:
   - Google Sheets API
   - Google Drive API

### 3.2 サービスアカウントの作成

1. 「API とサービス」→「認証情報」→「認証情報を作成」→「サービスアカウント」
2. サービスアカウント名：`article-generator-sa`
3. 「キー」タブ →「鍵を追加」→「新しい鍵を作成」→ JSON
4. ダウンロードした JSON を1行にして環境変数に設定

### 取得する値

```
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key":"..."}
```

---

## 📝 4. 環境変数ファイルの作成

以下の内容で `.env.example` ファイルを作成:

```env
# ===========================================
# 記事自動生成システム 環境変数
# ===========================================

# ----- Anthropic (Claude API) -----
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# ----- WordPress -----
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# ----- Google Sheets -----
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}

# ----- Database -----
DATABASE_URL=postgresql://postgres:postgres@db:5432/article_generator

# ----- Redis -----
REDIS_URL=redis://redis:6379

# ----- Application -----
APP_ENV=development
DEBUG=true
SECRET_KEY=your-random-secret-key-at-least-32-chars
FRONTEND_URL=http://localhost:3000
```

---

## ✅ 完了チェックリスト

- [ ] Anthropic API キーを取得した
- [ ] WordPress アプリケーションパスワードを作成した
- [ ] Google Cloud プロジェクトを作成し、API を有効化した
- [ ] サービスアカウントを作成し、JSON キーをダウンロードした
- [ ] `.env.example` ファイルを作成した

---

## 📌 次のタスク

タスク00完了後、**タスク01: プロジェクト初期化** に進んでください。
