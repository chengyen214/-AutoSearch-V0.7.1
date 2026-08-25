"""
tests/test_failed_webpage.py

AutoSearch V5

Integration Test

用途：

    測試剛剛 Parser 失敗的網站：

        https://iknow.stpi.niar.org.tw/Post/Read.aspx?PostID=23258

測試：

    1. Crawler
    2. SSL Certificate fallback
    3. HTML Download
    4. Parser
    5. Largest Text Fallback
    6. Article
    7. document_id
"""


from crawler.crawler import (
    download,
)


from parser.parser import (
    parse,
)


TEST_URL = (
    "https://iknow.stpi.niar.org.tw/Post/Read.aspx?PostID=23258"
)


TEST_KEYWORD = (
    "IC semiconductor"
)


def test_failed_webpage_crawl_and_parse():

    print()
    print("=" * 70)
    print("AutoSearch V5 Failed Webpage Test")
    print("=" * 70)

    print(
        f"URL      : {TEST_URL}"
    )

    print(
        f"Keyword  : {TEST_KEYWORD}"
    )

    print("=" * 70)

    # ==================================================
    # Crawl
    # ==================================================

    html = download(
        TEST_URL
    )

    assert html is not None

    assert isinstance(
        html,
        str,
    )

    assert html.strip()

    print(
        f"HTML Length: {len(html)}"
    )

    # ==================================================
    # Parser
    # ==================================================

    article = parse(
        html,
        TEST_KEYWORD,
        url=TEST_URL,
    )

    assert article is not None

    # ==================================================
    # Article Content
    # ==================================================

    assert hasattr(
        article,
        "content",
    )

    assert article.content is not None

    assert isinstance(
        article.content,
        str,
    )

    assert article.content.strip()

    assert len(article.content) >= 200

    print(
        f"Article Content Length: "
        f"{len(article.content)}"
    )

    # ==================================================
    # Document ID
    # ==================================================

    assert hasattr(
        article,
        "document_id",
    )

    assert article.document_id is not None

    assert len(
        article.document_id
    ) == 64

    print(
        f"Document ID: "
        f"{article.document_id}"
    )

    # ==================================================
    # Title
    # ==================================================

    print(
        f"Title: "
        f"{getattr(article, 'title', '')}"
    )

    # ==================================================
    # Content Preview
    # ==================================================

    print()
    print("-" * 70)
    print("CONTENT PREVIEW")
    print("-" * 70)

    print(
        article.content[:1000]
    )
    print()
    print("=" * 70)
    print("RAW HTML")
    print("=" * 70)
    print(html)
    print("=" * 70)

    print()
    print("=" * 70)
    print("TEST PASSED")
    print("=" * 70)