"""
tests/p4/test_parser.py

AutoSearch V4

P4.6 Generic Parser Tests

測試目前既有 parser/parser.py。

測試範圍：

1. HTML Noise Removal
2. Content Score
3. Main Content Detection
4. Article Generation
5. Title Extraction
6. URL / Keyword
7. Content Extraction
8. Empty / Short Content Fallback
9. Chinese / English Content
10. Existing Parser Compatibility

注意：

本測試不修改 parser/parser.py。
本測試不依賴外部網站。
"""


from parser.parser import (
    remove_html_noise,
    content_score,
    find_main_content,
    parse,
)


# ==================================================
#
# Test HTML
#
# ==================================================


LONG_CONTENT = """
This is the main article content about IC semiconductor technology.

The semiconductor industry continues to grow because of artificial
intelligence, advanced packaging, chiplet technology, and increasing
demand for high performance computing.

TSMC, Intel, and other semiconductor companies continue to develop
advanced process technologies and manufacturing capabilities.

The global semiconductor supply chain is also changing rapidly as
companies invest in new fabs, advanced packaging, research and
development, and AI accelerator technologies.

This paragraph exists to provide enough content for the parser's
content density and main content detection logic.
"""


CHINESE_CONTENT = """
這是一篇關於 IC semiconductor 半導體產業的新聞文章。

人工智慧快速發展帶動先進製程、先進封裝以及高效能運算需求，
全球半導體產業持續增加投資。

台積電、Intel 以及其他半導體公司持續發展先進製程技術，
並且擴大晶圓製造與先進封裝能力。

全球半導體供應鏈也正在快速變化，各家公司持續投入新的
晶圓廠、先進封裝、研究與開發，以及 AI 加速器相關技術。
"""


# ==================================================
#
# remove_html_noise
#
# ==================================================


def test_remove_html_noise_removes_script_and_style():

    from bs4 import BeautifulSoup

    html = f"""
    <html>
        <body>
            <script>
                alert("bad");
            </script>

            <style>
                body {{ display: none; }}
            </style>

            <article>
                {LONG_CONTENT}
            </article>
        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    cleaned = remove_html_noise(
        soup
    )

    assert cleaned.find("script") is None
    assert cleaned.find("style") is None

    assert "main article content" in cleaned.get_text(
        " ",
        strip=True,
    )


def test_remove_html_noise_removes_navigation_and_footer():

    from bs4 import BeautifulSoup

    html = f"""
    <html>
        <body>

            <nav>
                Navigation Menu
            </nav>

            <article>
                {LONG_CONTENT}
            </article>

            <footer>
                Footer Information
            </footer>

        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    cleaned = remove_html_noise(
        soup
    )

    text = cleaned.get_text(
        " ",
        strip=True,
    )

    assert "Navigation Menu" not in text
    assert "Footer Information" not in text
    assert "main article content" in text


def test_remove_html_noise_removes_ad_class():

    from bs4 import BeautifulSoup

    html = f"""
    <html>
        <body>

            <div class="advertisement">
                Advertisement Content
            </div>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    cleaned = remove_html_noise(
        soup
    )

    text = cleaned.get_text(
        " ",
        strip=True,
    )

    assert "Advertisement Content" not in text
    assert "main article content" in text


# ==================================================
#
# content_score
#
# ==================================================


def test_content_score_short_content_returns_zero():

    from bs4 import BeautifulSoup

    html = """
    <div>
        Short content
    </div>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    node = soup.div

    score = content_score(
        node
    )

    assert score == 0


def test_content_score_long_content_returns_positive_score():

    from bs4 import BeautifulSoup

    html = f"""
    <article>
        {LONG_CONTENT}
    </article>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    score = content_score(
        soup.article
    )

    assert score > 0


def test_content_score_keyword_bonus():

    from bs4 import BeautifulSoup

    html = f"""
    <article>
        {LONG_CONTENT}
    </article>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    without_keyword = content_score(
        soup.article,
        keyword="",
    )

    with_keyword = content_score(
        soup.article,
        keyword="semiconductor",
    )

    assert with_keyword > without_keyword


# ==================================================
#
# find_main_content
#
# ==================================================


def test_find_main_content_prefers_article():

    from bs4 import BeautifulSoup

    html = f"""
    <html>
        <body>

            <div>
                Short page content.
            </div>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    content = find_main_content(
        soup,
        keyword="semiconductor",
    )

    assert "main article content" in content


def test_find_main_content_supports_main():

    from bs4 import BeautifulSoup

    html = f"""
    <html>
        <body>

            <main>
                {LONG_CONTENT}
            </main>

        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    content = find_main_content(
        soup,
        keyword="semiconductor",
    )

    assert "main article content" in content


