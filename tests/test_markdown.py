from wordpress_post_mcp.markdown import convert_markdown


def test_heading():
    assert convert_markdown("# 見出し1") == "<h1>見出し1</h1>\n"


def test_paragraph():
    assert convert_markdown("Hello, world!") == "<p>Hello, world!</p>\n"


def test_bold():
    result = convert_markdown("**bold**")
    assert "<strong>bold</strong>" in result


def test_italic():
    result = convert_markdown("*italic*")
    assert "<em>italic</em>" in result


def test_unordered_list():
    result = convert_markdown("- item1\n- item2")
    assert "<ul>" in result
    assert "<li>item1</li>" in result
    assert "<li>item2</li>" in result


def test_ordered_list():
    result = convert_markdown("1. first\n2. second")
    assert "<ol>" in result
    assert "<li>first</li>" in result


def test_link():
    result = convert_markdown("[text](https://example.com)")
    assert '<a href="https://example.com">text</a>' in result


def test_code_block_uses_pre_code():
    result = convert_markdown("```\ncode here\n```")
    assert "<pre><code>" in result
    assert "code here" in result


def test_inline_code():
    result = convert_markdown("`inline`")
    assert "<code>inline</code>" in result


def test_empty_string():
    assert convert_markdown("") == ""
