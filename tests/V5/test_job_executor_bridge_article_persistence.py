"""
tests/V5/test_job_executor_bridge_article_persistence.py

AutoSearch V5

Test:
    JobExecutorBridge -> ArticleService

目的：
    確認 JobExecutorBridge 能正確將：

        Parser Result
            +
        Crawl Result HTML
            ↓
        ArticleService.create()

    並正確取得 persistence result。

不測：
    Search
    Crawl HTTP
    Parser
    AI Analysis
    AI Worker
    AI Scheduler
"""

from types import SimpleNamespace

from services.job_executor_bridge import (
    JobExecutorBridge,
)


# ==================================================
# Fake ArticleService
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
            "article_id": 123,
            "status": "created",
            "archive_version": "v1",
            "ai_task": "task-123",
        }


# ==================================================
# Test
# ==================================================


def test_job_executor_bridge_persists_parser_result():

    # ----------------------------------------------
    # Fake Article
    # ----------------------------------------------

    article = SimpleNamespace(
        id=None,
        document_id="doc-test-001",
        keyword="semiconductor",
        title="Test Semiconductor Article",
        url="https://example.com/test",
        source="test",
        content="Test article content",
    )

    # ----------------------------------------------
    # Parser Result
    # ----------------------------------------------

    parser_result = {
        "article": article,
    }

    # ----------------------------------------------
    # Crawl Result
    # ----------------------------------------------

    crawl_result = {
        "html": "<html><body>Test HTML</body></html>",
    }

    # ----------------------------------------------
    # Fake ArticleService
    # ----------------------------------------------

    fake_article_service = (
        FakeArticleService()
    )

    # ----------------------------------------------
    # Bridge
    # ----------------------------------------------

    bridge = JobExecutorBridge(
        article_service=fake_article_service,
    )

    # ----------------------------------------------
    # Execute Persistence Boundary
    # ----------------------------------------------

    result = (
        bridge._persist_parser_result(
            parser_result=parser_result,
            crawl_result=crawl_result,
        )
    )

    # ----------------------------------------------
    # Result
    # ----------------------------------------------

    assert result is not None

    assert result["status"] == "created"

    assert result["article_id"] == 123

    assert result["ai_task"] == "task-123"

    # ----------------------------------------------
    # ArticleService.create()
    # must be called exactly once
    # ----------------------------------------------

    assert len(
        fake_article_service.calls
    ) == 1

    call = (
        fake_article_service.calls[0]
    )

    # ----------------------------------------------
    # Article must be passed unchanged
    # ----------------------------------------------

    assert call["article"] is article

    # ----------------------------------------------
    # HTML must be passed unchanged
    # ----------------------------------------------

    assert (
        call["html"]
        == "<html><body>Test HTML</body></html>"
    )