"""
tests/V7_7/test_google_news_provider_v7_7.py

AutoSearch V7.7

GoogleNewsProvider 微調測試。

測試範圍：

1. Google News 候選數量固定為 30
2. Google News Search Query 限制近 7 天
3. Provider 最多回傳 10 筆
4. articles.url 已存在的 URL 延後
5. Database 不存在的 URL 優先
6. New URL 不足 10 筆時，由 Existing URL 補足

注意：

    本測試不真正呼叫 Google News。
    本測試不真正連接 MySQL。

    Google News Search 與 SQL Query
    都使用 mock。

    目的：

        驗證 GoogleNewsProvider 本身的
        Provider 邏輯。
"""

from __future__ import annotations

from typing import Any

import pytest

from search.google_news_provider import (
    GoogleNewsProvider,
)

from models.search_result import (
    SearchResult,
)


# ==================================================
#
# Helpers
#
# ==================================================

def make_search_result(
    url: str,
    rank: int = 1,
):
    """
    建立測試用 SearchResult。
    """

    return SearchResult(
        url=url,
        title=f"Test Article {rank}",
        keyword="",
        search_source="google_news",
        rank=rank,
    )


def make_results(
    count: int,
):
    """
    建立指定數量的 SearchResult。
    """

    return [
        make_search_result(
            f"https://example.com/news/{index}",
            rank=index,
        )
        for index in range(
            1,
            count + 1,
        )
    ]


# ==================================================
#
# Fixtures
#
# ==================================================

@pytest.fixture
def provider():
    """
    建立 GoogleNewsProvider。
    """

    return GoogleNewsProvider()


# ==================================================
#
# Test 1
# Candidate Results = 30
#
# ==================================================

def test_google_news_requests_30_candidates(
    provider,
    monkeypatch,
):
    """
    驗證：

        V4 Google News Search
            ↓
        max_results=30
    """

    calls: list[dict[str, Any]] = []

    source_results = make_results(
        30
    )

    def mock_google_news_search(
        keyword,
        max_results=None,
    ):
        calls.append(
            {
                "keyword": keyword,
                "max_results": max_results,
            }
        )

        return source_results

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        mock_google_news_search,
    )

    monkeypatch.setattr(
        provider.url_source_grouping_service,
        "fetch_crawler_urls",
        lambda: [],
    )

    monkeypatch.setattr(
        provider,
        "_get_existing_urls",
        lambda urls: set(),
    )

    result = provider.search(
        "semiconductor"
    )

    assert len(calls) == 1

    assert calls[0]["max_results"] == 30

    assert len(result) == 10


# ==================================================
#
# Test 2
# Query = when:7d
#
# ==================================================

def test_google_news_query_is_limited_to_7_days(
    provider,
    monkeypatch,
):
    """
    驗證：

        keyword
            ↓
        keyword when:7d
            ↓
        google_news_search()
    """

    calls: list[dict[str, Any]] = []

    def mock_google_news_search(
        keyword,
        max_results=None,
    ):
        calls.append(
            {
                "keyword": keyword,
                "max_results": max_results,
            }
        )

        return make_results(
            1
        )

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        mock_google_news_search,
    )

    monkeypatch.setattr(
        provider.url_source_grouping_service,
        "fetch_crawler_urls",
        lambda: [],
    )

    monkeypatch.setattr(
        provider,
        "_get_existing_urls",
        lambda urls: set(),
    )

    provider.search(
        "semiconductor"
    )

    assert len(calls) == 1

    assert calls[0]["keyword"] == (
        "semiconductor when:7d"
    )

    assert calls[0]["max_results"] == 30


# ==================================================
#
# Test 3
# Maximum Results = 10
#
# ==================================================

def test_google_news_returns_at_most_10_results(
    provider,
    monkeypatch,
):
    """
    驗證 Provider 最多回傳 10 筆。
    """

    source_results = make_results(
        30
    )

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        lambda keyword, max_results=None: (
            source_results
        ),
    )

    monkeypatch.setattr(
        provider.url_source_grouping_service,
        "fetch_crawler_urls",
        lambda: [],
    )

    monkeypatch.setattr(
        provider,
        "_get_existing_urls",
        lambda urls: set(),
    )

    result = provider.search(
        "semiconductor"
    )

    assert len(result) == 10


# ==================================================
#
# Test 4
# New URL Priority
#
# ==================================================

