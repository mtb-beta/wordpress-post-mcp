from typing import Any, cast

import httpx

from wordpress_post_mcp.errors import NetworkError, WordPressAPIError


class WpClient:
    """WordPress REST API クライアント。"""

    def __init__(self, url: str, username: str, app_password: str) -> None:
        self._base = f"{url}/wp-json/wp/v2"
        self._auth = (username, app_password)

    def _http(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(auth=self._auth)

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_error:
            try:
                detail = response.json().get("message", response.text)
            except Exception:
                detail = response.text
            raise WordPressAPIError(
                f"WordPress API エラー {response.status_code}: {detail}",
                status_code=response.status_code,
            )

    async def create_post(
        self,
        title: str,
        content_html: str,
        excerpt: str,
        slug: str,
        category_ids: list[int],
        tag_ids: list[int],
    ) -> dict[str, Any]:
        """下書き記事を作成する。"""
        payload: dict[str, Any] = {
            "title": title,
            "content": content_html,
            "status": "draft",
            "categories": category_ids,
            "tags": tag_ids,
        }
        if excerpt:
            payload["excerpt"] = excerpt
        if slug:
            payload["slug"] = slug

        try:
            async with self._http() as http:
                response = await http.post(f"{self._base}/posts", json=payload)
        except httpx.HTTPError as e:
            raise NetworkError(f"ネットワークエラー: {e}") from e

        self._raise_for_status(response)
        return cast(dict[str, Any], response.json())

    async def list_posts(
        self,
        query: str = "",
        status: str = "any",
        category_id: int | None = None,
        tag_id: int | None = None,
        order: str = "desc",
        per_page: int = 10,
        page: int = 1,
    ) -> dict[str, Any]:
        """記事一覧を取得する。カテゴリ・タグ情報を _embed で埋め込む。"""
        params: dict[str, Any] = {
            "status": status,
            "order": order,
            "per_page": per_page,
            "page": page,
            "_embed": "wp:term",
        }
        if query:
            params["search"] = query
        if category_id is not None:
            params["categories"] = category_id
        if tag_id is not None:
            params["tags"] = tag_id

        try:
            async with self._http() as http:
                response = await http.get(f"{self._base}/posts", params=params)
        except httpx.HTTPError as e:
            raise NetworkError(f"ネットワークエラー: {e}") from e

        self._raise_for_status(response)
        posts = [self._format_post_summary(p) for p in response.json()]
        return {
            "posts": posts,
            "total": int(response.headers.get("X-WP-Total", 0)),
            "total_pages": int(response.headers.get("X-WP-TotalPages", 0)),
            "page": page,
            "per_page": per_page,
        }

    async def get_post(self, post_id: int) -> dict[str, Any]:
        """指定 ID の記事を取得する。"""
        params = {"_embed": "wp:term"}
        try:
            async with self._http() as http:
                response = await http.get(
                    f"{self._base}/posts/{post_id}", params=params
                )
        except httpx.HTTPError as e:
            raise NetworkError(f"ネットワークエラー: {e}") from e

        self._raise_for_status(response)
        return self._format_post_detail(response.json())

    async def list_categories(self) -> list[dict[str, Any]]:
        """カテゴリ一覧を取得する。"""
        try:
            async with self._http() as http:
                response = await http.get(
                    f"{self._base}/categories", params={"per_page": 100}
                )
        except httpx.HTTPError as e:
            raise NetworkError(f"ネットワークエラー: {e}") from e

        self._raise_for_status(response)
        return [
            {"id": c["id"], "name": c["name"], "slug": c["slug"], "count": c["count"]}
            for c in response.json()
        ]

    async def list_tags(self) -> list[dict[str, Any]]:
        """タグ一覧を取得する。"""
        try:
            async with self._http() as http:
                response = await http.get(
                    f"{self._base}/tags", params={"per_page": 100}
                )
        except httpx.HTTPError as e:
            raise NetworkError(f"ネットワークエラー: {e}") from e

        self._raise_for_status(response)
        return [
            {"id": t["id"], "name": t["name"], "slug": t["slug"], "count": t["count"]}
            for t in response.json()
        ]

    def _extract_terms(
        self, post: dict[str, Any], taxonomy: str
    ) -> list[dict[str, Any]]:
        """_embedded から指定 taxonomy のタームを抽出する。"""
        embedded = post.get("_embedded", {})
        term_groups = embedded.get("wp:term", [])
        terms = []
        for group in term_groups:
            for term in group:
                if term.get("taxonomy") == taxonomy:
                    terms.append({"id": term["id"], "name": term["name"]})
        return terms

    def _format_post_summary(self, post: dict[str, Any]) -> dict[str, Any]:
        """記事一覧用の整形（本文なし）。"""
        return {
            "id": post["id"],
            "title": post["title"]["rendered"],
            "status": post["status"],
            "date": post["date"],
            "categories": self._extract_terms(post, "category"),
            "tags": self._extract_terms(post, "post_tag"),
            "excerpt": post["excerpt"]["rendered"],
        }

    def _format_post_detail(self, post: dict[str, Any]) -> dict[str, Any]:
        """記事詳細用の整形（本文あり）。"""
        return {
            "id": post["id"],
            "title": post["title"]["rendered"],
            "content": post["content"]["rendered"],
            "status": post["status"],
            "date": post["date"],
            "categories": self._extract_terms(post, "category"),
            "tags": self._extract_terms(post, "post_tag"),
            "link": post["link"],
        }
