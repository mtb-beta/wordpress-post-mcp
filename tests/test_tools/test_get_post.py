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


SAMPLE_POST = {
    "id": 42,
    "title": "記事タイトル",
    "content": "<p>本文</p>",
    "status": "publish",
    "date": "2024-01-15T10:00:00",
    "categories": [{"id": 1, "name": "技術"}],
    "tags": [{"id": 5, "name": "Python"}],
    "link": "https://example.com/post-slug/",
}


async def test_get_post_returns_post_with_content(mock_wp_client, mock_config):
    mock_wp_client.get_post.return_value = SAMPLE_POST

    result = await call_tool("get_post", post_id=42)

    assert result["id"] == 42
    assert result["content"] == "<p>本文</p>"
    assert result["categories"] == [{"id": 1, "name": "技術"}]
    assert result["tags"] == [{"id": 5, "name": "Python"}]


async def test_get_post_calls_client_with_correct_id(mock_wp_client, mock_config):
    mock_wp_client.get_post.return_value = SAMPLE_POST

    await call_tool("get_post", post_id=42)

    mock_wp_client.get_post.assert_awaited_once_with(42)
