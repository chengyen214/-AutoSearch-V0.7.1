"""
tests/V5/test_job_executor_bridge_direct_url.py

AutoSearch V5

Test:
    JobExecutorBridge Direct URL Pipeline

驗證：

    Job
      ↓
    Target
      ↓
    Source Resolution
      ↓
    Direct URL
      ↓
    CrawlService
      ↓
    ParserService
      ↓
    ArticleService

不測試：

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
            "type": "direct_url",
            "url": target.url,
            "keyword": target.keyword,
        }


    def get_provider(self, target):

        return None


# ==================================================
# Fake Source Resolution Bridge
# ==================================================


class FakeSourceResolutionBridge:

    def resolve(self, source_definition):

        return source_definition


    def is_direct_url(self, resolved_source):

        return (
            resolved_source.get("type")
            == "direct_url"
        )


    def is_search(self, resolved_source):

        return False


# ==================================================
# Fake Crawl Service
# ==================================================


class FakeCrawlService:

    def __init__(self):

        self.calls = []

    def crawl_target(self, target):

        self.calls.append(target)

        return {
            "url": target.url,
            "html": (
                "<html>"
                "<body>"
                "Direct URL Test"
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

        article = SimpleNamespace(
            id=None,
            document_id="direct-url-doc-001",
            keyword=keyword,
            title="Direct URL Test Article",
            url="https://example.com/direct-test",
            source="example",
            content="Direct URL parsed content",
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

        return {
            "article": article,
            "article_id": 501,
            "status": "created",
            "archive_version": "v1",
            "ai_task": "task-501",
        }


# ==================================================
# Test
# ==================================================


def test_direct_url_pipeline():

    # ----------------------------------------------
    # Target
    # ----------------------------------------------

    target = SimpleNamespace(
        id=10,
        keyword="semiconductor",
        url="https://example.com/direct-test",
    )

    # ----------------------------------------------
    # Job
    # ----------------------------------------------

    job = SimpleNamespace(
        id=100,
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
    # Context
    # ----------------------------------------------

    assert result is not None

    assert result["job"] is job

    assert result["target"] is target

    assert len(
        result["crawl_results"]
    ) == 1

    assert len(
        result["parser_results"]
    ) == 1

    assert len(
        result["article_results"]
    ) == 1

    # ----------------------------------------------
    # Crawl
    # ----------------------------------------------

    assert len(
        crawl_service.calls
    ) == 1

    assert (
        crawl_service.calls[0]
        is target
    )

    # ----------------------------------------------
    # Parser
    # ----------------------------------------------

    assert len(
        parser_service.calls
    ) == 1

    parser_call = (
        parser_service.calls[0]
    )

    assert (
        parser_call["keyword"]
        == "semiconductor"
    )

    # ----------------------------------------------
    # ArticleService
    # ----------------------------------------------

    assert len(
        article_service.calls
    ) == 1

    article_call = (
        article_service.calls[0]
    )

    assert (
        article_call["html"]
        == (
            "<html>"
            "<body>"
            "Direct URL Test"
            "</body>"
            "</html>"
        )
    )

    assert (
        article_call["article"]
        is result["parser_results"][0]["article"]
    )

    # ----------------------------------------------
    # Final Result
    # ----------------------------------------------

    article_result = (
        result["article_results"][0]
    )

    assert (
        article_result["article_id"]
        == 501
    )

    assert (
        article_result["status"]
        == "created"
    )

    assert (
        article_result["ai_task"]
        == "task-501"
    )