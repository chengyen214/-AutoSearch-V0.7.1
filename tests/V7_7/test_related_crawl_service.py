"""
tests/V7_7/test_related_crawl_service.py

AutoSearch V5

RelatedCrawlService Tests

測試重點：

    1. RelatedCrawlService 不使用 CrawlService
    2. Related Crawl 可以獨立完成：
       resolve -> download -> hash -> resources
    3. Raw HTML 可以保存到 Repository
    4. ParserService 可以取得 CrawlResult + keyword
    5. ArticleService 可以取得 article + html
    6. Crawl / Parser / Article Failure 可以獨立處理
    7. process_many() 單筆失敗不影響其他 Related URL
"""


# ==================================================
#
# Standard Library
#
# ==================================================

import hashlib


from types import SimpleNamespace


# ==================================================
#
# Pytest
#
# ==================================================

import pytest


# ==================================================
#
# Related Crawl Service
#
# ==================================================

from services.related_crawl_service import (
    RelatedCrawlService,
    CrawlResult,
    RelatedCrawlResult,
)


# ==================================================
#
# Test Doubles
#
# ==================================================

class MockRepository:
    """
    Mock RawHTMLRepository。

    不連真實 MongoDB。
    """

    def __init__(self):
        self.saved = []

    def save_crawl_result(
        self,
        crawl_result,
    ):
        self.saved.append(
            crawl_result
        )

        return "mock-mongo-id"


class MockParserService:
    """
    Mock ParserService。
    """

    def __init__(
        self,
        result=None,
        error=None,
    ):
        self.result = result
        self.error = error
        self.calls = []

    def parse_crawl_result(
        self,
        crawl_result,
        keyword,
    ):
        self.calls.append(
            (
                crawl_result,
                keyword,
            )
        )

        if self.error is not None:
            raise self.error

        if self.result is not None:
            return self.result

        return {
            "article": {
                "title": "Mock Article",
            }
        }


class MockArticleService:
    """
    Mock ArticleService。
    """

    def __init__(
        self,
        result=None,
        error=None,
    ):
        self.result = result
        self.error = error
        self.calls = []

    def create(
        self,
        article,
        html,
    ):
        self.calls.append(
            {
                "article": article,
                "html": html,
            }
        )

        if self.error is not None:
            raise self.error

        if self.result is not None:
            return self.result

        return {
            "article": article,
            "article_id": 101,
            "status": "created",
        }


# ==================================================
#
# Fixtures
#
# ==================================================

@pytest.fixture
def html():
    return """
    <html>
        <head>
            <title>Test Related Article</title>
        </head>
        <body>
            <article>
                Related article content.
            </article>
        </body>
    </html>
    """


@pytest.fixture
def repository():
    return MockRepository()


@pytest.fixture
def parser_service():
    return MockParserService()


@pytest.fixture
def article_service():
    return MockArticleService()


@pytest.fixture
def downloader(html):
    def _download(url):
        return html

    return _download


@pytest.fixture
def url_resolver():
    def _resolve(url):
        return url.rstrip("/") + "/resolved"

    return _resolve


@pytest.fixture
def resource_downloader():
    def _resources(html, base_url):
        return {
            "css": [
                {
                    "url": f"{base_url}/style.css",
                    "hash": "css-hash",
                }
            ],
            "images": [
                {
                    "url": f"{base_url}/image.jpg",
                    "hash": "image-hash",
                }
            ],
        }

    return _resources


@pytest.fixture
def service(
    downloader,
    url_resolver,
    resource_downloader,
    repository,
    parser_service,
    article_service,
):
    return RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        save_raw_html=True,
        parser_service=parser_service,
        article_service=article_service,
    )


# ==================================================
#
# 1. Service Initialization
#
# ==================================================

def test_service_initialization(service):
    """
    RelatedCrawlService 可以正常建立。
    """

    assert isinstance(
        service,
        RelatedCrawlService,
    )

    assert service.downloader is not None
    assert service.url_resolver is not None
    assert service.resource_downloader is not None
    assert service.raw_html_repository is not None
    assert service.parser_service is not None
    assert service.article_service is not None


# ==================================================
#
# 2. Crawl Success
#
# ==================================================

