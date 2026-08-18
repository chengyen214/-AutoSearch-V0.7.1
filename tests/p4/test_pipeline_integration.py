"""
tests/p4/test_pipeline_integration.py

AutoSearch V4

P4.8 Pipeline Integration

測試:

    ArticleService
        ↓
    Search
        ↓
    KeywordStrategy
        ↓
    SearchResult
        ↓
    Download
        ↓
    Parser
        ↓
    Article
        ↓
    Archive
        ↓
    AI Task
"""


from types import SimpleNamespace


from services.article_service import (
    ArticleService,
)


# ==================================================
#
# Helpers
#
# ==================================================


class FakeRepository:
    """Fake ArticleRepository。"""

    def __init__(self):
        self.inserted = []
        self.articles = []

    def insert(self, article):
        article.id = len(self.articles) + 1
        self.articles.append(article)
        self.inserted.append(article)
        return article

    def find_by_url(self, url):
        for article in self.articles:
            if article.url == url:
                return article

        return None

    def find_all(self, limit=None):
        if limit is None:
            return list(self.articles)

        return self.articles[:limit]

    def close(self):
        pass


class FakeTaskRepository:
    """Fake AITaskRepository。"""

    def __init__(self):
        self.tasks = []

    def insert(self, task):
        task.id = len(self.tasks) + 1
        self.tasks.append(task)
        return task


class FakeArchiveService:
    """Fake ArchiveService。"""

    def __init__(self):
        self.saved = []

    def save_html(
        self,
        article_id,
        url,
        html,
    ):
        version = SimpleNamespace(
            id=len(self.saved) + 1,
            article_id=article_id,
            url=url,
            file_hash="test-hash",
            version_number=len(self.saved) + 1,
        )

        self.saved.append(
            {
                "article_id": article_id,
                "url": url,
                "html": html,
            }
        )

        return version


class FakeArchiveIntegration:
    """Fake ArchiveIntegration。"""

    def _get_archive_repository(self):
        return None


class FakeBatchTrigger:
    """Fake AIBatchTriggerService。"""

    def __init__(self):
        self.calls = 0

    def check_and_trigger(self):
        self.calls += 1
        return False


# ==================================================
#
# Test 1
#
# ArticleService 使用統一 Search API
#
# ==================================================


def test_article_service_uses_unified_search(
    monkeypatch,
):
    """
    ArticleService.create()
    必須使用 search.search_adapter.search。
    """

    search_calls = []

    result = SimpleNamespace(
        title="Test Article",
        url="https://example.com/article",
        source="Example",
        published=None,
    )

    def fake_search(keyword):
        search_calls.append(keyword)
        return [result]

    monkeypatch.setattr(
        "services.article_service.search",
        fake_search,
    )

    monkeypatch.setattr(
        "services.article_service.download",
        lambda url, headers: "<html></html>",
    )

    monkeypatch.setattr(
        "services.article_service.parse",
        lambda html, keyword: SimpleNamespace(
            keyword=keyword,
            title="Parsed Article",
            url="",
            source="",
            published=None,
            content="This is test article content.",
            status="",
        ),
    )

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    service = ArticleService(
        repo=FakeRepository(),
        task_repo=FakeTaskRepository(),
        archive_service=FakeArchiveService(),
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=FakeBatchTrigger(),
    )

    result_data = service.create(
        "  IC   semiconductor  "
    )

    assert search_calls == [
        "  IC   semiconductor  "
    ]

    assert result_data["total"] == 1


# ==================================================
#
# Test 2
#
# Search Result → Download
#
# ==================================================


def test_pipeline_search_result_to_download(
    monkeypatch,
):
    """
    Search Result 必須進入 Download Pipeline。
    """

    download_calls = []

    search_result = SimpleNamespace(
        title="Test Article",
        url="https://example.com/article",
        source="Example",
        published=None,
    )

    def fake_search(keyword):
        return [search_result]

    def fake_download(
        url,
        headers,
    ):
        download_calls.append(
            {
                "url": url,
                "headers": headers,
            }
        )

        return "<html>test</html>"

    monkeypatch.setattr(
        "services.article_service.search",
        fake_search,
    )

    monkeypatch.setattr(
        "services.article_service.download",
        fake_download,
    )

    monkeypatch.setattr(
        "services.article_service.parse",
        lambda html, keyword: None,
    )

    service = ArticleService(
        repo=FakeRepository(),
        task_repo=FakeTaskRepository(),
        archive_service=FakeArchiveService(),
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=FakeBatchTrigger(),
    )

    service.create("IC semiconductor")

    assert len(download_calls) == 1

    assert (
        download_calls[0]["url"]
        == "https://example.com/article"
    )


