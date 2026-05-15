from typing import Annotated, Any

from markdown_it import MarkdownIt
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from wordpress_post_mcp.config import load_config
from wordpress_post_mcp.errors import WordPressMCPError
from wordpress_post_mcp.wp_client import WpClient

_md = MarkdownIt("commonmark")

mcp = FastMCP("wordpress-post-mcp")


def _client() -> WpClient:
    return WpClient(load_config())


@mcp.tool()
async def create_draft(
    title: Annotated[str, "記事タイトル"],
    content: Annotated[str, "記事本文（Markdown）"],
    excerpt: Annotated[str, "抜粋"] = "",
    slug: Annotated[str, "URL スラッグ"] = "",
    category_ids: Annotated[list[int], "カテゴリ ID のリスト"] = [],
    tag_ids: Annotated[list[int], "タグ ID のリスト"] = [],
) -> dict[str, Any]:
    """Markdown の本文を HTML に変換して WordPress に下書きを作成する。"""
    content_html = _md.render(content) if content else ""
    try:
        post = await _client().create_post(
            title=title,
            content_html=content_html,
            excerpt=excerpt,
            slug=slug,
            category_ids=category_ids,
            tag_ids=tag_ids,
        )
    except WordPressMCPError as e:
        raise ToolError(str(e)) from e

    return {
        "id": post["id"],
        "title": post["title"]["rendered"],
        "status": post["status"],
        "link": post["link"],
    }


@mcp.tool()
async def list_posts(
    query: Annotated[str, "検索キーワード"] = "",
    status: Annotated[str, "publish / draft / any"] = "any",
    category_id: Annotated[int | None, "カテゴリ ID で絞り込み"] = None,
    tag_id: Annotated[int | None, "タグ ID で絞り込み"] = None,
    order: Annotated[str, "asc / desc（投稿日順）"] = "desc",
    per_page: Annotated[int, "1〜100"] = 10,
    page: Annotated[int, "ページ番号"] = 1,
) -> dict[str, Any]:
    """記事一覧を取得する。本文は含まない。"""
    try:
        return await _client().list_posts(
            query=query,
            status=status,
            category_id=category_id,
            tag_id=tag_id,
            order=order,
            per_page=per_page,
            page=page,
        )
    except WordPressMCPError as e:
        raise ToolError(str(e)) from e


@mcp.tool()
async def get_post(
    post_id: Annotated[int, "取得する記事の ID"],
) -> dict[str, Any]:
    """指定 ID の記事の本文・カテゴリ・タグ・メタ情報を取得する。"""
    try:
        return await _client().get_post(post_id)
    except WordPressMCPError as e:
        raise ToolError(str(e)) from e


@mcp.tool()
async def list_categories() -> list[dict[str, Any]]:
    """WordPress に登録されているカテゴリの一覧を取得する。"""
    try:
        return await _client().list_categories()
    except WordPressMCPError as e:
        raise ToolError(str(e)) from e


@mcp.tool()
async def list_tags() -> list[dict[str, Any]]:
    """WordPress に登録されているタグの一覧を取得する。"""
    try:
        return await _client().list_tags()
    except WordPressMCPError as e:
        raise ToolError(str(e)) from e


def main() -> None:
    """サーバー起動エントリポイント。環境変数が未設定なら終了する。"""
    try:
        load_config()
    except WordPressMCPError as e:
        import sys

        print(f"設定エラー: {e}", file=sys.stderr)
        sys.exit(1)
    mcp.run()


if __name__ == "__main__":
    main()
