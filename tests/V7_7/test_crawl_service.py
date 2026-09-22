"""
tests/V7_7/test_crawl_service.py

AutoSearch V7.7

CrawlService integration tests.

測試範圍：

1. 原本 Crawl 流程正常
2. KeywordLinkDetector 可整合進 CrawlService
3. KeywordProcessor 正常處理 keyword
4. RelatedCrawlService 可收到偵測結果
5. Related URLs 最多 5 筆
6. 原始 HTML / hash / resources 流程不受影響
7. Crawl failure 時不會觸發 RelatedCrawlService
8. 沒有 keyword 時不會觸發 RelatedCrawlService
9. crawl_result() 可傳入 keyword
10. crawl_target() 可傳入 keyword
11. detector 發生錯誤不應破壞原始 Crawl
12. RelatedCrawlService 發生錯誤不應破壞原始 Crawl
13. Original CrawlResult 與 RelatedCrawlService 結果彼此獨立
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import pytest

from services.crawl_service import CrawlService


# ----------------------------------------------------------------------
# Mock dependencies
# ----------------------------------------------------------------------


class MockDownloader:
    """Mock HTML downloader."""

    def __init__(self, html: str, success: bool = True):
        self.html = html
        self.success = success
        self.calls: list[str] = []

    def __call__(self, url: str) -> str | None:
        self.calls.append(url)

        if not self.success:
            return None

        return self.html


class MockURLResolver:
    """Mock URL resolver."""

    def __init__(self, resolved_url: str):
        self.resolved_url = resolved_url
        self.calls: list[str] = []

    def __call__(self, url: str) -> str:
        self.calls.append(url)
        return self.resolved_url


class MockResourceDownloader:
    """Mock resource downloader."""

    def __init__(self):
        self.calls: list[str] = []

    def __call__(
        self,
        html: str,
        base_url: str,
    ) -> dict[str, Any]:
        self.calls.append(base_url)

        return {
            "css": [],
            "images": [],
        }


class MockRawHTMLRepository:
    """Mock RawHTMLRepository."""

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        self.saved: list[Any] = []

    def save(self, crawl_result: Any) -> Any:
        self.calls.append(
            {
                "method": "save",
                "crawl_result": crawl_result,
            }
        )
        self.saved.append(crawl_result)
        return crawl_result

    def save_crawl_result(
        self,
        crawl_result: Any,
    ) -> Any:
        self.calls.append(
            {
                "method": "save_crawl_result",
                "crawl_result": crawl_result,
            }
        )
        self.saved.append(crawl_result)
        return crawl_result


class MockKeywordLinkDetector:
    """
    Mock KeywordLinkDetector。

    CrawlService integration test 不直接測：
        - HTML link matching
        - URL filtering
        - MySQL articles.url
        - random selection

    那些責任由：
        tests/V7_7/test_keyword_link_detector.py
    測試。

    這裡只驗證 CrawlService 是否正確呼叫 detector。
    """

    def __init__(
        self,
        urls: list[str] | None = None,
        error: Exception | None = None,
    ):
        if urls is None:
            urls = [
                "https://example.com/news/1",
                "https://example.com/news/2",
                "https://example.com/news/3",
                "https://example.com/news/4",
                "https://example.com/news/5",
            ]

        self.urls = urls

        self.error = error
        self.calls: list[dict[str, Any]] = []

    def detect(
        self,
        html: str,
        processed_keyword: Any,
        base_url: str | None = None,
    ) -> list[str]:
        self.calls.append(
            {
                "html": html,
                "processed_keyword": processed_keyword,
                "base_url": base_url,
            }
        )

        if self.error is not None:
            raise self.error

        return list(self.urls)


class MockRelatedCrawlService:
    """
    Mock RelatedCrawlService。

    只模擬：

        process_many(
            related_urls,
            keyword,
        )

    不執行真正 Crawl / Parser / Article。
    """

    def __init__(
        self,
        error: Exception | None = None,
    ):
        self.error = error
        self.calls: list[dict[str, Any]] = []
        self.results: list[dict[str, Any]] = []

    def process_many(
        self,
        related_urls: list[str],
        keyword: str,
    ) -> list[dict[str, Any]]:
        self.calls.append(
            {
                "urls": list(related_urls),
                "keyword": keyword,
            }
        )

        if self.error is not None:
            raise self.error

        result = [
            {
                "url": url,
                "keyword": keyword,
            }
            for url in related_urls
        ]

        self.results.extend(result)

        return result


@dataclass
class MockSearchResult:
    """Mock SearchResult."""

    url: str
    keyword: str | None = None
    target_language: str | None = None


@dataclass
class MockTarget:
    """Mock Target."""

    url: str
    keyword: str | None = None
    target_language: str | None = None


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def html() -> str:
    """
    HTML containing multiple keyword-related links.

    Keyword:
        IC semiconductor
    """

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Semiconductor News</title>
    </head>
    <body>

        <nav>
            <a href="/news/1">Semiconductor Industry News</a>
            <a href="/news/2">IC Design Market</a>
        </nav>

        <main>
            <article>
                <h1>IC Semiconductor Update</h1>

                <a href="/news/3">
                    Semiconductor Technology
                </a>

                <a href="/news/4">
                    IC Semiconductor Market
                </a>

                <a href="/news/5">
                    Semiconductor Manufacturing
                </a>

                <a href="/news/6">
                    Semiconductor Supply Chain
                </a>

                <a href="/news/7">
                    Semiconductor Industry
                </a>

                <a href="/news/8">
                    Semiconductor Equipment
                </a>

                <a href="/news/9">
                    Semiconductor Foundry
                </a>

                <a href="/news/10">
                    Semiconductor Packaging
                </a>
            </article>
        </main>

    </body>
    </html>
    """


