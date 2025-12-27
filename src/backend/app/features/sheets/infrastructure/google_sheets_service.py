"""Google Sheets連携サービス"""

import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.shared.domain.enums import ArticleStatus
from app.shared.domain.exceptions import ExternalServiceError

settings = get_settings()

# Google Sheets設定
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_HEADERS = [
    "KW",
    "記事タイトル",
    "ステータス",
    "公開URL",
    "WP投稿ID",
    "生成日時",
    "更新日時",
    "備考",
]

# ステータス表示名マッピング
STATUS_DISPLAY = {
    ArticleStatus.PENDING: "未生成",
    ArticleStatus.GENERATING: "生成中",
    ArticleStatus.FAILED: "生成失敗",
    ArticleStatus.REVIEW_PENDING: "レビュー待ち",
    ArticleStatus.REVIEWED: "レビュー済み",
    ArticleStatus.PUBLISHED: "公開済み",
}


class GoogleSheetsService:
    """Google Sheetsサービス"""

    def __init__(self):
        self._client: gspread.Client | None = None

    @property
    def client(self) -> gspread.Client:
        """Google Sheetsクライアント取得（遅延初期化）"""
        if self._client is None:
            try:
                credentials_dict = json.loads(settings.google_credentials_json)
                credentials = Credentials.from_service_account_info(
                    credentials_dict, scopes=SCOPES
                )
                self._client = gspread.authorize(credentials)
            except json.JSONDecodeError as e:
                raise ExternalServiceError(
                    "Google Sheets",
                    f"GOOGLE_CREDENTIALS_JSONの形式が不正です: {str(e)}"
                )
            except Exception as e:
                raise ExternalServiceError(
                    "Google Sheets",
                    f"認証失敗: {str(e)}. GOOGLE_CREDENTIALS_JSONを確認してください。"
                )
        return self._client

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def create_spreadsheet(self, title: str) -> tuple[str, str]:
        """
        新規スプレッドシート作成

        Args:
            title: スプレッドシートタイトル

        Returns:
            (sheet_id, sheet_url)のタプル
        """
        try:
            spreadsheet = self.client.create(title)
            worksheet = spreadsheet.sheet1

            # ヘッダー行を設定
            worksheet.update("A1:H1", [SHEET_HEADERS])
            worksheet.format("A1:H1", {"textFormat": {"bold": True}})

            return spreadsheet.id, spreadsheet.url
        except Exception as e:
            error_msg = str(e)
            # よくあるエラーのメッセージを分かりやすく変換
            if "storageQuotaExceeded" in error_msg or "storage quota" in error_msg.lower():
                raise ExternalServiceError(
                    "Google Sheets",
                    "サービスアカウントのGoogle Driveストレージが不足しています。GOOGLE_SHEETS_SETUP.mdのトラブルシューティングを参照してください。"
                )
            elif "403" in error_msg:
                raise ExternalServiceError(
                    "Google Sheets",
                    "権限エラー: Google Sheets APIとGoogle Drive APIが有効になっているか確認してください。"
                )
            else:
                raise ExternalServiceError("Google Sheets", f"作成失敗: {error_msg}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def update_article_status(
        self,
        sheet_id: str,
        keyword: str,
        status: ArticleStatus,
        title: str | None = None,
        wp_url: str | None = None,
        wp_post_id: int | None = None,
    ) -> bool:
        """
        記事ステータス更新

        Args:
            sheet_id: スプレッドシートID
            keyword: キーワード
            status: 記事ステータス
            title: 記事タイトル
            wp_url: WordPress URL
            wp_post_id: WordPress投稿ID

        Returns:
            更新成功の場合True
        """
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1

            # キーワードでセルを検索
            try:
                cell = worksheet.find(keyword, in_column=1)
                row = cell.row
            except gspread.CellNotFound:
                # 見つからない場合は新規行追加
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                worksheet.append_row(
                    [keyword, "", STATUS_DISPLAY.get(status, ""), "", "", "", now, ""]
                )
                cell = worksheet.find(keyword, in_column=1)
                row = cell.row

            # バッチ更新用のデータ準備
            updates = []
            updates.append(
                {"range": f"C{row}", "values": [[STATUS_DISPLAY.get(status, str(status))]]}
            )

            if title:
                updates.append({"range": f"B{row}", "values": [[title]]})
            if wp_url:
                updates.append({"range": f"D{row}", "values": [[wp_url]]})
            if wp_post_id:
                updates.append({"range": f"E{row}", "values": [[str(wp_post_id)]]})

            # 更新日時
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updates.append({"range": f"G{row}", "values": [[now]]})

            # バッチ更新実行
            worksheet.batch_update(updates)
            return True

        except Exception as e:
            raise ExternalServiceError("Google Sheets", f"更新失敗: {str(e)}")


# シングルトンインスタンス
sheets_service = GoogleSheetsService()