def test_find_main_content_supports_article_content_class():

    from bs4 import BeautifulSoup

    html = f"""
    <html>
        <body>

            <div class="article-content">
                {LONG_CONTENT}
            </div>

        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    content = find_main_content(
        soup,
        keyword="semiconductor",
    )

    assert "main article content" in content


# ==================================================
#
# parse
#
# ==================================================


def test_parse_returns_article():

    html = f"""
    <html>
        <head>
            <title>Intel Semiconductor Technology</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "IC semiconductor",
        "https://example.com/article",
    )

    assert article is not None


def test_parse_extracts_title():

    html = f"""
    <html>
        <head>
            <title>Intel Semiconductor Technology</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "IC semiconductor",
        "https://example.com/article",
    )

    assert article.title == (
        "Intel Semiconductor Technology"
    )


def test_parse_sets_url():

    html = f"""
    <html>
        <head>
            <title>Test Article</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    url = (
        "https://example.com/"
        "semiconductor/article"
    )

    article = parse(
        html,
        "IC semiconductor",
        url,
    )

    assert article.url == url


def test_parse_sets_keyword():

    html = f"""
    <html>
        <head>
            <title>Test Article</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "IC semiconductor",
        "https://example.com/article",
    )

    assert article.keyword == (
        "IC semiconductor"
    )


def test_parse_extracts_article_content():

    html = f"""
    <html>
        <head>
            <title>Semiconductor Article</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "semiconductor",
        "https://example.com/article",
    )

    assert article.content

    assert "semiconductor" in (
        article.content.lower()
    )


def test_parse_removes_html_noise():

    html = f"""
    <html>
        <head>
            <title>Semiconductor Article</title>
        </head>

        <body>

            <nav>
                Navigation
            </nav>

            <div class="advertisement">
                Advertisement
            </div>

            <article>
                {LONG_CONTENT}
            </article>

            <footer>
                Footer
            </footer>

        </body>
    </html>
    """

    article = parse(
        html,
        "semiconductor",
        "https://example.com/article",
    )

    assert "Navigation" not in article.content
    assert "Advertisement" not in article.content
    assert "Footer" not in article.content

    assert "semiconductor" in (
        article.content.lower()
    )


# ==================================================
#
# Fallback
#
# ==================================================


def test_parse_uses_fallback_for_short_main_content():

    html = """
    <html>
        <head>
            <title>Short Article</title>
        </head>

        <body>

            <article>
                Short article content.
            </article>

            <p>
                Additional page content that is used
                by the parser fallback mechanism.
            </p>

        </body>
    </html>
    """

    article = parse(
        html,
        "article",
        "https://example.com/article",
    )

    assert article is not None
    assert article.content


# ==================================================
#
# Chinese / English
#
# ==================================================


def test_parse_chinese_content():

    html = f"""
    <html>
        <head>
            <title>半導體產業新聞</title>
        </head>

        <body>

            <article>
                {CHINESE_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "半導體",
        "https://example.com/chinese",
    )

    assert article.title == "半導體產業新聞"

    assert article.keyword == "半導體"

    assert article.content

    assert "半導體" in article.content


def test_parse_english_content():

    html = f"""
    <html>
        <head>
            <title>Global Semiconductor Industry</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "semiconductor",
        "https://example.com/english",
    )

    assert article.title == (
        "Global Semiconductor Industry"
    )

    assert article.content

    assert "semiconductor" in (
        article.content.lower()
    )


# ==================================================
#
# Empty HTML
#
# ==================================================


def test_parse_empty_html():

    article = parse(
        "",
        "semiconductor",
        "https://example.com/empty",
    )

    assert article is not None
    assert article.title == ""
    assert article.url == (
        "https://example.com/empty"
    )
    assert article.keyword == (
        "semiconductor"
    )


# ==================================================
#
# Missing Title
#
# ==================================================


def test_parse_without_title():

    html = f"""
    <html>
        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "semiconductor",
        "https://example.com/no-title",
    )

    assert article is not None
    assert article.title == ""
    assert article.url == (
        "https://example.com/no-title"
    )


# ==================================================
#
# Existing Parser Compatibility
#
# ==================================================


def test_parse_preserves_published_default():

    html = f"""
    <html>
        <head>
            <title>Test Article</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "semiconductor",
        "https://example.com/article",
    )

    assert article.published == ""


def test_parse_returns_article_with_content():

    html = f"""
    <html>
        <head>
            <title>Test Article</title>
        </head>

        <body>

            <article>
                {LONG_CONTENT}
            </article>

        </body>
    </html>
    """

    article = parse(
        html,
        "semiconductor",
        "https://example.com/article",
    )

    assert hasattr(
        article,
        "title",
    )

    assert hasattr(
        article,
        "url",
    )

    assert hasattr(
        article,
        "keyword",
    )

    assert hasattr(
        article,
        "content",
    )

    assert article.content
