from markdown_it import MarkdownIt


_md = MarkdownIt("commonmark")


def convert_markdown(text: str) -> str:
    """Markdown テキストを HTML に変換する。"""
    if not text:
        return ""
    return _md.render(text)
