"""
tests/V5/test_article_service_new_archive_version.py

AutoSearch V5

Test:
    ArticleService New Archive Version

驗證：

    Existing Article
        ↓
    Same URL
        ↓
    ArchiveService.save_html()
        ↓
    New Archive Version
        ↓
    Update Article Snapshot
        ↓
    ai_status = pending
        ↓
    Create AI Task
        ↓
    Batch Trigger

不測：

    AI Analysis
    AI Worker
    AI Scheduler
"""

from types import SimpleNamespace

from services.article_service import (
    ArticleService,
)


# ==================================================
# Fake Article Repository
# ==================================================


class FakeArticleRepository:

    def __init__(self):

        self.find_document_calls = []

        self.find_url_calls = []

        self.update_snapshot_calls = []

        self.ai_status_calls = []

    # ----------------------------------------------
    # Document ID Lookup
    # ----------------------------------------------

    def find_by_document_id(
        self,
        document_id,
    ):

        self.find_document_calls.append(
            document_id
        )

        return None

    # ----------------------------------------------
    # URL Lookup
    # ----------------------------------------------

    def find_by_url(
        self,
        url,
    ):

        self.find_url_calls.append(
            url
        )

        return SimpleNamespace(
            id=601,
            document_id="old-document-001",
            keyword="semiconductor",
            title="Old Article",
            url=url,
            source="test",
            content="Old content",
        )

    # ----------------------------------------------
    # Update Current Article Snapshot
    # ----------------------------------------------

    def update_content_snapshot(
        self,
        article_id,
        document_id,
        content,
        crawl_time,
        status,
    ):

        self.update_snapshot_calls.append(
            {
                "article_id": article_id,
                "document_id": document_id,
                "content": content,
                "crawl_time": crawl_time,
                "status": status,
            }
        )

        return True

    # ----------------------------------------------
    # Update AI Status
    # ----------------------------------------------

    def update_ai_status(
        self,
        article_id,
        status,
    ):

        self.ai_status_calls.append(
            {
                "article_id": article_id,
                "status": status,
            }
        )

        return True


# ==================================================
# Fake AI Task Repository
# ==================================================


class FakeTaskRepository:

    def __init__(self):

        self.insert_calls = []

    def insert(
        self,
        task,
    ):

        self.insert_calls.append(
            task
        )

        return task


# ==================================================
# Fake Archive Version Repository
# ==================================================


class FakeArchiveVersionRepository:

    def __init__(self):

        self.latest_version = (
            SimpleNamespace(
                version_number=1
            )
        )

    def get_latest_version(
        self,
        article_id,
    ):

        return self.latest_version


# ==================================================
# Fake Archive Service
# ==================================================


class FakeArchiveService:

    def __init__(
        self,
        version_repo,
    ):

        self.version_repo = (
            version_repo
        )

        self.save_calls = []

    def save_html(
        self,
        article_id,
        document_id,
        url,
        html,
    ):

        self.save_calls.append(
            {
                "article_id": article_id,
                "document_id": document_id,
                "url": url,
                "html": html,
            }
        )

        # ------------------------------------------
        # New Archive Version
        # ------------------------------------------

        return SimpleNamespace(
            version_number=2,
            file_hash="new-hash-002",
        )


# ==================================================
# Fake Archive Integration
# ==================================================


class FakeArchiveIntegration:

    def __init__(
        self,
        repository,
    ):

        self.repository = (
            repository
        )

    def _get_archive_repository(
        self,
    ):

        return self.repository


# ==================================================
# Fake Batch Trigger
# ==================================================


class FakeBatchTrigger:

    def __init__(self):

        self.calls = 0

    def check_and_trigger(
        self,
    ):

        self.calls += 1

        return True


# ==================================================
# Test
# ==================================================


def test_existing_url_creates_new_archive_version_and_ai_task():

    # ----------------------------------------------
    # New Crawl Article
    # ----------------------------------------------

    article = SimpleNamespace(
        id=None,
        document_id="new-document-002",
        keyword="semiconductor",
        title="Updated Semiconductor Article",
        url="https://example.com/article",
        source="test",
        content="Updated article content",
        crawl_time="2026-08-22 12:00:00",
        status="Success",
    )

    html = (
        "<html>"
        "<body>"
        "Updated HTML Content"
        "</body>"
        "</html>"
    )

    # ----------------------------------------------
    # Dependencies
    # ----------------------------------------------

    repo = FakeArticleRepository()

    task_repo = FakeTaskRepository()

    version_repo = (
        FakeArchiveVersionRepository()
    )

    archive_service = FakeArchiveService(
        version_repo=version_repo
    )

    archive_integration = (
        FakeArchiveIntegration(
            repository=version_repo
        )
    )

    batch_trigger = FakeBatchTrigger()

    # ----------------------------------------------
    # ArticleService
    # ----------------------------------------------

    service = ArticleService(
        repo=repo,
        task_repo=task_repo,
        archive_service=archive_service,
        archive_integration=archive_integration,
        batch_trigger=batch_trigger,
    )

    # ----------------------------------------------
    # Execute
    # ----------------------------------------------

    result = service.create(
        article=article,
        html=html,
    )

    # ----------------------------------------------
    # Result
    # ----------------------------------------------

    assert result is not None

    assert (
        result["status"]
        == "updated"
    )

    assert (
        result["article_id"]
        == 601
    )

    assert (
        result["archive_version"]
        .version_number
        == 2
    )

    assert (
        result["ai_task"]
        is not None
    )

    # ----------------------------------------------
    # Document Lookup
    # ----------------------------------------------

    assert (
        repo.find_document_calls
        == ["new-document-002"]
    )

    # ----------------------------------------------
    # URL Lookup
    # ----------------------------------------------

    assert (
        repo.find_url_calls
        == [
            "https://example.com/article"
        ]
    )

    # ----------------------------------------------
    # Archive
    # ----------------------------------------------

    assert (
        len(
            archive_service.save_calls
        )
        == 1
    )

    archive_call = (
        archive_service.save_calls[0]
    )

    assert (
        archive_call["article_id"]
        == 601
    )

    assert (
        archive_call["document_id"]
        == "new-document-002"
    )

    assert (
        archive_call["url"]
        == "https://example.com/article"
    )

    assert (
        archive_call["html"]
        == html
    )

    # ----------------------------------------------
    # Article Snapshot
    # ----------------------------------------------

    assert (
        len(
            repo.update_snapshot_calls
        )
        == 1
    )

    snapshot = (
        repo.update_snapshot_calls[0]
    )

    assert (
        snapshot["article_id"]
        == 601
    )

    assert (
        snapshot["document_id"]
        == "new-document-002"
    )

    assert (
        snapshot["content"]
        == "Updated article content"
    )

    assert (
        snapshot["crawl_time"]
        == "2026-08-22 12:00:00"
    )

    assert (
        snapshot["status"]
        == "Success"
    )

    # ----------------------------------------------
    # AI Status
    # ----------------------------------------------

    assert (
        repo.ai_status_calls
        == [
            {
                "article_id": 601,
                "status": "pending",
            }
        ]
    )

    # ----------------------------------------------
    # AI Task
    # ----------------------------------------------

    assert (
        len(
            task_repo.insert_calls
        )
        == 1
    )

    task = (
        task_repo.insert_calls[0]
    )

    assert (
        task.article_id
        == 601
    )

    assert (
        task.task_type
        == "analysis"
    )

    assert (
        task.status
        == "WAITING"
    )

    # ----------------------------------------------
    # Batch Trigger
    # ----------------------------------------------

    assert (
        batch_trigger.calls
        == 1
    )