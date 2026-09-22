"""
tests/V7_7/test_keyword_link_detector.py

AutoSearch V5

Keyword Link Detector Tests

測試：

    HTML + Processed Keyword
        ↓
    KeywordLinkDetector
        ↓
    Related URLs
"""

# ==================================================
#
# Imports
#
# ==================================================

from services.keyword_link_detector import (
    KeywordLinkDetector,
    detect_related_urls,
)


# ==================================================
#
# Test Data
#
# ==================================================

BASE_URL = "https://example.com/news"

PROCESSED_KEYWORD = {
    "original_keyword": "IC semiconductor",
    "target_language": "zh-TW",
    "terms": [
        {
            "original": "IC",
            "translated": "IC",
        },
        {
            "original": "semiconductor",
            "translated": "半導體",
        },
    ],
    "original_terms": [
        "IC",
        "semiconductor",
    ],
    "translated_terms": [
        "IC",
        "半導體",
    ],
}


# ==================================================
#
# Test 1
#
# Basic English Keyword Match
#
# ==================================================

def test_detect_english_keyword():
    html = """
    <html>
        <body>
            <a href="/news/1">
                Semiconductor Industry News
            </a>

            <a href="/news/2">
                Weather News
            </a>
        </body>
    </html>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == [
        "https://example.com/news/1"
    ]


# ==================================================
#
# Test 2
#
# Translated Keyword Match
#
# ==================================================

def test_detect_translated_keyword():
    html = """
    <html>
        <body>
            <a href="/news/1">
                台灣半導體產業發展
            </a>

            <a href="/news/2">
                台灣金融市場
            </a>
        </body>
    </html>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == [
        "https://example.com/news/1"
    ]


# ==================================================
#
# Test 3
#
# Original + Translated Keyword
#
# ==================================================

def test_detect_original_and_translated_keywords():
    html = """
    <html>
        <body>
            <a href="/news/1">
                IC semiconductor technology
            </a>

            <a href="/news/2">
                半導體技術
            </a>

            <a href="/news/3">
                Sports News
            </a>
        </body>
    </html>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    expected_urls = {
        "https://example.com/news/1",
        "https://example.com/news/2",
    }

    assert len(result) == 2
    assert set(result) == expected_urls

# ==================================================
#
# Test 4
#
# Relative URL
#
# ==================================================

def test_relative_url_is_resolved():
    html = """
    <a href="/article/123">
        Semiconductor Article
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url="https://example.com/",
    )

    assert result == [
        "https://example.com/article/123"
    ]


# ==================================================
#
# Test 5
#
# Duplicate URL
#
# ==================================================

def test_duplicate_url_is_removed():
    html = """
    <a href="/news/1">
        Semiconductor News
    </a>

    <a href="/news/1">
        Another Semiconductor News
    </a>

    <a href="/news/2">
        Semiconductor Technology
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    expected_urls = {
        "https://example.com/news/1",
        "https://example.com/news/2",
    }

    assert len(result) == 2
    assert set(result) == expected_urls
    assert len(result) == len(set(result))

# ==================================================
#
# Test 6
#
# Invalid Link Types
#
# ==================================================

def test_invalid_link_types_are_ignored():
    html = """
    <a href="#section">
        Semiconductor
    </a>

    <a href="javascript:void(0)">
        Semiconductor
    </a>

    <a href="mailto:test@example.com">
        Semiconductor
    </a>

    <a href="tel:123456789">
        Semiconductor
    </a>

    <a href="data:text/plain,test">
        Semiconductor
    </a>

    <a href="/news/1">
        Semiconductor News
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == [
        "https://example.com/news/1"
    ]


# ==================================================
#
# Test 7
#
# No Match
#
# ==================================================

def test_no_keyword_match_returns_empty_list():
    html = """
    <html>
        <body>
            <a href="/news/1">
                Weather Forecast
            </a>

            <a href="/news/2">
                Sports News
            </a>
        </body>
    </html>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == []


# ==================================================
#
# Test 8
#
# Empty HTML
#
# ==================================================

def test_empty_html_returns_empty_list():
    detector = KeywordLinkDetector()

    result = detector.detect(
        "",
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == []


# ==================================================
#
# Test 9
#
# Invalid Processed Keyword
#
# ==================================================

def test_invalid_processed_keyword_returns_empty_list():
    html = """
    <a href="/news/1">
        Semiconductor News
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        None,
        base_url=BASE_URL,
    )

    assert result == []


# ==================================================
#
# Test 10
#
# Invalid HTML Input
#
# ==================================================