@pytest.fixture
def service_dependencies(html: str):
    """
    建立 CrawlService 所需的 mock dependencies。
    """

    downloader = MockDownloader(
        html=html
    )

    url_resolver = MockURLResolver(
        resolved_url="https://example.com/news"
    )

    resource_downloader = (
        MockResourceDownloader()
    )

    raw_html_repository = (
        MockRawHTMLRepository()
    )

    keyword_link_detector = (
        MockKeywordLinkDetector()
    )

    related_crawl_service = (
        MockRelatedCrawlService()
    )

    return {
        "downloader": downloader,
        "url_resolver": url_resolver,
        "resource_downloader": resource_downloader,
        "raw_html_repository": raw_html_repository,
        "keyword_link_detector": keyword_link_detector,
        "related_crawl_service": related_crawl_service,
    }


def create_service(
    dependencies: dict[str, Any],
    related_crawl_service=None,
    keyword_link_detector=None,
) -> CrawlService:
    """
    建立測試用 CrawlService。
    """

    if related_crawl_service is None:
        related_crawl_service = (
            dependencies["related_crawl_service"]
        )

    if keyword_link_detector is None:
        keyword_link_detector = (
            dependencies["keyword_link_detector"]
        )

    return CrawlService(
        downloader=dependencies["downloader"],
        url_resolver=dependencies["url_resolver"],
        resource_downloader=(
            dependencies["resource_downloader"]
        ),
        raw_html_repository=(
            dependencies["raw_html_repository"]
        ),
        keyword_link_detector=(
            keyword_link_detector
        ),
        related_crawl_service=(
            related_crawl_service
        ),
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_crawl_original_flow(
    service_dependencies,
    html,
):
    """
    Test 1:
    原本 CrawlService 基本流程正常。
    """

    service = create_service(
        service_dependencies
    )

    result = service.crawl(
        "https://example.com/news"
    )

    assert result is not None
    assert result.success is True

    assert result.url == (
        "https://example.com/news"
    )

    assert result.resolved_url == (
        "https://example.com/news"
    )

    assert result.html == html

    expected_hash = hashlib.sha256(
        html.encode("utf-8")
    ).hexdigest()

    assert result.content_hash == (
        expected_hash
    )

    assert result.resources == {
        "css": [],
        "images": [],
    }

    assert service_dependencies[
        "downloader"
    ].calls == [
        "https://example.com/news"
    ]

    assert service_dependencies[
        "url_resolver"
    ].calls == [
        "https://example.com/news"
    ]

    assert service_dependencies[
        "resource_downloader"
    ].calls == [
        "https://example.com/news"
    ]

    repository = service_dependencies[
        "raw_html_repository"
    ]

    assert len(repository.saved) == 1
    assert repository.saved[0] is result


def test_keyword_link_detector_integration(
    service_dependencies,
    html,
):
    """
    Test 2:
    KeywordLinkDetector 正式接入 CrawlService。

    Flow:

        CrawlService
             ↓
        download HTML
             ↓
        KeywordProcessor
             ↓
        KeywordLinkDetector
             ↓
        RelatedCrawlService
    """

    service = create_service(
        service_dependencies
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
        target_language="zh-TW",
    )

    assert result.success is True
    assert result.html == html
    assert result.content_hash

    detector = service_dependencies[
        "keyword_link_detector"
    ]

    assert len(detector.calls) == 1

    detector_call = detector.calls[0]

    assert detector_call["html"] == html

    assert detector_call["base_url"] == (
        "https://example.com/news"
    )

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert len(related_service.calls) == 1

    call = related_service.calls[0]

    assert call["keyword"] == (
        "IC semiconductor"
    )

    urls = call["urls"]

    assert isinstance(urls, list)
    assert len(urls) == 5

    expected_urls = {
        "https://example.com/news/1",
        "https://example.com/news/2",
        "https://example.com/news/3",
        "https://example.com/news/4",
        "https://example.com/news/5",
    }

    assert set(urls) == expected_urls

    repository = service_dependencies[
        "raw_html_repository"
    ]

    assert len(repository.saved) == 1
    assert repository.saved[0] is result


def test_no_keyword_does_not_trigger_related_service(
    service_dependencies,
):
    """
    Test 3:
    keyword=None 時，
    不應啟動 Related Crawl。
    """

    service = create_service(
        service_dependencies
    )

    result = service.crawl(
        "https://example.com/news"
    )

    assert result.success is True

    detector = service_dependencies[
        "keyword_link_detector"
    ]

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert detector.calls == []
    assert related_service.calls == []


def test_empty_keyword_does_not_trigger_related_service(
    service_dependencies,
):
    """
    Test 4:
    keyword="" 時，
    不應啟動 Related Crawl。
    """

    service = create_service(
        service_dependencies
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="",
    )

    assert result.success is True

    detector = service_dependencies[
        "keyword_link_detector"
    ]

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert detector.calls == []
    assert related_service.calls == []


def test_crawl_failure_does_not_trigger_related_service():
    """
    Test 5:
    原始 Crawl 失敗時，
    不應執行 Related Crawl。
    """

    html = (
        "<html><body>failed</body></html>"
    )

    dependencies = {
        "downloader": MockDownloader(
            html=html,
            success=False,
        ),
        "url_resolver": MockURLResolver(
            resolved_url=(
                "https://example.com/news"
            )
        ),
        "resource_downloader": (
            MockResourceDownloader()
        ),
        "raw_html_repository": (
            MockRawHTMLRepository()
        ),
        "keyword_link_detector": (
            MockKeywordLinkDetector()
        ),
        "related_crawl_service": (
            MockRelatedCrawlService()
        ),
    }

    service = create_service(
        dependencies
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
    )

    assert result.success is False

    assert dependencies[
        "keyword_link_detector"
    ].calls == []

    assert dependencies[
        "related_crawl_service"
    ].calls == []

    assert dependencies[
        "raw_html_repository"
    ].saved == []


def test_related_service_receives_original_keyword(
    service_dependencies,
):
    """
    Test 6:
    RelatedCrawlService 必須收到原始 keyword，
    而不是 KeywordProcessor 轉換後的結果。
    """

    service = create_service(
        service_dependencies
    )

    service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
        target_language="zh-TW",
    )

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert len(related_service.calls) == 1

    assert related_service.calls[0][
        "keyword"
    ] == "IC semiconductor"

    assert isinstance(
        related_service.calls[0]["keyword"],
        str,
    )


