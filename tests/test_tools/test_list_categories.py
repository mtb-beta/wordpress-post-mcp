from wordpress_post_mcp.server import mcp


async def call_tool(name: str, **kwargs):
    tool = await mcp.get_tool(name)
    return await tool.fn(**kwargs)


async def test_list_categories_returns_list(mock_wp_client):
    mock_wp_client.list_categories.return_value = [
        {"id": 1, "name": "技術", "slug": "tech", "count": 42}
    ]

    result = await call_tool("list_categories")

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["name"] == "技術"
    assert result[0]["slug"] == "tech"
    assert result[0]["count"] == 42
