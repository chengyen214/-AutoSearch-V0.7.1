"""
tests/V5/test_target_execution_service.py

AutoSearch V5

TargetExecutionService Tests

測試重點：

    Direct URL：

        TargetExecutionService
            ↓
        CrawlService
            ↓
        ParserService
            ↓
        ArticleService

    Search Target：

        TargetExecutionService
            ↓
        JobExecutorBridge

重要：

    Direct URL 不應呼叫：

        JobExecutorBridge.execute_crawl()

    Direct URL 必須直接使用：

        CrawlService
        ParserService
        ArticleService
"""


# ============================================================
#
# Imports
#
# ============================================================

import pytest

from services.target_execution_service import (
    TargetExecutionService,
    default_target_execution_service,
    execute_target,
)


# ============================================================
#
# Fake Target
#
# ============================================================


class FakeTarget:

    def __init__(
        self,
        target_id=1,
        target_type="url",
        url="https://example.com",
        keyword="",
        search_provider="",
    ):

        self.id = target_id

        self.target_type = (
            target_type
        )

        self.url = url

        self.keyword = keyword

        self.search_provider = (
            search_provider
        )


# ============================================================
#
# Fake Crawl Service
#
# ============================================================


class FakeCrawlService:

    def __init__(
        self,
        result=None,
        error=None,
    ):

        self.result = (
            result
            if result is not None
            else {
                "html":
                    "<html>"
                    "<title>Example</title>"
                    "</html>",
            }
        )

        self.error = error

        self.calls = []

    def crawl_target(
        self,
        target,
    ):

        self.calls.append(
            target
        )

        if self.error is not None:

            raise self.error

        return self.result


# ============================================================
#
# Fake Parser Service
#
# ============================================================


class FakeParserService:

    def __init__(
        self,
        result=None,
        error=None,
    ):

        self.result = (
            result
            if result is not None
            else {
                "article":
                    {
                        "document_id":
                            "doc-001",

                        "title":
                            "Example",

                        "url":
                            "https://example.com",
                    }
            }
        )

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

        return self.result


# ============================================================
#
# Fake Article Service
#
# ============================================================


class FakeArticleService:

    def __init__(
        self,
        result=None,
        error=None,
    ):

        self.result = (
            result
            if result is not None
            else {
                "status":
                    "created",

                "article":
                    {
                        "document_id":
                            "doc-001",
                    },

                "article_id":
                    100,

                "archive_version":
                    1,

                "ai_task":
                    {
                        "status":
                            "WAITING",
                    },
            }
        )

        self.error = error

        self.calls = []

    def create(
        self,
        article,
        html,
    ):

        self.calls.append(
            (
                article,
                html,
            )
        )

        if self.error is not None:

            raise self.error

        return self.result


# ============================================================
#
# Fake Job Executor Bridge
#
# ============================================================


class FakeJobExecutorBridge:

    def __init__(
        self,
        direct_url=True,
        search=False,
    ):

        self.direct_url = (
            direct_url
        )

        self.search = (
            search
        )

        self.execute_crawl_calls = []

        self.execute_search_calls = []

        self.execute_search_and_crawl_calls = []

    # --------------------------------------------------------
    # Target Type
    # --------------------------------------------------------

    def is_direct_url(
        self,
        target,
    ):

        return self.direct_url

    def is_search(
        self,
        target,
    ):

        return self.search

    # --------------------------------------------------------
    # Direct Crawl
    #
    # This should NOT be called by Direct URL execution.
    # --------------------------------------------------------

    def execute_crawl(
        self,
        target,
    ):

        self.execute_crawl_calls.append(
            target
        )

        return {
            "called":
                True
        }

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    def execute_search(
        self,
        target,
        max_results=None,
    ):

        self.execute_search_calls.append(
            (
                target,
                max_results,
            )
        )

        return [
            "search-result"
        ]

    def execute_search_and_crawl(
        self,
        target,
        max_results=None,
    ):

        self.execute_search_and_crawl_calls.append(
            (
                target,
                max_results,
            )
        )

        return {
            "status":
                "success"
        }

    # --------------------------------------------------------
    # Source
    # --------------------------------------------------------

    def resolve_source(
        self,
        target,
    ):

        return {
            "target":
                target
        }

    def resolve_resolved_source(
        self,
        target,
    ):

        return {
            "target":
                target
        }

    # --------------------------------------------------------
    # Provider
    # --------------------------------------------------------

    def get_provider(
        self,
        target,
    ):

        return "google"

    def get_resolved_provider(
        self,
        target,
    ):

        return "google"

    def get_resolved_adapter(
        self,
        target,
    ):

        return "google-adapter"

    def get_resolved_search_source(
        self,
        target,
    ):

        return "google-search"

    def is_supported_provider(
        self,
        provider,
    ):

        return provider in (
            "google",
            "google_news",
        )