def test_related_urls_are_deduplicated(
    service_dependencies,
):
    """
    Test 7:
    此測試由 mock detector 模擬已完成
    URL deduplication 後的結果。

    真正的 deduplication：
        test_keyword_link_detector.py
    """

    detector = MockKeywordLinkDetector(
        urls=[
            "https://example.com/news/1",
            "https://example.com/news/1",
            "https://example.com/news/2",
            "https://example.com/news/2",
            "https://example.com/news/3",
        ]
    )

    related_service = MockRelatedCrawlService()

    service = create_service(
        service_dependencies,
        keyword_link_detector=detector,
        related_crawl_service=related_service,
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
    )

    assert result.success is True

    assert len(related_service.calls) == 1

    urls = related_service.calls[0]["urls"]

    # CrawlService 本身不做 dedup。
    # 因此只驗證 detector 結果原樣傳給 RelatedCrawlService。
    assert urls == [
        "https://example.com/news/1",
        "https://example.com/news/1",
        "https://example.com/news/2",
        "https://example.com/news/2",
        "https://example.com/news/3",
    ]


def test_crawl_result_with_keyword(
    service_dependencies,
):
    """
    Test 8:
    crawl_result(search_result, keyword=...)
    能正確把 keyword 傳入 Crawl pipeline。
    """

    service = create_service(
        service_dependencies
    )

    search_result = MockSearchResult(
        url="https://example.com/news",
    )

    result = service.crawl_result(
        search_result,
        keyword="IC semiconductor",
        target_language="zh-TW",
    )

    assert result.success is True

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert len(related_service.calls) == 1

    assert related_service.calls[0][
        "keyword"
    ] == "IC semiconductor"


