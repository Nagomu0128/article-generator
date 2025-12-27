"""WordPress XMLRPC API サービス"""

import base64
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from xmlrpc import client as xmlrpc_client

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.shared.domain.exceptions import ExternalServiceError

settings = get_settings()


class PostStatus(str, Enum):
    """WordPress投稿ステータス"""

    DRAFT = "draft"
    PUBLISH = "publish"


@dataclass
class WordPressPost:
    """WordPress投稿"""

    id: int
    title: str
    status: str
    link: str


class WordPressService:
    """WordPress REST APIクライアント"""

    def __init__(self):
        # URLの正規化（プロトコルがない場合はhttps://を追加）
        url = settings.wordpress_url.rstrip("/")
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        self.base_url = url

        # WordPress.comサイトもセルフホストサイトも標準のWP REST API v2を使用
        # WordPress.comサイトでもApplication Passwordsは標準のWP REST APIで動作する
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def auth_header(self) -> str:
        """Basic認証ヘッダーを生成"""
        # アプリケーションパスワードからスペースを削除
        app_password = settings.wordpress_app_password.replace(" ", "")
        credentials = f"{settings.wordpress_username}:{app_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def get_client(self) -> httpx.AsyncClient:
        """HTTPクライアントを取得（遅延初期化）"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": self.auth_header,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def create_post(
        self, title: str, content: str, status: PostStatus = PostStatus.DRAFT
    ) -> WordPressPost:
        """WordPress投稿を作成"""
        client = await self.get_client()

        # 標準のWP REST API v2を使用
        response = await client.post(
            f"{self.api_url}/posts",
            json={"title": title, "content": content, "status": status.value},
        )

        if response.status_code >= 400:
            raise ExternalServiceError("WordPress", f"Create failed: {response.text}")

        data = response.json()
        return WordPressPost(
            id=data["id"],
            title=data["title"]["rendered"],
            status=data["status"],
            link=data["link"],
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
    async def publish_post(self, post_id: int) -> WordPressPost:
        """WordPress投稿を公開"""
        client = await self.get_client()

        # 標準のWP REST API v2を使用
        response = await client.post(
            f"{self.api_url}/posts/{post_id}",
            json={"status": "publish"},
        )

        if response.status_code >= 400:
            raise ExternalServiceError("WordPress", f"Publish failed: {response.text}")

        data = response.json()
        return WordPressPost(
            id=data["id"],
            title=data["title"]["rendered"],
            status=data["status"],
            link=data["link"],
        )

    async def close(self):
        """HTTPクライアントをクローズ"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# シングルトンインスタンス
wordpress_service = WordPressService()