# ============================================================
#
# Factory
#
# ============================================================


def create_service(
    *,
    target_type="url",
    keyword="",
    crawl_result=None,
    parser_result=None,
    article_result=None,
    crawl_error=None,
    parser_error=None,
    article_error=None,
    bridge=None,
):

    target = FakeTarget(
        target_type=target_type,
        keyword=keyword,
    )

    crawl_service = FakeCrawlService(
        result=crawl_result,
        error=crawl_error,
    )

    parser_service = FakeParserService(
        result=parser_result,
        error=parser_error,
    )

    article_service = FakeArticleService(
        result=article_result,
        error=article_error,
    )

    if bridge is None:

        bridge = FakeJobExecutorBridge(
            direct_url=(
                target_type == "url"
            ),
            search=(
                target_type == "search"
            ),
        )

    service = TargetExecutionService(
        job_executor_bridge=bridge,
        crawl_service=crawl_service,
        parser_service=parser_service,
        article_service=article_service,
    )

    return (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    )


# ============================================================
#
# Initialization
#
# ============================================================


def test_service_initializes_with_injected_services():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service()

    assert (
        service.crawl_service
        is crawl_service
    )

    assert (
        service.parser_service
        is parser_service
    )

    assert (
        service.article_service
        is article_service
    )

    assert (
        service.job_executor_bridge
        is bridge
    )


# ============================================================
#
# Validation
#
# ============================================================


def test_execute_rejects_none_target():

    service = TargetExecutionService(
        job_executor_bridge=FakeJobExecutorBridge(),
        crawl_service=FakeCrawlService(),
        parser_service=FakeParserService(),
        article_service=FakeArticleService(),
    )

    with pytest.raises(
        ValueError,
        match="target cannot be None",
    ):

        service.execute(
            None
        )


def test_execute_direct_url_rejects_none_target():

    service = TargetExecutionService(
        job_executor_bridge=FakeJobExecutorBridge(),
        crawl_service=FakeCrawlService(),
        parser_service=FakeParserService(),
        article_service=FakeArticleService(),
    )

    with pytest.raises(
        ValueError,
        match="target cannot be None",
    ):

        service.execute_direct_url(
            None
        )


def test_validate_target():

    target = FakeTarget()

    assert (
        TargetExecutionService
        ._validate_target(
            target
        )
        is True
    )


def test_validate_target_rejects_none():

    with pytest.raises(
        ValueError,
        match="target cannot be None",
    ):

        TargetExecutionService._validate_target(
            None
        )


# ============================================================
#
# Target Type
#
# ============================================================


def test_is_direct_url():

    (
        service,
        target,
        *_,
    ) = create_service(
        target_type="url"
    )

    assert (
        service.is_direct_url(
            target
        )
        is True
    )


def test_url_target_is_not_search():

    (
        service,
        target,
        *_,
    ) = create_service(
        target_type="url"
    )

    assert (
        service.is_search(
            target
        )
        is False
    )


def test_is_search():

    (
        service,
        target,
        *_,
    ) = create_service(
        target_type="search"
    )

    assert (
        service.is_search(
            target
        )
        is True
    )


