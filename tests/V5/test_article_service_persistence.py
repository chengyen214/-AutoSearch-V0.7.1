"""
tests/V5/test_article_service_persistence.py

AutoSearch V5

ArticleService Persistence Pipeline Test

驗證：

    Article
        ↓
    ArticleService
        ↓
    SQL Article
        ↓
    Archive
        ↓
    AI Task WAITING

不測試：

    AI Analysis
    AI Worker
    AI Scheduler
"""

from types import SimpleNamespace

from services.article_service import ArticleService


# ==================================================
# Fake Article Repository
# ==================================================

class FakeArticleRepository:

    def __init__(self):
        self.articles = []
        self.next_id = 1

    def find_by_document_id(self, document_id):

        for article in self.articles:

            if article.document_id == document_id:
                return article

        return None

    def find_by_url(self, url):

        for article in self.articles:

            if article.url == url:
                return article

        return None

    def insert(self, article):

        article.id = self.next_id
        self.next_id += 1

        self.articles.append(article)

        return article

    def update_ai_status(
        self,
        article_id,
        status,
    ):

        for article in self.articles:

            if article.id == article_id:

                article.ai_status = status

                return True

        return False


# ==================================================
# Fake AI Task Repository
# ==================================================

class FakeAITaskRepository:

    def __init__(self):

        self.tasks = []

    def insert(self, task):

        self.tasks.append(task)

        return task


# ==================================================
# Fake Archive Service
# ==================================================

class FakeArchiveService:

    def __init__(self):

        self.saved = []

        self.version_number = 1

        self.version_repo = None

    def save_html(
        self,
        article_id,
        document_id,
        url,
        html,
    ):

        version = SimpleNamespace(
            article_id=article_id,
            document_id=document_id,
            url=url,
            version_number=self.version_number,
        )

        self.saved.append(
            {
                "article_id": article_id,
                "document_id": document_id,
                "url": url,
                "html": html,
            }
        )

        self.version_number += 1

        return version


# ==================================================
# Fake Archive Integration
# ==================================================

class FakeArchiveIntegration:

    def _get_archive_repository(self):

        return None


# ==================================================
# Fake Batch Trigger
# ==================================================

class FakeBatchTrigger:

    def __init__(self):

        self.called = False

    def check_and_trigger(self):

        self.called = True

        return False


# ==================================================
# Article Factory
# ==================================================

def make_article():

    return SimpleNamespace(
        id=None,
        document_id="test-document-001",
        keyword="semiconductor",
        title="Test Semiconductor Article",
        url="https://example.com/test-article",
        source="example",
        published=None,
        content="Test article content",
        crawl_time=None,
        status="Success",
        ai_status="pending",
    )


# ==================================================
# Test
# ==================================================

def test_article_service_create_persists_article_archive_and_ai_task():

    # ----------------------------------------------
    # Dependencies
    # ----------------------------------------------

    article_repo = FakeArticleRepository()

    task_repo = FakeAITaskRepository()

    archive_service = FakeArchiveService()

    archive_integration = FakeArchiveIntegration()

    batch_trigger = FakeBatchTrigger()

    service = ArticleService(
        repo=article_repo,
        task_repo=task_repo,
        archive_service=archive_service,
        archive_integration=archive_integration,
        batch_trigger=batch_trigger,
    )

    # ----------------------------------------------
    # Article
    # ----------------------------------------------

    article = make_article()

    html = """
    <html>
        <head>
            <title>Test Article</title>
        </head>
        <body>
            Semiconductor test content.
        </body>
    </html>
    """

    # ----------------------------------------------
    # Execute
    # ----------------------------------------------

    result = service.create(
        article=article,
        html=html,
    )

    # ----------------------------------------------
    # ArticleService Result
    # ----------------------------------------------

    assert result is not None

    assert result["status"] == "created"

    assert result["article_id"] == 1

    assert result["article"] is article

    # ----------------------------------------------
    # SQL Article
    # ----------------------------------------------

    assert len(article_repo.articles) == 1

    saved_article = article_repo.articles[0]

    assert saved_article.id == 1

    assert (
        saved_article.document_id
        == "test-document-001"
    )

    assert (
        saved_article.url
        == "https://example.com/test-article"
    )

    # ----------------------------------------------
    # Archive
    # ----------------------------------------------

    assert len(
        archive_service.saved
    ) == 1

    archive = archive_service.saved[0]

    assert archive["article_id"] == 1

    assert (
        archive["document_id"]
        == "test-document-001"
    )

    assert (
        archive["url"]
        == "https://example.com/test-article"
    )

    assert "Semiconductor test content" in (
        archive["html"]
    )

    # ----------------------------------------------
    # AI Task
    # ----------------------------------------------

    assert len(
        task_repo.tasks
    ) == 1

    task = task_repo.tasks[0]

    assert task.article_id == 1

    assert task.task_type == "analysis"

    assert task.status == "WAITING"

    assert task.priority == 0

    assert task.retry_count == 0

    # ----------------------------------------------
    # Batch Trigger
    # ----------------------------------------------

    assert (
        batch_trigger.called
        is True
    )