def test_crawl_success(
    service,
    repository,
):
    """
    RelatedCrawlService.crawl()
    應成功完成完整 Crawl。
    """

    result = service.crawl(
        "https://example.com/article/1"
    )

    assert isinstance(
        result,
        CrawlResult,
    )

    assert result.success is True

    assert (
        result.url
        == "https://example.com/article/1"
    )

    assert (
        result.resolved_url
        == "https://example.com/article/1/resolved"
    )

    assert result.html is not None
    assert result.content_hash is not None

    assert result.content_hash == hashlib.sha256(
        result.html.encode("utf-8")
    ).hexdigest()

    assert result.resources["css"]
    assert result.resources["images"]

    assert len(
        repository.saved
    ) == 1

    assert (
        repository.saved[0]
        is result
    )


# ==================================================
#
# 3. Crawl Hash
#
# ==================================================

def test_generate_content_hash():
    """
    SHA-256 Hash 正確。
    """

    html = "<html>hello</html>"

    result = (
        RelatedCrawlService
        .generate_content_hash(
            html
        )
    )

    expected = hashlib.sha256(
        html.encode("utf-8")
    ).hexdigest()

    assert result == expected


# ==================================================
#
# 4. Invalid URL
#
# ==================================================

def test_crawl_invalid_url(
    service,
):
    """
    Invalid URL 應回傳失敗 CrawlResult。
    """

    result = service.crawl(
        None
    )

    assert isinstance(
        result,
        CrawlResult,
    )

    assert result.success is False
    assert result.error is not None


# ==================================================
#
# 5. Download Failure
#
# ==================================================

def test_crawl_download_failure(
    repository,
    parser_service,
    article_service,
    url_resolver,
    resource_downloader,
):
    """
    Download Exception
    不應被吞掉成成功。
    """

    def downloader(url):
        raise RuntimeError(
            "download failed"
        )

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    result = service.crawl(
        "https://example.com/fail"
    )

    assert result.success is False
    assert (
        result.error
        == "download failed"
    )

    assert repository.saved == []


# ==================================================
#
# 6. Empty HTML
#
# ==================================================

def test_crawl_empty_html(
    repository,
    parser_service,
    article_service,
    url_resolver,
    resource_downloader,
):
    """
    Empty HTML 應視為 Crawl Failure。
    """

    def downloader(url):
        return "   "

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    result = service.crawl(
        "https://example.com/empty"
    )

    assert result.success is False

    assert (
        result.error
        == "Downloaded HTML is empty"
    )

    assert repository.saved == []


# ==================================================
#
# 7. Resource Failure
#
# ==================================================

def test_resource_failure_does_not_fail_crawl(
    downloader,
    url_resolver,
    repository,
    parser_service,
    article_service,
):
    """
    Resource Download Failure
    不應讓 HTTP Crawl Failure。
    """

    def resource_downloader(
        html,
        base_url,
    ):
        raise RuntimeError(
            "resource failed"
        )

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    result = service.crawl(
        "https://example.com/resource-fail"
    )

    assert result.success is True

    assert result.resources == {
        "css": [],
        "images": [],
    }

    assert len(
        repository.saved
    ) == 1


# ==================================================
#
# 8. Process Success
#
# ==================================================

def test_process_success(
    service,
    parser_service,
    article_service,
):
    """
    完整流程：

        Crawl
          ↓
        Parser
          ↓
        Article
    """

    result = service.process(
        "https://example.com/article/2",
        "IC semiconductor",
    )

    assert isinstance(
        result,
        RelatedCrawlResult,
    )

    assert result.success is True

    assert result.status == "success"

    assert result.crawl_result is not None
    assert result.crawl_result.success is True

    assert result.parser_result is not None
    assert result.article is not None
    assert result.article_result is not None

    assert (
        result.article_result["article_id"]
        == 101
    )

    assert len(
        parser_service.calls
    ) == 1

    crawl_result, keyword = (
        parser_service.calls[0]
    )

    assert isinstance(
        crawl_result,
        CrawlResult,
    )

    assert keyword == "IC semiconductor"

    assert len(
        article_service.calls
    ) == 1

    article_call = (
        article_service.calls[0]
    )

    assert (
        article_call["article"]
        is result.article
    )

    assert (
        article_call["html"]
        == result.crawl_result.html
    )


# ==================================================
#
# 9. Process Parser Failure
#
# ==================================================