def test_search_target_is_not_direct_url():

    (
        service,
        target,
        *_,
    ) = create_service(
        target_type="search"
    )

    assert (
        service.is_direct_url(
            target
        )
        is False
    )


# ============================================================
#
# Direct URL Pipeline
#
# ============================================================


def test_execute_direct_url_calls_crawl_service():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service()

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        len(
            crawl_service.calls
        )
        == 1
    )

    assert (
        crawl_service.calls[0]
        is target
    )

    assert (
        bridge.execute_crawl_calls
        == []
    )


def test_execute_direct_url_calls_parser_service():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        keyword="IC semiconductor"
    )

    service.execute_direct_url(
        target
    )

    assert (
        len(
            parser_service.calls
        )
        == 1
    )

    crawl_result, keyword = (
        parser_service.calls[0]
    )

    assert (
        crawl_result
        == crawl_service.result
    )

    assert (
        keyword
        == "IC semiconductor"
    )


def test_execute_direct_url_calls_article_service():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service()

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        len(
            article_service.calls
        )
        == 1
    )

    article, html = (
        article_service.calls[0]
    )

    assert (
        article
        == parser_service.result[
            "article"
        ]
    )

    assert (
        html
        == crawl_service.result[
            "html"
        ]
    )


def test_execute_direct_url_pipeline_order():

    events = []

    class Crawl:

        def crawl_target(
            self,
            target,
        ):

            events.append(
                "crawl"
            )

            return {
                "html":
                    "<html>test</html>"
            }

    class Parser:

        def parse_crawl_result(
            self,
            crawl_result,
            keyword,
        ):

            events.append(
                "parser"
            )

            return {
                "article":
                    {
                        "document_id":
                            "doc-001"
                    }
            }

    class Article:

        def create(
            self,
            article,
            html,
        ):

            events.append(
                "article"
            )

            return {
                "status":
                    "created",

                "article_id":
                    1,

                "ai_task":
                    {
                        "status":
                            "WAITING"
                    },
            }

    service = TargetExecutionService(
        job_executor_bridge=FakeJobExecutorBridge(),
        crawl_service=Crawl(),
        parser_service=Parser(),
        article_service=Article(),
    )

    target = FakeTarget()

    service.execute_direct_url(
        target
    )

    assert events == [
        "crawl",
        "parser",
        "article",
    ]


def test_execute_url_target():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service()

    result = (
        service.execute(
            target
        )
    )

    assert (
        result["article_result"]["status"]
        == "created"
    )

    assert (
        len(
            crawl_service.calls
        )
        == 1
    )

    assert (
        len(
            parser_service.calls
        )
        == 1
    )

    assert (
        len(
            article_service.calls
        )
        == 1
    )

    assert (
        bridge.execute_crawl_calls
        == []
    )


# ============================================================
#
# Direct URL Failure
#
# ============================================================


def test_direct_url_crawl_failure():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        crawl_error=RuntimeError(
            "crawl failed"
        )
    )

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["crawl_result"]
        is None
    )

    assert (
        result["parser_result"]
        is None
    )

    assert (
        result["article_result"]["status"]
        == "crawl_failed"
    )

    assert (
        parser_service.calls
        == []
    )

    assert (
        article_service.calls
        == []
    )

    assert (
        bridge.execute_crawl_calls
        == []
    )


def test_direct_url_crawl_returns_none():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        crawl_result=None
    )

    crawl_service.result = None

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["crawl_result"]
        is None
    )

    assert (
        result["article_result"]["status"]
        == "crawl_failed"
    )

    assert (
        parser_service.calls
        == []
    )

    assert (
        article_service.calls
        == []
    )


def test_direct_url_parser_failure():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        parser_error=RuntimeError(
            "parser failed"
        )
    )

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["crawl_result"]
        is not None
    )

    assert (
        result["parser_result"]
        is None
    )

    assert (
        result["article_result"]["status"]
        == "parser_failed"
    )

    assert (
        article_service.calls
        == []
    )

    assert (
        bridge.execute_crawl_calls
        == []
    )


