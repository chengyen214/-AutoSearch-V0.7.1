"""
tests/V5/test_article_service_duplicate.py

AutoSearch V5

Test:
    ArticleService Document Duplicate Detection

驗證：

    Article
      ↓
    ArticleService.create()
      ↓
    document_id 已存在
      ↓
    duplicate

確認 Duplicate 時：

    不新增 Article
    不建立 Archive
    不建立 AI Task
    回傳既有 Article
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

        self.insert_calls = []

        self.find_document_calls = []

        self.find_url_calls = []

    def find_by_document_id(
        self,
        document_id,
    ):

        self.find_document_calls.append(
            document_id
        )

        return SimpleNamespace(
            id=501,
            document_id=document_id,
            keyword="semiconductor",
            title="Existing Article",
            url="https://example.com/existing",
        )

    def find_by_url(
        self,
        url,
    ):

        self.find_url_calls.append(
            url
        )

        return None

    def insert(
        self,
        article,
    ):

        self.insert_calls.append(
            article
        )

        return SimpleNamespace(
            id=999,
            document_id=article.document_id,
        )


# ==================================================
# Fake Task Repository
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
# Fake Archive Service
# ==================================================


class FakeArchiveService:

    def __init__(self):

        self.save_calls = []

        self.version_repo = (
            FakeArchiveVersionRepository()
        )

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

        return SimpleNamespace(
            version_number=1
        )


# ==================================================
# Fake Archive Version Repository
# ==================================================


class FakeArchiveVersionRepository:

    def get_latest_version(
        self,
        article_id,
    ):

        return None


# ==================================================
# Fake Archive Integration
# ==================================================


class FakeArchiveIntegration:

    def __init__(self):

        self.repository = (
            FakeArchiveVersionRepository()
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

        return False


# ==================================================
# Test
# ==================================================


def test_document_id_duplicate_does_not_create_new_pipeline():

    # ----------------------------------------------
    # Article
    # ----------------------------------------------

    article = SimpleNamespace(
        id=None,
        document_id="document-duplicate-001",
        keyword="semiconductor",
        title="New Crawl Result",
        url="https://example.com/new",
        source="test",
        content="New content",
    )

    html = (
        "<html>"
        "<body>"
        "New HTML"
        "</body>"
        "</html>"
    )

    # ----------------------------------------------
    # Dependencies
    # ----------------------------------------------

    repo = FakeArticleRepository()

    task_repo = FakeTaskRepository()

    archive_service = FakeArchiveService()

    archive_integration = (
        FakeArchiveIntegration()
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
        == "duplicate"
    )

    assert (
        result["article_id"]
        == 501
    )

    assert (
        result["article"].document_id
        == "document-duplicate-001"
    )

    # ----------------------------------------------
    # Must NOT insert Article
    # ----------------------------------------------

    assert (
        len(repo.insert_calls)
        == 0
    )

    # ----------------------------------------------
    # Must NOT save Archive
    # ----------------------------------------------

    assert (
        len(archive_service.save_calls)
        == 0
    )

    # ----------------------------------------------
    # Must NOT create AI Task
    # ----------------------------------------------

    assert (
        len(task_repo.insert_calls)
        == 0
    )

    # ----------------------------------------------
    # Must NOT trigger AI Batch
    # ----------------------------------------------

    assert (
        batch_trigger.calls
        == 0
    )

    # ----------------------------------------------
    # Document ID lookup must happen
    # ----------------------------------------------

    assert (
        repo.find_document_calls
        == ["document-duplicate-001"]
    )