import pytest
import httpx
import respx

from wordpress_post_mcp.config import Config
from wordpress_post_mcp.errors import WordPressMCPError
from wordpress_post_mcp.wp_client import WpClient

BASE_URL = "https://example.com"
CONFIG = Config(url=BASE_URL, username="user", app_password="pass")
API_BASE = f"{BASE_URL}/wp-json/wp/v2"


@pytest.fixture
def client():
    return WpClient(CONFIG)


# --- create_post ---

@respx.mock
async def test_create_post_sends_correct_request(client):
    route = respx.post(f"{API_BASE}/posts").mock(
        return_value=httpx.Response(
            201,
            json={"id": 1, "title": {"rendered": "タイトル"}, "status": "draft", "link": "https://example.com/?p=1"},
        )
    )

    result = await client.create_post(
        title="タイトル",
        content_html="<p>本文</p>",
        excerpt="抜粋",
        slug="slug",
        category_ids=[1, 2],
        tag_ids=[3],
    )

    assert route.called
    request = route.calls[0].request
    import json
    body = json.loads(request.content)
    assert body["title"] == "タイトル"
    assert body["content"] == "<p>本文</p>"
    assert body["status"] == "draft"
    assert body["categories"] == [1, 2]
    assert body["tags"] == [3]
    assert result["id"] == 1


@respx.mock
async def test_create_post_raises_on_auth_error(client):
    respx.post(f"{API_BASE}/posts").mock(return_value=httpx.Response(401, json={"code": "rest_forbidden"}))

    with pytest.raises(WordPressMCPError):
        await client.create_post(title="t", content_html="c", excerpt="", slug="", category_ids=[], tag_ids=[])


# --- list_posts ---

@respx.mock
async def test_list_posts_returns_posts_and_pagination(client):
    respx.get(f"{API_BASE}/posts").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "title": {"rendered": "記事1"},
                    "status": "publish",
                    "date": "2024-01-15T10:00:00",
                    "excerpt": {"rendered": "<p>抜粋</p>"},
                    "_embedded": {
                        "wp:term": [
                            [{"id": 1, "name": "技術", "taxonomy": "category"}],
                            [{"id": 5, "name": "Python", "taxonomy": "post_tag"}],
                        ]
                    },
                }
            ],
            headers={"X-WP-Total": "50", "X-WP-TotalPages": "5"},
        )
    )

    result = await client.list_posts()

    assert result["total"] == 50
    assert result["total_pages"] == 5
    assert len(result["posts"]) == 1
    assert result["posts"][0]["id"] == 1


@respx.mock
async def test_list_posts_passes_query_params(client):
    route = respx.get(f"{API_BASE}/posts").mock(
        return_value=httpx.Response(
            200,
            json=[],
            headers={"X-WP-Total": "0", "X-WP-TotalPages": "0"},
        )
    )

    await client.list_posts(query="検索ワード", status="publish", category_id=1, tag_id=2, order="asc", per_page=5, page=2)

    request = route.calls[0].request
    assert b"search=%E6%A4%9C%E7%B4%A2%E3%83%AF%E3%83%BC%E3%83%89" in request.url.raw_path or "search" in str(request.url)
    assert "status=publish" in str(request.url)
    assert "categories=1" in str(request.url)
    assert "tags=2" in str(request.url)
    assert "order=asc" in str(request.url)
    assert "per_page=5" in str(request.url)
    assert "page=2" in str(request.url)


# --- get_post ---

@respx.mock
async def test_get_post_returns_post(client):
    respx.get(f"{API_BASE}/posts/42").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 42,
                "title": {"rendered": "記事"},
                "content": {"rendered": "<p>本文</p>"},
                "status": "publish",
                "date": "2024-01-15T10:00:00",
                "link": "https://example.com/post/",
                "_embedded": {
                    "wp:term": [
                        [{"id": 1, "name": "技術", "taxonomy": "category"}],
                        [{"id": 5, "name": "Python", "taxonomy": "post_tag"}],
                    ]
                },
            },
        )
    )

    result = await client.get_post(42)

    assert result["id"] == 42
    assert result["title"] == "記事"


@respx.mock
async def test_get_post_raises_on_not_found(client):
    respx.get(f"{API_BASE}/posts/999").mock(return_value=httpx.Response(404, json={"code": "rest_post_invalid_id"}))

    with pytest.raises(WordPressMCPError):
        await client.get_post(999)


# --- list_categories ---

@respx.mock
async def test_list_categories_returns_list(client):
    respx.get(f"{API_BASE}/categories").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"id": 1, "name": "技術", "slug": "tech", "count": 42},
            ],
        )
    )

    result = await client.list_categories()

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["name"] == "技術"


# --- list_tags ---

@respx.mock
async def test_list_tags_returns_list(client):
    respx.get(f"{API_BASE}/tags").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"id": 5, "name": "Python", "slug": "python", "count": 18},
            ],
        )
    )

    result = await client.list_tags()

    assert len(result) == 1
    assert result[0]["id"] == 5
    assert result[0]["name"] == "Python"


# --- ネットワークエラー ---

@respx.mock
async def test_create_post_raises_on_network_error(client):
    respx.post(f"{API_BASE}/posts").mock(side_effect=httpx.ConnectError("connection refused"))

    with pytest.raises(WordPressMCPError):
        await client.create_post(title="t", content_html="c", excerpt="", slug="", category_ids=[], tag_ids=[])