def test_direct_url_parser_returns_none():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service()

    parser_service.result = None

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["parser_result"]
        is None
    )

    assert (
        result["article_result"]["status"]
        == "parser_failed"
    )

    assert (
        article_service.calls
        == []
    )


def test_direct_url_parser_result_invalid():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        parser_result={
            "invalid":
                True
        }
    )

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["article_result"]["status"]
        == "parser_result_invalid"
    )

    assert (
        article_service.calls
        == []
    )


def test_direct_url_html_missing():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        crawl_result={
            "status":
                "success"
        }
    )

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["article_result"]["status"]
        == "html_missing"
    )

    assert (
        article_service.calls
        == []
    )


def test_direct_url_article_service_failure():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        article_error=RuntimeError(
            "article persistence failed"
        )
    )

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["article_result"]["status"]
        == "article_service_failed"
    )

    assert (
        result["article_result"]["article_id"]
        is None
    )


# ============================================================
#
# Search Target
#
# ============================================================


def test_execute_search_target_is_not_reimplemented():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        target_type="search"
    )

    with pytest.raises(
        ValueError,
        match="Search Target execution",
    ):

        service.execute(
            target
        )

    assert (
        crawl_service.calls
        == []
    )

    assert (
        parser_service.calls
        == []
    )

    assert (
        article_service.calls
        == []
    )


def test_execute_search_delegates_to_bridge():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        target_type="search"
    )

    result = (
        service.execute_search(
            target
        )
    )

    assert (
        result
        == [
            "search-result"
        ]
    )

    assert (
        len(
            bridge.execute_search_calls
        )
        == 1
    )


def test_execute_search_default_max_results():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        target_type="search"
    )

    service.execute_search(
        target
    )

    assert (
        bridge.execute_search_calls[0][1]
        is None
    )


def test_execute_search_with_max_results():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        target_type="search"
    )

    service.execute_search(
        target,
        max_results=20,
    )

    assert (
        bridge.execute_search_calls[0][1]
        == 20
    )


def test_execute_search_rejects_url_target():

    (
        service,
        target,
        *_,
    ) = create_service(
        target_type="url"
    )

    with pytest.raises(
        ValueError,
        match="not a Search Target",
    ):

        service.execute_search(
            target
        )


def test_execute_search_and_crawl_delegates_to_bridge():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service(
        target_type="search"
    )

    result = (
        service.execute_search_and_crawl(
            target,
            max_results=10,
        )
    )

    assert (
        result["status"]
        == "success"
    )

    assert (
        len(
            bridge.execute_search_and_crawl_calls
        )
        == 1
    )

    assert (
        bridge
        .execute_search_and_crawl_calls[0][1]
        == 10
    )

    assert (
        crawl_service.calls
        == []
    )

    assert (
        parser_service.calls
        == []
    )

    assert (
        article_service.calls
        == []
    )


def test_execute_search_and_crawl_rejects_url_target():

    (
        service,
        target,
        *_,
    ) = create_service(
        target_type="url"
    )

    with pytest.raises(
        ValueError,
        match="not a Search Target",
    ):

        service.execute_search_and_crawl(
            target
        )


# ============================================================
#
# Execute Crawl
#
# ============================================================


def test_execute_crawl_delegates_to_direct_url():

    (
        service,
        target,
        crawl_service,
        parser_service,
        article_service,
        bridge,
    ) = create_service()

    result = (
        service.execute_crawl(
            target
        )
    )

    assert (
        result["article_result"]["status"]
        == "created"
    )

    assert (
        len(
            crawl_service.calls
        )
        == 1
    )

    assert (
        bridge.execute_crawl_calls
        == []
    )


def test_execute_direct_url_rejects_search_target():

    (
        service,
        target,
        *_,
    ) = create_service(
        target_type="search"
    )

    with pytest.raises(
        ValueError,
        match="not a Direct URL Target",
    ):

        service.execute_direct_url(
            target
        )


