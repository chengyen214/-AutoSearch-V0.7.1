"""
tests/V5/test_job_executor_bridge_search_pipeline.py

AutoSearch V5

Test:
    JobExecutorBridge Search Pipeline

驗證：

    Job
      ↓
    Target
      ↓
    TargetSourceService
      ↓
    SourceResolutionBridge
      ↓
    SearchExecutionBridge
      ↓
    SearchResult[]
      ↓
    CrawlService
      ↓
    ParserService
      ↓
    ArticleService

重要：

    SearchResult 必須逐筆完成：

        SearchResult
            ↓
        Crawl
            ↓
        Parser
            ↓
        ArticleService
            ↓
        下一筆 SearchResult

不測試：

    真實 Search API
    真實 HTTP
    真實 Parser
    真實 SQL
    Archive
    AI Analysis
    AI Worker
    AI Scheduler
"""

from types import SimpleNamespace

from services.job_executor_bridge import (
    JobExecutorBridge,
)


# ==================================================
# Fake Target Source Service
# ==================================================


class FakeTargetSourceService:

    def resolve(self, target):

        return {
            "type": "search",
            "provider": "test_search",
            "keyword": target.keyword,
        }

    def get_provider(self, target):

        return "test_search"


# ==================================================
# Fake Source Resolution Bridge
# ==================================================


class FakeSourceResolutionBridge:

    def resolve(self, source_definition):

        return source_definition

    def is_direct_url(self, resolved_source):

        return False

    def is_search(self, resolved_source):

        return (
            resolved_source.get("type")
            == "search"
        )

    def get_provider(self, resolved_source):

        return "fake-provider"

    def get_adapter(self, resolved_source):

        return "fake-adapter"

    def get_search_source(self, resolved_source):

        return "test_search"

    def is_supported_provider(self, provider):

        return provider == "test_search"


# ==================================================
# Fake Search Execution Bridge
# ==================================================


class FakeSearchExecutionBridge:

    def __init__(self):

        self.calls = []

    def execute(
        self,
        resolved_source,
        max_results=None,
    ):

        self.calls.append(
            {
                "resolved_source": resolved_source,
                "max_results": max_results,
            }
        )

        return [
            {
                "url": "https://example.com/article-1",
                "title": "Article One",
            },
            {
                "url": "https://example.com/article-2",
                "title": "Article Two",
            },
            {
                "url": "https://example.com/article-3",
                "title": "Article Three",
            },
        ]


# ==================================================
# Fake Crawl Service
# ==================================================


class FakeCrawlService:

    def __init__(self):

        self.calls = []

    def crawl_result(
        self,
        search_result,
    ):

        self.calls.append(
            search_result
        )

        url = search_result["url"]

        return {
            "url": url,
            "html": (
                "<html>"
                "<body>"
                f"Content for {url}"
                "</body>"
                "</html>"
            ),
            "status": "success",
        }


# ==================================================
# Fake Parser Service
# ==================================================


class FakeParserService:

    def __init__(self):

        self.calls = []

    def parse_crawl_result(
        self,
        crawl_result,
        keyword,
    ):

        self.calls.append(
            {
                "crawl_result": crawl_result,
                "keyword": keyword,
            }
        )

        url = crawl_result["url"]

        article = SimpleNamespace(
            id=None,
            document_id=f"doc-{url.split('/')[-1]}",
            keyword=keyword,
            title=f"Parsed {url.split('/')[-1]}",
            url=url,
            source="test",
            content="Parsed content",
        )

        return {
            "article": article,
        }


# ==================================================
# Fake Article Service
# ==================================================


class FakeArticleService:

    def __init__(self):

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

        article_id = 100 + len(
            self.calls
        )

        return {
            "article": article,
            "article_id": article_id,
            "status": "created",
            "archive_version": "v1",
            "ai_task": f"task-{article_id}",
        }


# ==================================================
# Test
# ==================================================


def test_search_pipeline_processes_results_one_by_one():

    # ----------------------------------------------
    # Job
    # ----------------------------------------------

    job = SimpleNamespace(
        id=200,
    )

    # ----------------------------------------------
    # Target
    # ----------------------------------------------

    target = SimpleNamespace(
        id=20,
        keyword="semiconductor",
    )

    # ----------------------------------------------
    # Dependencies
    # ----------------------------------------------

    target_source_service = (
        FakeTargetSourceService()
    )

    source_resolution_bridge = (
        FakeSourceResolutionBridge()
    )

    search_execution_bridge = (
        FakeSearchExecutionBridge()
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

    # ----------------------------------------------
    # Bridge
    # ----------------------------------------------

    bridge = JobExecutorBridge(
        target_source_service=(
            target_source_service
        ),
        source_resolution_bridge=(
            source_resolution_bridge
        ),
        search_execution_bridge=(
            search_execution_bridge
        ),
        crawl_service=crawl_service,
        parser_service=parser_service,
        article_service=article_service,
    )

    # ----------------------------------------------
    # Execute
    # ----------------------------------------------

    result = bridge.execute(
        job=job,
        target=target,
    )

    # ----------------------------------------------
    # Search
    # ----------------------------------------------

    assert len(
        result["search_results"]
    ) == 3

    assert len(
        search_execution_bridge.calls
    ) == 1

    # ----------------------------------------------
    # Crawl
    # ----------------------------------------------

    assert len(
        result["crawl_results"]
    ) == 3

    assert len(
        crawl_service.calls
    ) == 3

    assert (
        crawl_service.calls[0]["url"]
        == "https://example.com/article-1"
    )

    assert (
        crawl_service.calls[1]["url"]
        == "https://example.com/article-2"
    )

    assert (
        crawl_service.calls[2]["url"]
        == "https://example.com/article-3"
    )

    # ----------------------------------------------
    # Parser
    # ----------------------------------------------

    assert len(
        result["parser_results"]
    ) == 3

    assert len(
        parser_service.calls
    ) == 3

    for call in parser_service.calls:

        assert (
            call["keyword"]
            == "semiconductor"
        )

    # ----------------------------------------------
    # ArticleService
    # ----------------------------------------------

    assert len(
        result["article_results"]
    ) == 3

    assert len(
        article_service.calls
    ) == 3

    # ----------------------------------------------
    # Verify ArticleService received
    # the correct HTML for each URL
    # ----------------------------------------------

    assert (
        article_service.calls[0]["html"]
        == (
            "<html>"
            "<body>"
            "Content for "
            "https://example.com/article-1"
            "</body>"
            "</html>"
        )
    )

    assert (
        article_service.calls[1]["html"]
        == (
            "<html>"
            "<body>"
            "Content for "
            "https://example.com/article-2"
            "</body>"
            "</html>"
        )
    )

    assert (
        article_service.calls[2]["html"]
        == (
            "<html>"
            "<body>"
            "Content for "
            "https://example.com/article-3"
            "</body>"
            "</html>"
        )
    )

    # ----------------------------------------------
    # Verify persistence results
    # ----------------------------------------------

    assert (
        result["article_results"][0]["article_id"]
        == 101
    )

    assert (
        result["article_results"][1]["article_id"]
        == 102
    )

    assert (
        result["article_results"][2]["article_id"]
        == 103
    )

    assert all(
        item["status"] == "created"
        for item in result["article_results"]
    )