def test_process_parser_failure(
    downloader,
    url_resolver,
    resource_downloader,
    repository,
    article_service,
):
    """
    Parser Failure
    應回傳 parser_failed。
    """

    parser_service = MockParserService(
        error=RuntimeError(
            "parser failed"
        )
    )

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    result = service.process(
        "https://example.com/parser-fail",
        "semiconductor",
    )

    assert result.success is False

    assert (
        result.status
        == "parser_failed"
    )

    assert (
        result.error
        == "parser failed"
    )

    assert result.crawl_result is not None
    assert result.crawl_result.success is True

    assert result.article_result is None

    assert article_service.calls == []


# ==================================================
#
# 10. Process Invalid Parser Result
#
# ==================================================

def test_process_invalid_parser_result(
    downloader,
    url_resolver,
    resource_downloader,
    repository,
    article_service,
):
    """
    Parser 回傳沒有 Article
    應判斷為 parser_result_invalid。
    """

    parser_service = MockParserService(
        result={}
    )

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    result = service.process(
        "https://example.com/invalid-parser",
        "semiconductor",
    )

    assert result.success is False

    assert (
        result.status
        == "parser_result_invalid"
    )

    assert result.article is None
    assert result.article_result is None

    assert article_service.calls == []


# ==================================================
#
# 11. Process ArticleService Failure
#
# ==================================================

def test_process_article_service_failure(
    downloader,
    url_resolver,
    resource_downloader,
    repository,
    parser_service,
):
    """
    ArticleService Failure
    應回傳 article_service_failed。
    """

    article_service = MockArticleService(
        error=RuntimeError(
            "article save failed"
        )
    )

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    result = service.process(
        "https://example.com/article-fail",
        "semiconductor",
    )

    assert result.success is False

    assert (
        result.status
        == "article_service_failed"
    )

    assert (
        result.error
        == "article save failed"
    )

    assert result.crawl_result is not None
    assert result.parser_result is not None
    assert result.article is not None


# ==================================================
#
# 12. Invalid Keyword
#
# ==================================================

@pytest.mark.parametrize(
    "keyword",
    [
        None,
        "",
        "   ",
    ],
)
def test_process_invalid_keyword(
    service,
    keyword,
):
    """
    Invalid Keyword 不應進入 Crawl。
    """

    result = service.process(
        "https://example.com/article",
        keyword,
    )

    assert isinstance(
        result,
        RelatedCrawlResult,
    )

    assert result.success is False
    assert (
        result.status
        == "invalid_keyword"
    )


# ==================================================
#
# 13. Process Many
#
# ==================================================

def test_process_many(
    service,
):
    """
    process_many()
    應處理多個 Related URLs。
    """

    urls = [
        "https://example.com/1",
        "https://example.com/2",
        "https://example.com/3",
    ]

    results = service.process_many(
        urls,
        "semiconductor",
    )

    assert len(results) == 3

    assert all(
        isinstance(
            result,
            RelatedCrawlResult,
        )
        for result in results
    )

    assert all(
        result.success
        for result in results
    )


# ==================================================
#
# 14. Process Many Continues After Failure
#
# ==================================================

def test_process_many_continues_after_failure(
    url_resolver,
    resource_downloader,
    repository,
    parser_service,
    article_service,
):
    """
    單一 Related URL Failure
    不應中斷後續 URL。
    """

    def downloader(url):

        if url.endswith("/fail"):
            raise RuntimeError(
                "expected failure"
            )

        return "<html><body>ok</body></html>"

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    urls = [
        "https://example.com/ok-1",
        "https://example.com/fail",
        "https://example.com/ok-2",
    ]

    results = service.process_many(
        urls,
        "semiconductor",
    )

    assert len(results) == 3

    assert (
        results[0].success is True
    )

    assert (
        results[1].success is False
    )

    assert (
        results[1].status
        == "crawl_failed"
    )

    assert (
        results[2].success is True
    )


# ==================================================
#
# 15. Raw HTML Persistence
#
# ==================================================

