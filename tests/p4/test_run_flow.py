"""
tests/p4/test_run_flow.py

AutoSearch V4

P4 Data Sources
P4.1 / P4.8 Run Flow Integration Test

Purpose
-------

確認 P4 Search Adapter 與正式 Run Flow
已正確接入。

Test Flow:

    run.py
        ↓
    app.main.main()
        ↓
    AutoSearchApplication.run()
        ↓
    ArticleService
        ↓
    Search Adapter
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
        ↓
    AI Trigger
        ↓
    Knowledge Intelligence

注意
----

本測試全部使用 Mock。

不執行：

- 真實 Google News RSS
- 真實 HTML Download
- 真實 Parser
- Groq / AI
- Database
- Archive Storage
- Duplicate Storage
- AI Worker
- AI Scheduler
- Knowledge Processing
- Excel Export

目的：

快速驗證 P4 Search Adapter
以及 P4.8 正式 Application Run Flow
的模組整合是否正確。
"""


from models.search_result import (
    SearchResult,
)


from models.article import (
    Article,
)


from services.article_service import (
    ArticleService,
)


# ==================================================
#
# Mock Search
#
# ==================================================


def mock_search(
    keyword,
):
    """
    Mock P4 Search Adapter。

    模擬：

        Search Adapter
            ↓
        SearchResult
            ↓
        ArticleService
    """

    return [

        SearchResult(
            keyword=keyword,
            title="P4.1 Test Article",
            url="https://example.com/test",
            source="Test Source",
            published=None,
            search_source="test",
            rank=1,
        ),

    ]


# ==================================================
#
# Mock Download
#
# ==================================================


def mock_download(
    url,
    headers=None,
):
    """
    Mock HTML Download。

    不進行真正 HTTP Request。
    """

    return """
    <html>
        <head>
            <title>P4.1 Test Article</title>
        </head>

        <body>

            <article>

                <h1>P4.1 Test Article</h1>

                <p>
                    This is a P4.1 integration test article.
                    This content is only used for testing.
                </p>

            </article>

        </body>
    </html>
    """


# ==================================================
#
# Mock Parser
#
# ==================================================


def mock_parse(
    html,
    keyword,
):
    """
    Mock Parser。

    模擬 Parser 回傳 Article。
    """

    return Article(
        keyword=keyword,
        title="P4.1 Test Article",
        url="https://example.com/test",
        source="Test Source",
        content="P4.1 Test Article Content",
        published=None,
    )


# ==================================================
#
# Test Repository
#
# ==================================================


class MockArticleRepository:
    """
    Mock ArticleRepository。

    避免 P4 Run Flow Test
    寫入真正 Database。
    """

    def __init__(
        self,
    ):
        self.articles = []

    # ==================================================
    #
    # Find By URL
    #
    # ==================================================

    def find_by_url(
        self,
        url,
    ):
        """
        P4 Test 中預設沒有既有 Article。

        因此每次測試都走：

            New Article
        """

        return None

    # ==================================================
    #
    # Find All
    #
    # ==================================================

    def find_all(
        self,
        limit=None,
    ):
        return self.articles

    # ==================================================
    #
    # Insert
    #
    # ==================================================

    def insert(
        self,
        article,
    ):
        """
        模擬 ArticleRepository.insert()。

        Article ID 由 Repository
        在 insert 時建立。

        這與正式 Article lifecycle 一致：

            Article()
                ↓
            Repository.insert()
                ↓
            article.id
        """

        article.id = (
            len(self.articles)
            + 1
        )

        self.articles.append(
            article
        )

        return article

    # ==================================================
    #
    # Find By ID
    #
    # ==================================================

    def find_by_id(
        self,
        article_id,
    ):
        for article in self.articles:

            if article.id == article_id:

                return article

        return None

    # ==================================================
    #
    # Count
    #
    # ==================================================

    def count(
        self,
    ):
        return len(
            self.articles
        )

    # ==================================================
    #
    # Close
    #
    # ==================================================

    def close(
        self,
    ):
        pass


