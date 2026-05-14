import pytest
from unittest.mock import AsyncMock, patch

from wordpress_post_mcp.config import Config


@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setenv("WP_URL", "https://example.com")
    monkeypatch.setenv("WP_USERNAME", "user")
    monkeypatch.setenv("WP_APP_PASSWORD", "pass")
    return Config(url="https://example.com", username="user", app_password="pass")


@pytest.fixture
def mock_wp_client():
    with patch("wordpress_post_mcp.server.WpClient") as mock_cls:
        instance = AsyncMock()
        mock_cls.return_value = instance
        yield instance