def test_raw_html_persistence(
    service,
    repository,
):
    """
    Related Crawl 成功後
    Raw HTML 應保存至 Repository。
    """

    result = service.crawl(
        "https://example.com/persist"
    )

    assert result.success is True

    assert len(
        repository.saved
    ) == 1

    saved_result = (
        repository.saved[0]
    )

    assert (
        saved_result.url
        == result.url
    )

    assert (
        saved_result.html
        == result.html
    )

    assert (
        saved_result.content_hash
        == result.content_hash
    )

    assert (
        saved_result.resources
        == result.resources
    )


# ==================================================
#
# 16. Extract Article - Dict
#
# ==================================================

def test_extract_article_dict():
    """
    _extract_article()
    支援 dict.article。
    """

    article = {
        "title": "Test"
    }

    result = (
        RelatedCrawlService
        ._extract_article(
            {
                "article": article
            }
        )
    )

    assert result == article


# ==================================================
#
# 17. Extract Article - Object
#
# ==================================================

def test_extract_article_object():
    """
    _extract_article()
    支援 object.article。
    """

    article = {
        "title": "Test"
    }

    parser_result = SimpleNamespace(
        article=article
    )

    result = (
        RelatedCrawlService
        ._extract_article(
            parser_result
        )
    )

    assert result == article


# ==================================================
#
# 18. Extract HTML - Dict
#
# ==================================================

def test_extract_html_dict():
    """
    _extract_html()
    支援 dict.html。
    """

    html = "<html>test</html>"

    result = (
        RelatedCrawlService
        ._extract_html(
            {
                "html": html
            }
        )
    )

    assert result == html


# ==================================================
#
# 19. Extract HTML - Object
#
# ==================================================

def test_extract_html_object():
    """
    _extract_html()
    支援 object.html。
    """

    html = "<html>test</html>"

    crawl_result = SimpleNamespace(
        html=html
    )

    result = (
        RelatedCrawlService
        ._extract_html(
            crawl_result
        )
    )

    assert result == html


# ==================================================
#
# 20. Is Success
#
# ==================================================

def test_is_success(
    service,
):
    """
    is_success()
    正確判斷 Related Crawl。
    """

    success_result = service.crawl(
        "https://example.com/success"
    )

    assert (
        service.is_success(
            success_result
        )
        is True
    )

    failure_result = CrawlResult(
        url="https://example.com/failure",
        success=False,
    )

    assert (
        service.is_success(
            failure_result
        )
        is False
    )


# ==================================================
#
# 21. Get HTML
#
# ==================================================

def test_get_html(
    service,
):
    """
    get_html()
    正確回傳 HTML。
    """

    result = service.crawl(
        "https://example.com/html"
    )

    html = service.get_html(
        result
    )

    assert html == result.html


# ==================================================
#
# 22. Get Content Hash
#
# ==================================================

def test_get_content_hash(
    service,
):
    """
    get_content_hash()
    正確回傳 Hash。
    """

    result = service.crawl(
        "https://example.com/hash"
    )

    content_hash = (
        service.get_content_hash(
            result
        )
    )

    assert (
        content_hash
        == result.content_hash
    )


# ==================================================
#
# 23. Get Resources
#
# ==================================================

def test_get_resources(
    service,
):
    """
    get_resources()
    正確回傳 resources。
    """

    result = service.crawl(
        "https://example.com/resources"
    )

    resources = (
        service.get_resources(
            result
        )
    )

    assert resources == result.resources


# ==================================================
#
# 24. Final URL
#
# ==================================================

def test_final_url(
    service,
):
    """
    final_url
    優先使用 resolved_url。
    """

    result = service.crawl(
        "https://example.com/final"
    )

    assert (
        result.final_url
        == result.resolved_url
    )


# ==================================================
#
# 25. Process Status Updated
#
# ==================================================

def test_process_updated_status(
    downloader,
    url_resolver,
    resource_downloader,
    repository,
    parser_service,
):
    """
    ArticleService 回傳 updated
    時應正確反映 RelatedCrawlResult。
    """

    article_service = MockArticleService(
        result={
            "article": {
                "title": "Updated"
            },
            "article_id": 202,
            "status": "updated",
        }
    )

    service = RelatedCrawlService(
        downloader=downloader,
        url_resolver=url_resolver,
        resource_downloader=resource_downloader,
        raw_html_repository=repository,
        parser_service=parser_service,
        article_service=article_service,
    )

    result = service.process(
        "https://example.com/updated",
        "semiconductor",
    )

    assert result.status == "updated"
    assert result.success is True