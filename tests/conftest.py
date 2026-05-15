import os
from unittest.mock import AsyncMock, patch

import pytest

# pytest のコレクション（モジュールインポート）前に env vars をセットする。
# config.py はインポート時に Config = load_config() を実行するため、
# この時点で env vars が存在している必要がある。
os.environ.setdefault("WP_URL", "https://example.com")
os.environ.setdefault("WP_USERNAME", "user")
os.environ.setdefault("WP_APP_PASSWORD", "pass")


@pytest.fixture
def mock_wp_client():
    with patch("wordpress_post_mcp.server.WpClient") as mock_cls:
        instance = AsyncMock()
        mock_cls.return_value = instance
        yield instance
