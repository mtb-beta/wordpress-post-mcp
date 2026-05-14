import pytest

from wordpress_post_mcp.server import mcp


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("WP_URL", "https://example.com")
    monkeypatch.setenv("WP_USERNAME", "user")
    monkeypatch.setenv("WP_APP_PASSWORD", "pass")


async def call_tool(name: str, **kwargs):
    tool = await mcp.get_tool(name)
    return await tool.fn(**kwargs)


async def test_list_tags_returns_list(mock_wp_client, mock_config):
    mock_wp_client.list_tags.return_value = [
        {"id": 5, "name": "Python", "slug": "python", "count": 18}
    ]

    result = await call_tool("list_tags")

    assert len(result) == 1
    assert result[0]["id"] == 5
    assert result[0]["name"] == "Python"
    assert result[0]["slug"] == "python"
    assert result[0]["count"] == 18