def test_crawl_target_with_keyword(
    service_dependencies,
):
    """
    Test 9:
    crawl_target(target, keyword=...)
    能正確把 keyword 傳入 Crawl pipeline。
    """

    service = create_service(
        service_dependencies
    )

    target = MockTarget(
        url="https://example.com/news",
    )

    result = service.crawl_target(
        target,
        keyword="IC semiconductor",
        target_language="zh-TW",
    )

    assert result.success is True

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert len(related_service.calls) == 1

    assert related_service.calls[0][
        "keyword"
    ] == "IC semiconductor"


def test_keyword_from_search_result(
    service_dependencies,
):
    """
    Test 10:
    當 crawl_result() 沒有明確傳 keyword 時，
    可以從 search_result.keyword 取得 keyword。
    """

    service = create_service(
        service_dependencies
    )

    search_result = MockSearchResult(
        url="https://example.com/news",
        keyword="IC semiconductor",
        target_language="zh-TW",
    )

    result = service.crawl_result(
        search_result
    )

    assert result.success is True

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert len(related_service.calls) == 1

    assert related_service.calls[0][
        "keyword"
    ] == "IC semiconductor"


def test_keyword_from_target(
    service_dependencies,
):
    """
    Test 11:
    當 crawl_target() 沒有明確傳 keyword 時，
    可以從 target.keyword 取得 keyword。
    """

    service = create_service(
        service_dependencies
    )

    target = MockTarget(
        url="https://example.com/news",
        keyword="IC semiconductor",
        target_language="zh-TW",
    )

    result = service.crawl_target(
        target
    )

    assert result.success is True

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert len(related_service.calls) == 1

    assert related_service.calls[0][
        "keyword"
    ] == "IC semiconductor"


def test_related_service_failure_does_not_break_original_crawl(
    service_dependencies,
):
    """
    Test 12:
    RelatedCrawlService 如果失敗，
    原始 Crawl 不應該因此失敗。

    這是 side-branch 架構的重要保護。
    """

    related_service = MockRelatedCrawlService(
        error=RuntimeError(
            "Simulated Related Crawl failure"
        )
    )

    service = create_service(
        service_dependencies,
        related_crawl_service=related_service,
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
    )

    # Original Crawl still succeeds
    assert result.success is True

    assert result.html
    assert result.content_hash

    assert len(
        related_service.calls
    ) == 1

    repository = service_dependencies[
        "raw_html_repository"
    ]

    assert len(repository.saved) == 1
    assert repository.saved[0] is result


def test_keyword_detector_failure_does_not_break_original_crawl(
    service_dependencies,
):
    """
    Test 13:
    KeywordLinkDetector 發生錯誤時，
    原始 Crawl 仍然成功。
    """

    detector = MockKeywordLinkDetector(
        error=RuntimeError(
            "Simulated detector failure"
        )
    )

    related_service = (
        service_dependencies[
            "related_crawl_service"
        ]
    )

    service = create_service(
        service_dependencies,
        keyword_link_detector=detector,
        related_crawl_service=related_service,
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
    )

    assert result.success is True

    assert result.html is not None
    assert result.content_hash is not None

    assert len(detector.calls) == 1
    assert related_service.calls == []

    repository = service_dependencies[
        "raw_html_repository"
    ]

    assert len(repository.saved) == 1
    assert repository.saved[0] is result


