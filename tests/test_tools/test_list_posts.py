from wordpress_post_mcp.server import mcp


async def call_tool(name: str, **kwargs):
    tool = await mcp.get_tool(name)
    return await tool.fn(**kwargs)


SAMPLE_RESULT = {
    "posts": [
        {
            "id": 1,
            "title": "記事1",
            "status": "publish",
            "date": "2024-01-15T10:00:00",
            "categories": [{"id": 1, "name": "技術"}],
            "tags": [{"id": 5, "name": "Python"}],
            "excerpt": "<p>抜粋</p>",
        }
    ],
    "total": 50,
    "total_pages": 5,
    "page": 1,
    "per_page": 10,
}


async def test_list_posts_returns_result(mock_wp_client):
    mock_wp_client.list_posts.return_value = SAMPLE_RESULT

    result = await call_tool("list_posts")

    assert result["total"] == 50
    assert len(result["posts"]) == 1


async def test_list_posts_passes_query(mock_wp_client):
    mock_wp_client.list_posts.return_value = {**SAMPLE_RESULT, "posts": []}

    await call_tool("list_posts", query="検索ワード")

    call_kwargs = mock_wp_client.list_posts.call_args.kwargs
    assert call_kwargs["query"] == "検索ワード"


async def test_list_posts_default_status_is_any(mock_wp_client):
    mock_wp_client.list_posts.return_value = {**SAMPLE_RESULT, "posts": []}

    await call_tool("list_posts")

    call_kwargs = mock_wp_client.list_posts.call_args.kwargs
    assert call_kwargs["status"] == "any"


async def test_list_posts_default_order_is_desc(mock_wp_client):
    mock_wp_client.list_posts.return_value = {**SAMPLE_RESULT, "posts": []}

    await call_tool("list_posts")

    call_kwargs = mock_wp_client.list_posts.call_args.kwargs
    assert call_kwargs["order"] == "desc"


async def test_list_posts_passes_category_and_tag_filter(mock_wp_client):
    mock_wp_client.list_posts.return_value = {**SAMPLE_RESULT, "posts": []}

    await call_tool("list_posts", category_id=1, tag_id=5)

    call_kwargs = mock_wp_client.list_posts.call_args.kwargs
    assert call_kwargs["category_id"] == 1
    assert call_kwargs["tag_id"] == 5


async def test_list_posts_result_has_no_content_field(mock_wp_client):
    mock_wp_client.list_posts.return_value = SAMPLE_RESULT

    result = await call_tool("list_posts")

    for post in result["posts"]:
        assert "content" not in post