# ============================================================
#
# Source Resolution
#
# ============================================================


def test_resolve_source_delegates_to_bridge():

    (
        service,
        target,
        *_,
    ) = create_service()

    result = (
        service.resolve_source(
            target
        )
    )

    assert (
        result["target"]
        is target
    )


def test_resolve_resolved_source_delegates_to_bridge():

    (
        service,
        target,
        *_,
    ) = create_service()

    result = (
        service.resolve_resolved_source(
            target
        )
    )

    assert (
        result["target"]
        is target
    )


# ============================================================
#
# Provider
#
# ============================================================


def test_get_provider():

    (
        service,
        target,
        *_,
    ) = create_service()

    assert (
        service.get_provider(
            target
        )
        == "google"
    )


def test_get_resolved_provider():

    (
        service,
        target,
        *_,
    ) = create_service()

    assert (
        service.get_resolved_provider(
            target
        )
        == "google"
    )


def test_get_resolved_adapter():

    (
        service,
        target,
        *_,
    ) = create_service()

    assert (
        service.get_resolved_adapter(
            target
        )
        == "google-adapter"
    )


def test_get_resolved_search_source():

    (
        service,
        target,
        *_,
    ) = create_service()

    assert (
        service.get_resolved_search_source(
            target
        )
        == "google-search"
    )


def test_is_supported_provider():

    (
        service,
        *_,
    ) = create_service()

    assert (
        service.is_supported_provider(
            "google"
        )
        is True
    )

    assert (
        service.is_supported_provider(
            "unknown"
        )
        is False
    )


# ============================================================
#
# Helpers
#
# ============================================================


def test_get_target_id_from_dict():

    target = {
        "id":
            123
    }

    assert (
        TargetExecutionService
        ._get_target_id(
            target
        )
        == 123
    )


def test_get_target_id_from_object():

    target = FakeTarget(
        target_id=456
    )

    assert (
        TargetExecutionService
        ._get_target_id(
            target
        )
        == 456
    )


def test_get_target_id_from_none():

    assert (
        TargetExecutionService
        ._get_target_id(
            None
        )
        is None
    )


def test_get_keyword_from_target():

    target = FakeTarget(
        keyword="  IC semiconductor  "
    )

    assert (
        TargetExecutionService
        ._get_keyword(
            target
        )
        == "IC semiconductor"
    )


def test_get_keyword_from_dict():

    target = {
        "keyword":
            "  semiconductor  "
    }

    assert (
        TargetExecutionService
        ._get_keyword(
            target
        )
        == "semiconductor"
    )


def test_get_keyword_missing_returns_empty():

    target = FakeTarget(
        keyword=""
    )

    assert (
        TargetExecutionService
        ._get_keyword(
            target
        )
        == ""
    )


def test_extract_article_from_dict():

    parser_result = {
        "article":
            {
                "document_id":
                    "doc-001"
            }
    }

    article = (
        TargetExecutionService
        ._extract_article(
            parser_result
        )
    )

    assert (
        article
        == parser_result["article"]
    )


def test_extract_article_from_document_dict():

    article = {
        "document_id":
            "doc-001"
    }

    result = (
        TargetExecutionService
        ._extract_article(
            article
        )
    )

    assert (
        result
        == article
    )


def test_extract_article_invalid():

    assert (
        TargetExecutionService
        ._extract_article(
            {
                "invalid":
                    True
            }
        )
        is None
    )


def test_extract_html_from_dict():

    crawl_result = {
        "html":
            "<html></html>"
    }

    assert (
        TargetExecutionService
        ._extract_html(
            crawl_result
        )
        == "<html></html>"
    )


def test_extract_html_from_raw_html():

    crawl_result = {
        "raw_html":
            "<html>raw</html>"
    }

    assert (
        TargetExecutionService
        ._extract_html(
            crawl_result
        )
        == "<html>raw</html>"
    )