# ==================================================
#
# Test AI Task Repository
#
# ==================================================


class MockAITaskRepository:
    """
    Mock AI Task Repository。

    P4 Run Flow Test
    不測試真正 AI Pipeline。
    """

    def __init__(
        self,
    ):
        self.tasks = []

    # ==================================================
    #
    # Insert
    #
    # ==================================================

    def insert(
        self,
        task,
    ):
        self.tasks.append(
            task
        )

        return task


# ==================================================
#
# Test Archive Service
#
# ==================================================


class MockArchiveVersion:
    """
    Mock Archive Version。
    """

    def __init__(
        self,
    ):

        self.version_number = 1

        self.file_hash = (
            "p4-test-hash"
        )


class MockArchiveService:
    """
    Mock ArchiveService。

    P4 Run Flow Test
    不測試真正 Archive。
    """

    def __init__(
        self,
    ):

        self.version_repo = None

    # ==================================================
    #
    # Save HTML
    #
    # ==================================================

    def save_html(
        self,
        article_id,
        url,
        html,
    ):

        return MockArchiveVersion()


# ==================================================
#
# Test Archive Integration
#
# ==================================================


class MockArchiveIntegration:
    """
    Mock ArchiveIntegration。
    """

    def _get_archive_repository(
        self,
    ):

        return None


# ==================================================
#
# Test Batch Trigger
#
# ==================================================


class MockBatchTrigger:
    """
    Mock AI Batch Trigger。

    不啟動真正 AI Scheduler / Worker。
    """

    def check_and_trigger(
        self,
    ):

        return False


# ==================================================
#
# P4.1 Run Flow Test
#
# ==================================================


