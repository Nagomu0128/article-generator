# WordPress連携セットアップガイド

## 現在の状況

WordPress.com無料サイト (`kyoshidk-ewbmx.wordpress.com`) では、以下のAPIが制限されています：

- ❌ **WP REST API v2** - 404エラー（無効化されている）
- ❌ **XMLRPC** - Application Passwordsが機能しない
- ⚠️ **WordPress.com REST API v1.1** - OAuth 2.0が必要（複雑）

## 推奨される解決策

### オプション1: セルフホストWordPressサイトを使用（推奨）

セルフホストのWordPressサイトであれば、Application Passwordsが完全に機能します。

**必要なもの:**
- WordPressホスティング（Xserver、ロリポップ、ConoHa WINGなど）
- または、ローカルのWordPress環境（Local by Flywheel、XAMPPなど）

**設定手順:**

1. **WordPressをインストール**
   - ホスティングサービスの管理画面からWordPressをインストール
   - または、[wordpress.org](https://ja.wordpress.org/)からダウンロード

2. **Application Passwordsを設定**
   - WordPressダッシュボード → ユーザー → プロフィール
   - 「アプリケーションパスワード」セクションまでスクロール
   - 新しいアプリケーション名を入力（例: "Article Generator"）
   - 「新しいアプリケーションパスワードを追加」をクリック
   - 生成されたパスワードをコピー（例: `xxxx xxxx xxxx xxxx xxxx xxxx`）

3. **環境変数を更新**

`.env`ファイルを編集：

```env
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

4. **バックエンドを再起動**

```bash
docker-compose restart backend_app
```

### オプション2: WordPress.com有料プランにアップグレード

WordPress.comの**Businessプラン以上**であれば、プラグインをインストールして標準のWP REST APIを有効化できます。

**料金:** 月額$25〜

**手順:**
1. [WordPress.com Pricing](https://wordpress.com/pricing/)でBusinessプランにアップグレード
2. Jetpackプラグインを有効化
3. Application Passwordsを設定
4. `.env`ファイルを更新して再起動

### オプション3: ローカルWordPress環境でテスト（開発用）

開発・テスト目的であれば、ローカルにWordPressをセットアップできます。

**Local by Flywheel（推奨）:**

1. [Local by Flywheel](https://localwp.com/)をダウンロード・インストール
2. 新しいサイトを作成
3. サイト起動後、管理画面にアクセス
4. Application Passwordsを設定
5. `.env`を更新：

```env
WORDPRESS_URL=http://article-generator.local
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

**ngrokで外部アクセス（オプション）:**

Dockerコンテナからローカルのデータベースにアクセスする場合：

```bash
# ngrokをインストール
npm install -g ngrok

# WordPressサイトを公開
ngrok http 80

# 表示されたURLを使用
# 例: https://abc123.ngrok.io
```

## トラブルシューティング

### Application Passwordsが表示されない場合

WordPress 5.6以降が必要です。また、HTTPSが有効でない場合は表示されないことがあります。

**解決方法:**

`wp-config.php`に以下を追加（開発環境のみ）：

```php
define('ALLOW_UNFILTERED_UPLOADS', true);
```

### WP REST APIが無効な場合

プラグインやテーマがAPIを無効化している可能性があります。

**確認方法:**

```bash
curl https://your-site.com/wp-json/wp/v2
```

正常な場合、JSONレスポンスが返ります。

### 認証エラーが発生する場合

1. Application Passwordを再生成
2. スペースを含めて正確にコピー
3. ユーザー名が正しいか確認（メールアドレスではなくユーザー名）
4. WordPressのバージョンが5.6以降か確認

## まとめ

WordPress.com無料サイトではApplication Passwordsが機能しません。

**最も簡単な解決策:**
- セルフホストのWordPressサイトを使用
- または、ローカル環境でテスト

**質問がある場合:**
- [WordPress.org フォーラム](https://ja.wordpress.org/support/)
- [WordPress.com サポート](https://wordpress.com/support/)
