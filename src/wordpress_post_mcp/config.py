from dataclasses import dataclass

from decouple import UndefinedValueError, config

from wordpress_post_mcp.errors import ConfigurationError


@dataclass
class Config:
    """サーバー設定。"""

    url: str
    username: str
    app_password: str


def load_config() -> Config:
    """環境変数（または .env）から設定を読み込む。未設定の変数があれば ConfigurationError を投げる。"""
    try:
        url = config("WP_URL").rstrip("/")
        username = config("WP_USERNAME")
        app_password = config("WP_APP_PASSWORD")
    except UndefinedValueError as e:
        raise ConfigurationError(str(e)) from e

    return Config(url=url, username=username, app_password=app_password)