# ==================================================
#
# Test 3
#
# Download → Parser
#
# ==================================================


def test_pipeline_download_to_parser(
    monkeypatch,
):
    """
    Download 成功後必須進入 Parser。
    """

    parse_calls = []

    search_result = SimpleNamespace(
        title="Test Article",
        url="https://example.com/article",
        source="Example",
        published=None,
    )

    monkeypatch.setattr(
        "services.article_service.search",
        lambda keyword: [search_result],
    )

    monkeypatch.setattr(
        "services.article_service.download",
        lambda url, headers: "<html>test</html>",
    )

    def fake_parse(
        html,
        keyword,
    ):
        parse_calls.append(
            {
                "html": html,
                "keyword": keyword,
            }
        )

        return SimpleNamespace(
            keyword=keyword,
            title="Parsed Article",
            url="",
            source="",
            published=None,
            content="Test article content.",
            status="",
        )

    monkeypatch.setattr(
        "services.article_service.parse",
        fake_parse,
    )

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    service = ArticleService(
        repo=FakeRepository(),
        task_repo=FakeTaskRepository(),
        archive_service=FakeArchiveService(),
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=FakeBatchTrigger(),
    )

    service.create(
        "IC semiconductor"
    )

    assert len(parse_calls) == 1

    assert (
        parse_calls[0]["html"]
        == "<html>test</html>"
    )

    assert (
        parse_calls[0]["keyword"]
        == "IC semiconductor"
    )


# ==================================================
#
# Test 4
#
# Parser → Article Metadata
#
# ==================================================


def test_pipeline_parser_to_article_metadata(
    monkeypatch,
):
    """
    Parser 完成後，
    ArticleService 必須正確回填 SearchResult Metadata。
    """

    repo = FakeRepository()

    search_result = SimpleNamespace(
        title="Search Title",
        url="https://example.com/article",
        source="Example Source",
        published="2026-08-18",
    )

    monkeypatch.setattr(
        "services.article_service.search",
        lambda keyword: [search_result],
    )

    monkeypatch.setattr(
        "services.article_service.download",
        lambda url, headers: "<html>test</html>",
    )

    monkeypatch.setattr(
        "services.article_service.parse",
        lambda html, keyword: SimpleNamespace(
            keyword="",
            title="Parser Title",
            url="",
            source="",
            published=None,
            content="Test article content.",
            status="",
        ),
    )

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    service = ArticleService(
        repo=repo,
        task_repo=FakeTaskRepository(),
        archive_service=FakeArchiveService(),
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=FakeBatchTrigger(),
    )

    result = service.create(
        "IC semiconductor"
    )

    article = result["articles"][0]

    assert article.keyword == "IC semiconductor"

    assert article.title == "Search Title"

    assert (
        article.url
        == "https://example.com/article"
    )

    assert article.source == "Example Source"

    assert article.published == "2026-08-18"

    assert article.status == "Success"


# ==================================================
#
# Test 5
#
# New Article → Archive
#
# ==================================================


def test_pipeline_creates_archive_version(
    monkeypatch,
):
    """
    新 Article 必須先建立 Archive Version。
    """

    archive_service = FakeArchiveService()

    search_result = SimpleNamespace(
        title="Test Article",
        url="https://example.com/article",
        source="Example",
        published=None,
    )

    monkeypatch.setattr(
        "services.article_service.search",
        lambda keyword: [search_result],
    )

    monkeypatch.setattr(
        "services.article_service.download",
        lambda url, headers: "<html>test</html>",
    )

    monkeypatch.setattr(
        "services.article_service.parse",
        lambda html, keyword: SimpleNamespace(
            keyword=keyword,
            title="Test Article",
            url="",
            source="",
            published=None,
            content="Test article content.",
            status="",
        ),
    )

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    task_repo = FakeTaskRepository()

    service = ArticleService(
        repo=FakeRepository(),
        task_repo=task_repo,
        archive_service=archive_service,
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=FakeBatchTrigger(),
    )

    result = service.create(
        "IC semiconductor"
    )

    assert result["new"] == 1

    assert len(
        archive_service.saved
    ) == 1

    assert (
        archive_service.saved[0]["url"]
        == "https://example.com/article"
    )


