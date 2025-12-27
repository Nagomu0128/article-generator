# Google Sheets連携セットアップガイド

このガイドでは、Google Sheets連携を有効にする手順を説明します。

## 前提条件

- Googleアカウント
- Google Cloud Platformのプロジェクト（無料で作成可能）

## セットアップ手順

### 1. Google Cloud Consoleでプロジェクトを作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 画面上部のプロジェクト選択ドロップダウンをクリック
3. 「新しいプロジェクト」をクリック
4. プロジェクト名を入力（例: `article-generator`）
5. 「作成」をクリック

### 2. Google Sheets APIを有効化

1. 左側メニューから「APIとサービス」→「ライブラリ」を選択
2. 検索ボックスで「Google Sheets API」を検索
3. 「Google Sheets API」をクリック
4. 「有効にする」ボタンをクリック
5. 同様に「Google Drive API」も有効化（スプレッドシート作成に必要）

### 3. サービスアカウントを作成

1. 左側メニューから「IAMと管理」→「サービスアカウント」を選択
2. 「サービスアカウントを作成」をクリック
3. サービスアカウント名を入力（例: `article-generator-sheets`）
4. 「作成して続行」をクリック
5. 役割の選択は**スキップ**（後で権限を付与します）
6. 「完了」をクリック

### 4. サービスアカウントキーを作成

1. 作成したサービスアカウント名をクリック
2. 「キー」タブを選択
3. 「鍵を追加」→「新しい鍵を作成」をクリック
4. キーのタイプで「JSON」を選択
5. 「作成」をクリック
6. JSONファイルがダウンロードされます（**このファイルは安全に保管してください**）

### 5. 環境変数を設定

#### ダウンロードしたJSONファイルの内容を確認

JSONファイルを開くと以下のような内容になっています：

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "xxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...\n-----END PRIVATE KEY-----\n",
  "client_email": "article-generator-sheets@your-project.iam.gserviceaccount.com",
  "client_id": "xxxxx",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

#### .envファイルに設定

プロジェクトルートの`.env`ファイルを開き、以下の行を見つけます：

```env
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

この行を、ダウンロードしたJSONファイルの**内容全体を1行に**して置き換えます：

```env
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-id","private_key_id":"xxxxx","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBA...\n-----END PRIVATE KEY-----\n","client_email":"article-generator-sheets@your-project.iam.gserviceaccount.com","client_id":"xxxxx","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/..."}
```

**重要な注意点**:
- JSON全体を1行にコピーしてください
- 改行は`\n`のままにしてください
- ダブルクォート（`"`）をエスケープする必要はありません

### 6. バックエンドを再起動

環境変数を反映させるため、バックエンドを再起動します：

```bash
docker-compose restart backend

# または完全に再ビルド
docker-compose down
docker-compose up -d
```

### 7. 動作確認

1. フロントエンドでカテゴリページにアクセス
2. 任意のカテゴリカードで「スプレッドシート作成」ボタンをクリック
3. 成功すると「スプレッドシートを作成しました」というトーストが表示されます
4. ボタンが「スプレッドシートを開く」に変わります

### 8. スプレッドシートへのアクセス権限を付与

作成されたスプレッドシートは、デフォルトではサービスアカウントのみがアクセスできます。
自分のGoogleアカウントでアクセスするには：

1. 「スプレッドシートを開く」ボタンをクリック
2. 開いたスプレッドシートで右上の「共有」ボタンをクリック
3. 自分のメールアドレスを追加
4. 権限を「編集者」または「閲覧者」に設定
5. 「送信」をクリック

## トラブルシューティング

### エラー: "GOOGLE_CREDENTIALS_JSONの形式が不正です"

- JSONファイルの内容を正しくコピーできているか確認
- JSONが1行になっているか確認
- ダブルクォートが正しくエスケープされているか確認

### エラー: "認証失敗"

- Google Sheets APIが有効化されているか確認
- Google Drive APIが有効化されているか確認
- サービスアカウントキーが正しく作成されているか確認
- バックエンドを再起動したか確認

### エラー: "サービスアカウントのGoogle Driveストレージが不足しています" 🔥

**このエラーが最も一般的です！**

#### 原因
サービスアカウントで作成されたスプレッドシートは、そのサービスアカウントのGoogle Driveストレージを使用します。無料のGoogleアカウントでは、サービスアカウントに十分なストレージが割り当てられていない場合があります。

