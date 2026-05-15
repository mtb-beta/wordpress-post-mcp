import pytest
from fastmcp.exceptions import ToolError

from wordpress_post_mcp.server import mcp
from wordpress_post_mcp.errors import WordPressMCPError


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("WP_URL", "https://example.com")
    monkeypatch.setenv("WP_USERNAME", "user")
    monkeypatch.setenv("WP_APP_PASSWORD", "pass")


async def call_tool(name: str, **kwargs):
    """MCPツールを直接呼び出すヘルパー。"""
    tool = await mcp.get_tool(name)
    return await tool.fn(**kwargs)


async def test_create_draft_converts_markdown_to_html(mock_wp_client, mock_config):
    mock_wp_client.create_post.return_value = {
        "id": 1,
        "title": {"rendered": "タイトル"},
        "status": "draft",
        "link": "https://example.com/?p=1",
    }

    result = await call_tool(
        "create_draft",
        title="タイトル",
        content="# 見出し\n本文です",
    )

    assert result["id"] == 1
    assert result["status"] == "draft"
    called_html = mock_wp_client.create_post.call_args.kwargs["content_html"]
    assert "<h1>" in called_html


async def test_create_draft_sends_empty_excerpt_when_omitted(
    mock_wp_client, mock_config
):
    mock_wp_client.create_post.return_value = {
        "id": 2,
        "title": {"rendered": "T"},
        "status": "draft",
        "link": "https://example.com/?p=2",
    }

    await call_tool("create_draft", title="T", content="body")

    call_kwargs = mock_wp_client.create_post.call_args.kwargs
    assert call_kwargs["excerpt"] == ""


async def test_create_draft_sends_category_and_tag_ids(mock_wp_client, mock_config):
    mock_wp_client.create_post.return_value = {
        "id": 3,
        "title": {"rendered": "T"},
        "status": "draft",
        "link": "https://example.com/?p=3",
    }

    await call_tool(
        "create_draft", title="T", content="body", category_ids=[1, 2], tag_ids=[5]
    )

    call_kwargs = mock_wp_client.create_post.call_args.kwargs
    assert call_kwargs["category_ids"] == [1, 2]
    assert call_kwargs["tag_ids"] == [5]


async def test_create_draft_returns_correct_format(mock_wp_client, mock_config):
    mock_wp_client.create_post.return_value = {
        "id": 10,
        "title": {"rendered": "記事タイトル"},
        "status": "draft",
        "link": "https://example.com/?p=10",
    }

    result = await call_tool("create_draft", title="記事タイトル", content="本文")

    assert result == {
        "id": 10,
        "title": "記事タイトル",
        "status": "draft",
        "link": "https://example.com/?p=10",
    }


async def test_create_draft_raises_mcp_error_on_wp_error(mock_wp_client, mock_config):
    mock_wp_client.create_post.side_effect = WordPressMCPError("認証エラー")

    with pytest.raises(ToolError):
        await call_tool("create_draft", title="T", content="body")
