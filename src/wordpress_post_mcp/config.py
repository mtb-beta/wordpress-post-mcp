import os
from dataclasses import dataclass

from wordpress_post_mcp.errors import WordPressMCPError


@dataclass
class Config:
    """サーバー設定。"""

    url: str
    username: str
    app_password: str


def load_config() -> Config:
    """環境変数から設定を読み込む。未設定の変数があれば WordPressMCPError を投げる。"""
    missing = [v for v in ("WP_URL", "WP_USERNAME", "WP_APP_PASSWORD") if not os.getenv(v)]
    if missing:
        raise WordPressMCPError(f"必須の環境変数が設定されていません: {', '.join(missing)}")

    url = os.environ["WP_URL"].rstrip("/")
    return Config(
        url=url,
        username=os.environ["WP_USERNAME"],
        app_password=os.environ["WP_APP_PASSWORD"],
    )