def test_extract_html_missing():

    assert (
        TargetExecutionService
        ._extract_html(
            {
                "status":
                    "success"
            }
        )
        is None
    )


def test_get_result_status():

    assert (
        TargetExecutionService
        ._get_result_status(
            {
                "status":
                    "created"
            }
        )
        == "created"
    )


def test_get_result_status_unknown():

    assert (
        TargetExecutionService
        ._get_result_status(
            {}
        )
        == "unknown"
    )


# ============================================================
#
# Default Service
#
# ============================================================


def test_default_service_exists():

    assert (
        default_target_execution_service
        is not None
    )

    assert isinstance(
        default_target_execution_service,
        TargetExecutionService,
    )


# ============================================================
#
# Convenience Function
#
# ============================================================


def test_execute_target_function():

    bridge = FakeJobExecutorBridge(
        direct_url=True
    )

    crawl_service = (
        FakeCrawlService()
    )

    parser_service = (
        FakeParserService()
    )

    article_service = (
        FakeArticleService()
    )

    service = TargetExecutionService(
        job_executor_bridge=bridge,
        crawl_service=crawl_service,
        parser_service=parser_service,
        article_service=article_service,
    )

    target = FakeTarget()

    result = (
        service.execute(
            target
        )
    )

    assert (
        result["article_result"]["status"]
        == "created"
    )


# ============================================================
#
# Direct Pipeline AI Task Preservation
#
# ============================================================


def test_direct_url_preserves_article_service_ai_task():

    article_result = {
        "status":
            "created",

        "article_id":
            999,

        "archive_version":
            3,

        "ai_task":
            {
                "id":
                    123,

                "status":
                    "WAITING",
            },
    }

    (
        service,
        target,
        *_,
    ) = create_service(
        article_result=article_result
    )

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["article_result"]["article_id"]
        == 999
    )

    assert (
        result["article_result"]["ai_task"]["id"]
        == 123
    )

    assert (
        result["article_result"]["ai_task"]["status"]
        == "WAITING"
    )


# ============================================================
#
# Direct URL Must Not Use Bridge Crawl
#
# ============================================================


def test_direct_url_does_not_call_bridge_execute_crawl():

    bridge = FakeJobExecutorBridge(
        direct_url=True
    )

    crawl_service = (
        FakeCrawlService()
    )

    parser_service = (
        FakeParserService()
    )

    article_service = (
        FakeArticleService()
    )

    service = TargetExecutionService(
        job_executor_bridge=bridge,
        crawl_service=crawl_service,
        parser_service=parser_service,
        article_service=article_service,
    )

    target = FakeTarget()

    service.execute_direct_url(
        target
    )

    assert (
        bridge.execute_crawl_calls
        == []
    )


# ============================================================
#
# Direct URL Complete Pipeline Result
#
# ============================================================


def test_direct_url_returns_all_pipeline_results():

    crawl_result = {
        "html":
            "<html>test</html>"
    }

    parser_result = {
        "article":
            {
                "document_id":
                    "doc-100"
            }
    }

    article_result = {
        "status":
            "created",

        "article_id":
            100,

        "archive_version":
            1,

        "ai_task":
            {
                "status":
                    "WAITING"
            },
    }

    (
        service,
        target,
        *_,
    ) = create_service(
        crawl_result=crawl_result,
        parser_result=parser_result,
        article_result=article_result,
    )

    result = (
        service.execute_direct_url(
            target
        )
    )

    assert (
        result["crawl_result"]
        == crawl_result
    )

    assert (
        result["parser_result"]
        == parser_result
    )

    assert (
        result["article_result"]
        == article_result
    )


# ============================================================
#
# Public API
#
# ============================================================


def test_public_api():

    from services.target_execution_service import (
        TargetExecutionService,
        default_target_execution_service,
        execute_target,
    )

    assert (
        TargetExecutionService
        is not None
    )

    assert (
        default_target_execution_service
        is not None
    )

    assert callable(
        execute_target
    )