def test_related_detector_uses_resolved_url_as_base(
    service_dependencies,
):
    """
    Test 14:
    Relative URL detection 應該使用 resolved_url
    作為 base URL。
    """

    service = create_service(
        service_dependencies
    )

    result = service.crawl(
        "https://example.com/original",
        keyword="IC semiconductor",
    )

    assert result.success is True

    detector = service_dependencies[
        "keyword_link_detector"
    ]

    assert len(detector.calls) == 1

    assert detector.calls[0]["base_url"] == (
        "https://example.com/news"
    )


def test_original_html_persistence_is_unchanged(
    service_dependencies,
    html,
):
    """
    Test 15:
    加入 Related Crawl 後，
    MongoDB Raw HTML persistence
    仍保存 Original HTML。
    """

    service = create_service(
        service_dependencies
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
    )

    assert result.success is True

    repository = service_dependencies[
        "raw_html_repository"
    ]

    assert len(repository.saved) == 1

    saved_result = repository.saved[0]

    assert saved_result.html == html

    assert saved_result.url == (
        "https://example.com/news"
    )

    assert saved_result.resolved_url == (
        "https://example.com/news"
    )

    expected_hash = hashlib.sha256(
        html.encode("utf-8")
    ).hexdigest()

    assert saved_result.content_hash == (
        expected_hash
    )


def test_related_service_not_called_when_no_related_urls(
    service_dependencies,
):
    """
    Test 16:
    沒有符合 keyword 的連結時，
    不應呼叫 RelatedCrawlService。
    """

    detector = MockKeywordLinkDetector(
        urls=[]
    )

    related_service = (
        service_dependencies[
            "related_crawl_service"
        ]
    )

    service = create_service(
        service_dependencies,
        keyword_link_detector=detector,
        related_crawl_service=related_service,
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
    )

    assert result.success is True

    assert len(detector.calls) == 1
    assert related_service.calls == []


def test_crawl_many_with_keyword(
    service_dependencies,
):
    """
    Test 17:
    crawl_many() 可以帶 keyword。
    """

    service = create_service(
        service_dependencies
    )

    urls = [
        "https://example.com/news/1",
        "https://example.com/news/2",
        "https://example.com/news/3",
    ]

    results = service.crawl_many(
        urls,
        keyword="IC semiconductor",
        target_language="zh-TW",
    )

    assert len(results) == 3

    assert all(
        result.success
        for result in results
    )

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert len(
        related_service.calls
    ) == 3

    assert all(
        call["keyword"]
        == "IC semiconductor"
        for call in related_service.calls
    )


def test_original_result_is_independent_from_related_result(
    service_dependencies,
):
    """
    Test 18:
    驗證最重要的架構契約：

        CrawlService
            ↓
        Original CrawlResult

    與：

        RelatedCrawlService
            ↓
        Related results

    彼此獨立。

    Original CrawlResult：
        - 不包含 related_urls
        - 不包含 Related Crawl result
        - 不被 Related Crawl result 取代
    """

    service = create_service(
        service_dependencies
    )

    result = service.crawl(
        "https://example.com/news",
        keyword="IC semiconductor",
    )

    related_service = service_dependencies[
        "related_crawl_service"
    ]

    assert result.success is True

    assert len(
        related_service.results
    ) == 5

    # --------------------------------------------------
    # Original CrawlResult remains Original CrawlResult
    # --------------------------------------------------

    assert hasattr(
        result,
        "url",
    )

    assert hasattr(
        result,
        "html",
    )

    assert hasattr(
        result,
        "content_hash",
    )

    assert hasattr(
        result,
        "resources",
    )

    assert not hasattr(
        result,
        "related_urls",
    )

    assert not hasattr(
        result,
        "related_results",
    )

    # --------------------------------------------------
    # Original result is not replaced
    # --------------------------------------------------

    repository = service_dependencies[
        "raw_html_repository"
    ]

    assert repository.saved[0] is result

    assert result.url == (
        "https://example.com/news"
    )

    assert result.html is not None

    assert result.content_hash is not None

    # --------------------------------------------------
    # Related results are separate
    # --------------------------------------------------

    assert related_service.results != []

    assert related_service.results[0][
        "url"
    ] != result.url


# ----------------------------------------------------------------------
# End
# ----------------------------------------------------------------------