# ==================================================
#
# Test 6
#
# Archive → AI Task
#
# ==================================================


def test_pipeline_creates_ai_task_after_archive(
    monkeypatch,
):
    """
    Archive 成功後才建立 AI Task。
    """

    task_repo = FakeTaskRepository()

    search_result = SimpleNamespace(
        title="Test Article",
        url="https://example.com/article",
        source="Example",
        published=None,
    )

    monkeypatch.setattr(
        "services.article_service.search",
        lambda keyword: [search_result],
    )

    monkeypatch.setattr(
        "services.article_service.download",
        lambda url, headers: "<html>test</html>",
    )

    monkeypatch.setattr(
        "services.article_service.parse",
        lambda html, keyword: SimpleNamespace(
            keyword=keyword,
            title="Test Article",
            url="",
            source="",
            published=None,
            content="Test article content.",
            status="",
        ),
    )

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    service = ArticleService(
        repo=FakeRepository(),
        task_repo=task_repo,
        archive_service=FakeArchiveService(),
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=FakeBatchTrigger(),
    )

    result = service.create(
        "IC semiconductor"
    )

    assert result["new"] == 1

    assert len(
        task_repo.tasks
    ) == 1

    task = task_repo.tasks[0]

    assert task.article_id == 1

    assert task.task_type == "analysis"

    assert task.status == "WAITING"


# ==================================================
#
# Test 7
#
# Archive Failure → No AI Task
#
# ==================================================


def test_pipeline_archive_failure_does_not_create_ai_task(
    monkeypatch,
):
    """
    Archive 失敗時不得建立 AI Task。
    """

    task_repo = FakeTaskRepository()

    class FailedArchiveService:
        def save_html(
            self,
            article_id,
            url,
            html,
        ):
            return None

    search_result = SimpleNamespace(
        title="Test Article",
        url="https://example.com/article",
        source="Example",
        published=None,
    )

    monkeypatch.setattr(
        "services.article_service.search",
        lambda keyword: [search_result],
    )

    monkeypatch.setattr(
        "services.article_service.download",
        lambda url, headers: "<html>test</html>",
    )

    monkeypatch.setattr(
        "services.article_service.parse",
        lambda html, keyword: SimpleNamespace(
            keyword=keyword,
            title="Test Article",
            url="",
            source="",
            published=None,
            content="Test article content.",
            status="",
        ),
    )

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    service = ArticleService(
        repo=FakeRepository(),
        task_repo=task_repo,
        archive_service=FailedArchiveService(),
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=FakeBatchTrigger(),
    )

    result = service.create(
        "IC semiconductor"
    )

    assert result["new"] == 0

    assert result["failed"] == 1

    assert len(
        task_repo.tasks
    ) == 0


# ==================================================
#
# Test 8
#
# Batch Trigger
#
# ==================================================


def test_pipeline_triggers_ai_batch_after_task_creation(
    monkeypatch,
):
    """
    AI Task 建立後，
    ArticleService 必須通知 Batch Trigger。
    """

    batch_trigger = FakeBatchTrigger()

    search_result = SimpleNamespace(
        title="Test Article",
        url="https://example.com/article",
        source="Example",
        published=None,
    )

    monkeypatch.setattr(
        "services.article_service.search",
        lambda keyword: [search_result],
    )

    monkeypatch.setattr(
        "services.article_service.download",
        lambda url, headers: "<html>test</html>",
    )

    monkeypatch.setattr(
        "services.article_service.parse",
        lambda html, keyword: SimpleNamespace(
            keyword=keyword,
            title="Test Article",
            url="",
            source="",
            published=None,
            content="Test article content.",
            status="",
        ),
    )

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    service = ArticleService(
        repo=FakeRepository(),
        task_repo=FakeTaskRepository(),
        archive_service=FakeArchiveService(),
        archive_integration=FakeArchiveIntegration(),
        batch_trigger=batch_trigger,
    )

    service.create(
        "IC semiconductor"
    )

    assert batch_trigger.calls == 1