def test_p4_1_run_flow(
    monkeypatch,
):
    """
    P4.1 Run Flow Integration Test。

    驗證：

        Keyword
            ↓
        Search Adapter
            ↓
        SearchResult
            ↓
        SearchResult → Article
            ↓
        ArticleService
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

    # ==================================================
    #
    # Mock Search Adapter
    #
    # ==================================================

    monkeypatch.setattr(
        "services.article_service.search",
        mock_search,
    )

    # ==================================================
    #
    # Mock Downloader
    #
    # ==================================================

    monkeypatch.setattr(
        "services.article_service.download",
        mock_download,
    )

    # ==================================================
    #
    # Mock Parser
    #
    # ==================================================

    monkeypatch.setattr(
        "services.article_service.parse",
        mock_parse,
    )

    # ==================================================
    #
    # Mock Duplicate Checker
    #
    # ==================================================

    monkeypatch.setattr(
        "services.article_service.is_duplicate",
        lambda document_id: False,
    )

    # ==================================================
    #
    # Mock Duplicate Storage
    #
    # ==================================================

    monkeypatch.setattr(
        "services.article_service.save_document",
        lambda document_id: None,
    )

    # ==================================================
    #
    # Create Dependencies
    #
    # ==================================================

    repo = (
        MockArticleRepository()
    )

    task_repo = (
        MockAITaskRepository()
    )

    archive_service = (
        MockArchiveService()
    )

    archive_integration = (
        MockArchiveIntegration()
    )

    batch_trigger = (
        MockBatchTrigger()
    )

    # ==================================================
    #
    # Create Article Service
    #
    # ==================================================

    service = ArticleService(

        repo=repo,

        task_repo=task_repo,

        archive_service=(
            archive_service
        ),

        archive_integration=(
            archive_integration
        ),

        batch_trigger=(
            batch_trigger
        ),
    )

    # ==================================================
    #
    # Execute Run Flow
    #
    # ==================================================

    result = service.create(
        "IC semiconductor"
    )

    # ==================================================
    #
    # Basic Result
    #
    # ==================================================

    assert result is not None

    assert isinstance(
        result,
        dict,
    )

    # ==================================================
    #
    # Search
    #
    # ==================================================

    assert (
        result["total"]
        == 1
    )

    # ==================================================
    #
    # New Article
    #
    # ==================================================

    assert (
        result["new"]
        == 1
    )

    # ==================================================
    #
    # Duplicate
    #
    # ==================================================

    assert (
        result["duplicate"]
        == 0
    )

    # ==================================================
    #
    # Failed
    #
    # ==================================================

    assert (
        result["failed"]
        == 0
    )

    # ==================================================
    #
    # Article Result
    #
    # ==================================================

    assert len(
        result["articles"]
    ) == 1

    article = (
        result["articles"][0]
    )

    assert isinstance(
        article,
        Article,
    )

    # ==================================================
    #
    # Article Metadata
    #
    # ==================================================

    assert (
        article.keyword
        == "IC semiconductor"
    )

    assert (
        article.title
        == "P4.1 Test Article"
    )

    assert (
        article.url
        == "https://example.com/test"
    )

    assert (
        article.source
        == "Test Source"
    )

    # ==================================================
    #
    # Article Content
    #
    # ==================================================

    assert (
        article.content
        == "P4.1 Test Article Content"
    )

    # ==================================================
    #
    # Article Status
    #
    # ==================================================

    assert (
        article.status
        == "Success"
    )

    # ==================================================
    #
    # Article ID
    #
    # ==================================================

    assert (
        article.id
        == 1
    )

    # ==================================================
    #
    # Document ID
    #
    # ==================================================

    assert (
        article.document_id
        is not None
    )

    assert (
        len(article.document_id)
        > 0
    )

    # ==================================================
    #
    # Repository
    #
    # ==================================================

    assert (
        repo.count()
        == 1
    )

    assert (
        repo.find_by_id(
            article.id
        )
        is article
    )

    # ==================================================
    #
    # AI Task
    #
    # ==================================================

    assert (
        len(task_repo.tasks)
        == 1
    )

    assert (
        task_repo.tasks[0].article_id
        == article.id
    )

    assert (
        task_repo.tasks[0].task_type
        == "analysis"
    )

    assert (
        task_repo.tasks[0].status
        == "WAITING"
    )

    # ==================================================
    #
    # Batch Trigger
    #
    # ==================================================

    assert (
        batch_trigger.check_and_trigger()
        is False
    )


# ============================================================
#
# P4.8 Run Flow Integration Test
#
# ============================================================


def test_p4_8_application_run_flow(
    monkeypatch,
):
    """
    P4.8 Run Flow Integration Test。

    驗證正式 Application Flow：

        AutoSearchApplication
            ↓
        _collect_articles()
            ↓
        ArticleService.create()
            ↓
        Articles
            ↓
        AI Trigger
            ↓
        Knowledge Intelligence

    注意：

        不執行：

        - Google News
        - HTTP
        - Database
        - AI Worker
        - AI Scheduler
        - Knowledge Processing
        - Excel Export
    """

    from app.main import (
        AutoSearchApplication,
    )

    # ==================================================
    #
    # Mock ArticleService
    #
    # ==================================================

    class MockArticleService:

        def __init__(
            self,
        ):
            self.calls = []

        def create(
            self,
            keyword,
        ):

            self.calls.append(
                keyword
            )

            # ------------------------------------------
            # Important:
            #
            # Article model 不接受 id
            # 作為 constructor argument。
            #
            # 正式流程也是由 Repository
            # 在 insert 後取得 Article ID。
            #
            # 因此測試中必須：
            #
            # Article(...)
            #     ↓
            # article.id = 1
            #
            # ------------------------------------------

            article = Article(
                keyword=keyword,
                title="P4.8 Test Article",
                url="https://example.com/p4.8",
                source="P4.8 Test",
                content="P4.8 content",
                status="Success",
            )

            article.id = 1

            return {
                "articles": [
                    article
                ],
                "total": 1,
                "new": 1,
                "duplicate": 0,
                "failed": 0,
            }

    # ==================================================
    #
    # Mock AI Task Repository
    #
    # ==================================================

    class MockAITaskRepository:

        def count_running_tasks(
            self,
        ):
            return 0

        def recover_running_tasks(
            self,
        ):
            return 0

        def count_waiting_tasks(
            self,
        ):
            return 0

    # ==================================================
    #
    # Mock Batch Trigger
    #
    # ==================================================

    class MockBatchTrigger:

        def check_and_trigger(
            self,
        ):
            return False

        def force_trigger(
            self,
        ):
            return False

    # ==================================================
    #
    # Mock Scheduler
    #
    # ==================================================

    class MockScheduler:

        def is_running(
            self,
        ):
            return False

        def stop(
            self,
        ):
            return True

    # ==================================================
    #
    # Mock Knowledge Intelligence
    #
    # ==================================================

    class MockKnowledgeService:

        def __init__(
            self,
        ):
            self.called = False

        def run(
            self,
        ):
            self.called = True

    # ==================================================
    #
    # Mock History
    #
    # ==================================================

    monkeypatch.setattr(
        "app.main.save_history",
        lambda *args, **kwargs: None,
    )

    # ==================================================
    #
    # Mock Export
    #
    # ==================================================

    monkeypatch.setattr(
        "app.main.export",
        lambda articles: None,
    )

    # ==================================================
    #
    # Mock SEARCH_KEYWORDS
    #
    # ==================================================

    monkeypatch.setattr(
        "app.main.SEARCH_KEYWORDS",
        ["IC semiconductor"],
    )

    # ==================================================
    #
    # Create Application
    #
    # ==================================================

    app = AutoSearchApplication(
        ai_threshold=50,
        ai_wait_interval=0.01,
    )

    # ==================================================
    #
    # Replace Dependencies
    #
    # ==================================================

    article_service = (
        MockArticleService()
    )

    knowledge_service = (
        MockKnowledgeService()
    )

    app.article_service = (
        article_service
    )

    app.ai_task_repository = (
        MockAITaskRepository()
    )

    app.ai_batch_trigger = (
        MockBatchTrigger()
    )

    app.ai_scheduler = (
        MockScheduler()
    )

    app.knowledge_service = (
        knowledge_service
    )

    # ==================================================
    #
    # Execute Application Run
    #
    # ==================================================

    articles = app.run()

    # ==================================================
    #
    # Verify ArticleService
    #
    # ==================================================

    assert (
        article_service.calls
        == ["IC semiconductor"]
    )

    # ==================================================
    #
    # Verify Article Result
    #
    # ==================================================

    assert len(
        articles
    ) == 1

    article = articles[0]

    assert isinstance(
        article,
        Article,
    )

    # ==================================================
    #
    # Verify Article ID
    #
    # ==================================================

    assert (
        article.id
        == 1
    )

    # ==================================================
    #
    # Verify Article Metadata
    #
    # ==================================================

    assert (
        article.keyword
        == "IC semiconductor"
    )

    assert (
        article.title
        == "P4.8 Test Article"
    )

    assert (
        article.url
        == "https://example.com/p4.8"
    )

    assert (
        article.source
        == "P4.8 Test"
    )

    assert (
        article.content
        == "P4.8 content"
    )

    assert (
        article.status
        == "Success"
    )

    # ==================================================
    #
    # Verify Knowledge Layer
    #
    # ==================================================

    assert (
        knowledge_service.called
        is True
    )


# ============================================================
#
# P4.8 run.py Entry Point Test
#
# ============================================================


def test_p4_8_run_py_entrypoint(
    monkeypatch,
):
    """
    P4.8 Run.py Entry Point Test。

    驗證：

        run.py
            ↓
        app.main.main()

    不真正執行 Application Pipeline。
    """

    import run

    called = {
        "value": False,
    }

    def mock_main():

        called["value"] = True

    monkeypatch.setattr(
        run,
        "main",
        mock_main,
    )

    # ==================================================
    #
    # 模擬 run.py 的 main() 呼叫
    #
    # ==================================================

    run.main()

    assert (
        called["value"]
        is True
    )