def test_new_database_urls_are_prioritized(
    provider,
    monkeypatch,
):
    """
    驗證：

        Candidate
            ↓
        articles.url
            ↓
        New URL 優先
            ↓
        最多 10 筆
    """

    source_results = make_results(
        12
    )

    existing_urls = {
        "https://example.com/news/1",
        "https://example.com/news/2",
        "https://example.com/news/3",
        "https://example.com/news/4",
        "https://example.com/news/5",
        "https://example.com/news/6",
    }

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        lambda keyword, max_results=None: (
            source_results
        ),
    )

    monkeypatch.setattr(
        provider.url_source_grouping_service,
        "fetch_crawler_urls",
        lambda: [],
    )

    monkeypatch.setattr(
        GoogleNewsProvider,
        "_get_existing_urls",
        staticmethod(
            lambda urls: (
                set(urls) & existing_urls
            )
        ),
    )

    result = provider.search(
        "semiconductor"
    )

    assert len(result) == 10

    result_urls = {
        item.url
        for item in result
    }

    expected_new_urls = {
        f"https://example.com/news/{index}"
        for index in range(
            7,
            13,
        )
    }

    assert expected_new_urls.issubset(
        result_urls
    )

    assert len(result_urls) == 10

    existing_in_result = {
        url
        for url in result_urls
        if url in existing_urls
    }

    assert len(existing_in_result) == 4


# ==================================================
#
# Test 5
# Existing URL Fills Remaining Slots
#
# ==================================================

def test_existing_database_urls_fill_remaining_slots(
    provider,
    monkeypatch,
):
    """
    驗證：

        New URL < 10

    時：

        New URLs
            ↓
        Existing URLs 補足
            ↓
        最多 10 筆
    """

    source_results = make_results(
        12
    )

    existing_urls = {
        "https://example.com/news/4",
        "https://example.com/news/5",
        "https://example.com/news/6",
        "https://example.com/news/7",
        "https://example.com/news/8",
        "https://example.com/news/9",
        "https://example.com/news/10",
        "https://example.com/news/11",
        "https://example.com/news/12",
    }

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        lambda keyword, max_results=None: (
            source_results
        ),
    )

    monkeypatch.setattr(
        provider.url_source_grouping_service,
        "fetch_crawler_urls",
        lambda: [],
    )

    monkeypatch.setattr(
        provider,
        "_get_existing_urls",
        lambda urls: (
            set(urls) & existing_urls
        ),
    )

    result = provider.search(
        "semiconductor"
    )

    assert len(result) == 10

    result_urls = [
        item.url
        for item in result
    ]

    # --------------------------------------------------
    # New URLs
    #
    # /news/1
    # /news/2
    # /news/3
    #
    # 必須全部保留。
    # --------------------------------------------------

    assert (
        "https://example.com/news/1"
        in result_urls
    )

    assert (
        "https://example.com/news/2"
        in result_urls
    )

    assert (
        "https://example.com/news/3"
        in result_urls
    )

    # --------------------------------------------------
    # Remaining 7 slots
    #
    # 由 Existing URLs 補足。
    # --------------------------------------------------

    assert len(
        result_urls
    ) == 10

    assert len(
        {
            url
            for url in result_urls
            if url in existing_urls
        }
    ) == 7


# ==================================================
#
# Test 6
# Invalid max_results cannot exceed 10
#
# ==================================================

@pytest.mark.parametrize(
    "requested",
    [
        11,
        20,
        30,
        100,
    ],
)
def test_provider_never_returns_more_than_10(
    provider,
    monkeypatch,
    requested,
):
    """
    即使呼叫端要求超過 10，
    Provider 仍不能超過 max_results=10。
    """

    source_results = make_results(
        30
    )

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        lambda keyword, max_results=None: (
            source_results
        ),
    )

    monkeypatch.setattr(
        provider.url_source_grouping_service,
        "fetch_crawler_urls",
        lambda: [],
    )

    monkeypatch.setattr(
        provider,
        "_get_existing_urls",
        lambda urls: set(),
    )

    result = provider.search(
        "semiconductor",
        max_results=requested,
    )

    assert len(result) <= 10


# ==================================================
#
# Test 7
# Candidate Results Remain 30
# Even When Final Limit Is Smaller
#
# ==================================================

def test_candidate_limit_remains_30_when_final_limit_is_5(
    provider,
    monkeypatch,
):
    """
    驗證：

        final max_results
            ≠
        candidate_results

    即使最後只要求 5 筆，
    Google News 仍先取得 30 筆候選。
    """

    calls: list[dict[str, Any]] = []

    source_results = make_results(
        30
    )

    def mock_google_news_search(
        keyword,
        max_results=None,
    ):
        calls.append(
            {
                "keyword": keyword,
                "max_results": max_results,
            }
        )

        return source_results

    monkeypatch.setattr(
        "search.google_news_provider.google_news_search",
        mock_google_news_search,
    )

    monkeypatch.setattr(
        provider.url_source_grouping_service,
        "fetch_crawler_urls",
        lambda: [],
    )

    monkeypatch.setattr(
        provider,
        "_get_existing_urls",
        lambda urls: set(),
    )

    result = provider.search(
        "semiconductor",
        max_results=5,
    )

    assert len(result) == 5

    assert calls[0]["max_results"] == 30