def test_invalid_html_input_returns_empty_list():
    detector = KeywordLinkDetector()

    result = detector.detect(
        None,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == []


# ==================================================
#
# Test 11
#
# Match Count
#
# ==================================================

def test_min_match_count():
    html = """
    <a href="/news/1">
        Semiconductor News
    </a>

    <a href="/news/2">
        IC Semiconductor News
    </a>
    """

    detector = KeywordLinkDetector(
        min_match_count=2,
    )

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == [
        "https://example.com/news/2"
    ]


# ==================================================
#
# Test 12
#
# Max Results
#
# ==================================================

def test_max_results():
    html = """
    <a href="/news/1">
        Semiconductor News 1
    </a>

    <a href="/news/2">
        Semiconductor News 2
    </a>

    <a href="/news/3">
        Semiconductor News 3
    </a>
    """

    detector = KeywordLinkDetector(
        max_results=2,
    )

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    expected_urls = {
        "https://example.com/news/1",
        "https://example.com/news/2",
        "https://example.com/news/3",
    }

    # 最多 2 筆
    assert len(result) == 2

    # 所有結果必須來自候選 URL
    assert set(result).issubset(
        expected_urls
    )

    # 不得重複
    assert len(result) == len(
        set(result)
    )


# ==================================================
#
# Test 13
#
# Title Attribute
#
# ==================================================

def test_keyword_match_in_title_attribute():
    html = """
    <a
        href="/news/1"
        title="Semiconductor Industry"
    >
        Read More
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == [
        "https://example.com/news/1"
    ]


# ==================================================
#
# Test 14
#
# Aria Label
#
# ==================================================

def test_keyword_match_in_aria_label():
    html = """
    <a
        href="/news/1"
        aria-label="Semiconductor Industry News"
    >
        Read More
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == [
        "https://example.com/news/1"
    ]


# ==================================================
#
# Test 15
#
# Convenience API
#
# ==================================================

def test_convenience_api():
    html = """
    <a href="/news/1">
        Semiconductor News
    </a>
    """

    result = detect_related_urls(
        html,
        PROCESSED_KEYWORD,
        base_url=BASE_URL,
    )

    assert result == [
        "https://example.com/news/1"
    ]


# ==================================================
#
# Test 16
#
# Advertisement / Click URL Filter
#
# ==================================================

def test_advertisement_and_click_url_are_ignored():
    html = """
    <a href="/tech/webad/click.asp?Seq=98978">
        Semiconductor Advertisement
    </a>

    <a href="/news/123">
        Semiconductor Industry News
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url="https://example.com/",
    )

    assert result == [
        "https://example.com/news/123"
    ]


# ==================================================
#
# Test 17
#
# Category URL Filter
#
# ==================================================

def test_category_url_is_ignored():
    html = """
    <a href="/research/report-category/?CnlID=3&cat=CSE">
        Semiconductor Category
    </a>

    <a href="/tech/dt/n/shwnws.asp?id=123">
        Semiconductor Industry News
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url="https://example.com/",
    )

    assert result == [
        "https://example.com/tech/dt/n/shwnws.asp?id=123"
    ]


# ==================================================
#
# Test 18
#
# Search / Tag / Archive URL Filter
#
# ==================================================

def test_non_content_page_urls_are_ignored():
    html = """
    <a href="/search?q=semiconductor">
        Semiconductor Search
    </a>

    <a href="/category/semiconductor">
        Semiconductor Category
    </a>

    <a href="/tag/semiconductor">
        Semiconductor Tag
    </a>

    <a href="/archive/semiconductor">
        Semiconductor Archive
    </a>

    <a href="/news/123">
        Semiconductor Industry News
    </a>
    """

    detector = KeywordLinkDetector()

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url="https://example.com/",
    )

    assert result == [
        "https://example.com/news/123"
    ]


# ==================================================
#
# Test 19
#
# Tracking Query Filter
#
# ==================================================

def test_tracking_query_is_ignored():
    html = """
    <a
        href="/news/1?utm_source=google&utm_campaign=test"
    >
        Semiconductor News 1
    </a>

    <a
        href="/news/2?fbclid=123456"
    >
        Semiconductor News 2
    </a>

    <a
        href="/news/3?id=123"
    >
        Semiconductor News 3
    </a>
    """

    detector = KeywordLinkDetector(
        max_results=None,
    )

    result = detector.detect(
        html,
        PROCESSED_KEYWORD,
        base_url="https://example.com/",
    )

    assert result == [
        "https://example.com/news/3?id=123"
    ]


# ==================================================
#
# Test 20
#
# SQL New URL Priority
#
# ==================================================

def test_existing_sql_urls_are_deprioritized(monkeypatch):
    html = """
    <a href="/news/1">
        Semiconductor News 1
    </a>

    <a href="/news/2">
        Semiconductor News 2
    </a>

    <a href="/news/3">
        Semiconductor News 3
    </a>

    <a href="/news/4">
        Semiconductor News 4
    </a>
    """

    existing_urls = {
        "https://example.com/news/1",
        "https://example.com/news/2",
    }

    detector = KeywordLinkDetector(
        max_results=2,
    )

    # Mock MySQL 查詢結果。
    # 不實際連線資料庫，但保留 production
    # 的 SQL URL priority 邏輯。
    monkeypatch.setattr(
        detector,
        "_get_existing_urls",
        lambda urls: (
            set(urls) & existing_urls
        ),
    )

    processed_keyword = {
        "original_terms": [
            "semiconductor"
        ],
        "translated_terms": [],
    }

    result = detector.detect(
        html,
        processed_keyword,
        base_url="https://example.com",
    )

    assert len(result) == 2

    # SQL 不存在的 URL 優先：
    #
    # /news/3
    # /news/4
    #
    # 優先於：
    #
    # /news/1
    # /news/2
    #
    # 因為：
    # /news/1、/news/2 已存在 articles.url
    assert set(result) == {
        "https://example.com/news/3",
        "https://example.com/news/4",
    }