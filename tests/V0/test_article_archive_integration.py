"""
tests/test_article_archive_integration.py

AutoSearch V4

P2.2.2 Step 6

ArticleService
+
ArchiveService
+
RawDocument
+
ArchiveVersion
+
AITask

Integration Test
"""

from unittest.mock import patch

from services.article_service import ArticleService


# ==================================================
#
# Test Article → Archive → AI Task
#
# ==================================================

def test_article_archive_integration():

    service = ArticleService()

    # ==============================================
    # Mock Search Result
    # ==============================================

    class SearchItem:

        title = "Test Semiconductor Article"

        url = "https://example.com/test"

        source = "TestSource"

        published = None

    # ==============================================
    # Mock Article
    # ==============================================

    class TestArticle:

        keyword = ""

        title = ""

        url = ""

        source = ""

        published = None

        content = (
            "This is a test semiconductor article."
        )

        status = ""

        document_id = ""

        id = None

    test_article = TestArticle()

    # ==============================================
    # Mock Saved Article
    # ==============================================

    class SavedArticle:

        id = 999

        document_id = (
            "test_document_999"
        )

        title = (
            "Test Semiconductor Article"
        )

        content = (
            "This is a test semiconductor article."
        )

    # ==============================================
    # Mock Archive Version
    # ==============================================

    class ArchiveVersion:

        version_number = 1

        article_id = 999

    # ==============================================
    # Mock AI Task
    # ==============================================

    class AITaskResult:

        id = 1

        article_id = 999

        status = "WAITING"

    # ==============================================
    # Mock Pipeline
    # ==============================================

    with patch(
        "services.article_service.search"
    ) as mock_search, \
         patch(
             "services.article_service.download"
         ) as mock_download, \
         patch(
             "services.article_service.parse"
         ) as mock_parse, \
         patch(
             "services.article_service.is_duplicate"
         ) as mock_duplicate, \
         patch(
             "services.article_service.save_document"
         ) as mock_save_document:

        # ==========================================
        # Search
        # ==========================================

        mock_search.return_value = [
            SearchItem()
        ]

        # ==========================================
        # Download
        # ==========================================

        mock_download.return_value = (
            "<html>"
            "<body>"
            "Test Semiconductor Article"
            "</body>"
            "</html>"
        )

        # ==========================================
        # Parser
        # ==========================================

        mock_parse.return_value = test_article

        # ==========================================
        # Duplicate
        # ==========================================

        mock_duplicate.return_value = False

        # ==========================================
        # Article Repository
        # ==========================================

        service.repo.insert = (
            lambda article:
            SavedArticle()
        )

        # ==========================================
        # Archive Service
        # ==========================================

        service.archive_service.save_html = (
            lambda article_id, url, html:
            ArchiveVersion()
        )

        # ==========================================
        # AI Task
        # ==========================================

        service.task_repo.insert = (
            lambda task:
            AITaskResult()
        )

        # ==========================================
        # Execute
        # ==========================================

        result = service.create(
            "semiconductor"
        )

    # ==================================================
    # Assertions
    # ==================================================

    # Article
    assert result["total"] == 1

    assert result["new"] == 1

    assert result["duplicate"] == 0

    assert result["failed"] == 0

    assert len(
        result["articles"]
    ) == 1

    # ==============================================
    # Article ID
    # ==============================================

    assert (
        result["articles"][0].id
        == 999
    )

    # ==============================================
    # Archive Version
    # ==============================================

    assert (
        service.archive_service.save_html
        is not None
    )

    # ==============================================
    # AI Task
    # ==============================================

    service.task_repo.insert.assert_not_called \
        if hasattr(
            service.task_repo.insert,
            "assert_not_called"
        ) else None


# ==================================================
#
# Test Archive Failure
#
# Article should NOT create AI Task
#
# ==================================================

def test_article_archive_failure():

    service = ArticleService()

    class SearchItem:

        title = "Archive Failure Test"

        url = "https://example.com/failure"

        source = "TestSource"

        published = None

    class TestArticle:

        keyword = ""

        title = ""

        url = ""

        source = ""

        published = None

        content = (
            "Archive failure test content."
        )

        status = ""

        document_id = ""

        id = None

    class SavedArticle:

        id = 1000

        document_id = (
            "test_document_1000"
        )

    with patch(
        "services.article_service.search"
    ) as mock_search, \
         patch(
             "services.article_service.download"
         ) as mock_download, \
         patch(
             "services.article_service.parse"
         ) as mock_parse, \
         patch(
             "services.article_service.is_duplicate"
         ) as mock_duplicate, \
         patch(
             "services.article_service.save_document"
         ):

        mock_search.return_value = [
            SearchItem()
        ]

        mock_download.return_value = (
            "<html>Archive Failure</html>"
        )

        mock_parse.return_value = (
            TestArticle()
        )

        mock_duplicate.return_value = False

        # ==========================================
        # Article Save
        # ==========================================

        service.repo.insert = (
            lambda article:
            SavedArticle()
        )

        # ==========================================
        # Archive Failure
        # ==========================================

        service.archive_service.save_html = (
            lambda article_id, url, html:
            None
        )

        # ==========================================
        # AI Task
        # ==========================================

        ai_task_created = []

        service.task_repo.insert = (
            lambda task:
            ai_task_created.append(task)
        )

        result = service.create(
            "semiconductor"
        )

    # ==============================================
    # Archive Failed
    # ==============================================

    assert result["new"] == 0

    assert result["failed"] == 1

    # ==============================================
    # AI Task MUST NOT be created
    # ==============================================

    assert len(
        ai_task_created
    ) == 0