#### 解決方法1: Google Workspaceアカウントを使用（推奨）

Google Workspaceアカウント（有料）を使用している場合、この問題は発生しません。

#### 解決方法2: 手動でスプレッドシートを作成して共有（無料アカウント向け）

1. **自分のGoogleアカウントで新しいスプレッドシートを作成**
   - Google Sheetsにアクセス: https://sheets.google.com
   - 「空白」をクリックして新しいスプレッドシートを作成
   - タイトルを設定（例: `[AI開発] 記事管理`）

2. **ヘッダー行を追加**
   - 1行目に以下の列を追加：
     - A1: `KW`
     - B1: `記事タイトル`
     - C1: `ステータス`
     - D1: `公開URL`
     - E1: `WP投稿ID`
     - F1: `生成日時`
     - G1: `更新日時`
     - H1: `備考`
   - 1行目を選択して太字にする

3. **サービスアカウントと共有**
   - 右上の「共有」ボタンをクリック
   - サービスアカウントのメールアドレスを追加：
     ```
     article-generator-sheets@your-project-id.iam.gserviceaccount.com
     ```
   - 権限を「編集者」に設定
   - 「送信」をクリック

4. **スプレッドシートのIDとURLを取得**
   - URLをコピー: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - SPREADSHEET_IDの部分をメモ

5. **データベースに手動登録**（開発者向け）

   データベースに直接登録するか、以下のSQLを実行：
   ```sql
   UPDATE categories
   SET sheet_id = 'SPREADSHEET_ID',
       sheet_url = 'https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit',
       sheets_synced_at = NOW()
   WHERE id = 'CATEGORY_ID';
   ```

#### 解決方法3: 古いスプレッドシートを削除

サービスアカウントのDriveに古いスプレッドシートが多数ある場合：

1. Google Cloud Consoleでサービスアカウントのメールアドレスを確認
2. そのアカウントで作成されたスプレッドシートを見つけて削除
3. ただし、サービスアカウントのDriveには直接アクセスできないため、API経由で削除する必要があります

### エラー: "権限エラー"

- Google Sheets APIが有効になっているか確認
- **Google Drive API**が有効になっているか確認（重要！）
- サービスアカウントが正しく作成されているか確認

### エラー: "スプレッドシートの作成に失敗しました"

1. ブラウザの開発者ツール（F12）を開く
2. コンソールタブで詳細なエラーメッセージを確認
3. エラーメッセージに従って対応

### スプレッドシートが作成されたが開けない

- スプレッドシートへのアクセス権限を自分のアカウントに付与してください（上記手順8を参照）

## サービスアカウントのメールアドレスを確認する方法

サービスアカウントのメールアドレスは以下の形式です：

```
article-generator-sheets@your-project-id.iam.gserviceaccount.com
```

確認方法：
1. Google Cloud Consoleで「IAMと管理」→「サービスアカウント」を開く
2. 作成したサービスアカウントのメールアドレスをコピー

または、`.env`ファイルの`GOOGLE_CREDENTIALS_JSON`内の`client_email`フィールドで確認できます。

## セキュリティに関する注意

- サービスアカウントキーのJSONファイルは**Gitにコミットしないでください**
- `.env`ファイルは`.gitignore`に含まれています
- 本番環境では環境変数を安全に管理してください（例: Railway Secrets）

## 連携後の動作

Google Sheets連携が有効になると：

1. カテゴリごとにスプレッドシートを作成できます
2. 記事を作成すると、自動的にスプレッドシートに行が追加されます
3. 記事のステータスが変更されると、自動的にスプレッドシートが更新されます
4. WordPress公開時、公開URLがスプレッドシートに記録されます

スプレッドシートの列構成：
- KW: キーワード
- 記事タイトル: 生成されたタイトル
- ステータス: 未生成/生成中/レビュー待ち/公開済み など
- 公開URL: WordPress公開URL
- WP投稿ID: WordPressの投稿ID
- 生成日時: 記事作成日時
- 更新日時: 最終更新日時
- 備考: 任意のメモ

## 費用について

Google Sheets APIの利用は基本的に無料です：

- 1日あたり500リクエスト（プロジェクトあたり）
- 通常の使用では上限に達することはほとんどありません
- 詳細: https://developers.google.com/sheets/api/limits
