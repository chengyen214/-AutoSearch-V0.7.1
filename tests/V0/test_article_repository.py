"""
tests/test_article_repository.py

AutoSearch V4

P3.2

Article Repository Test

測試:

    save()
    insert()
    find_all()
    find_by_id()
    find_model_by_id()
    find_pending_ai()
    update_ai_status()
    get_ai_status()
    update_ai_analysis()
    find_failed_ai()

    find_by_importance()
    find_by_category()
    find_by_ai_keyword()
    find_by_keyword()
    find_by_source()

    exists()
    count()

測試方式:

    pytest
    unittest.mock

目的:

    驗證 ArticleRepository Database CRUD
    驗證 AI Retrieval
    驗證 Async AI Pipeline Repository Support

注意:

    本測試不連接真實 MySQL。
"""


from unittest.mock import MagicMock

import pytest

from database.article_repository import (
    ArticleRepository
)


# ============================================================
# Fake Article
# ============================================================

class FakeArticle:

    def __init__(
        self,
        article_id=None
    ):

        self.id = article_id

        self.document_id = "doc-test-001"

        self.keyword = "TSMC"

        self.title = "Test Article"

        self.url = "https://example.com/article"

        self.source = "CNA"

        self.published = None

        self.content = "Test article content"

        self.crawl_time = None

        self.status = "Success"

        self.ai_analysis = None

        self.ai_status = "pending"


# ============================================================
# Fake AI Analysis
# ============================================================

class FakeAIAnalysis:

    def __init__(self):

        self.summary = "Test summary"

        self.category = "Semiconductor"

        self.keywords = [
            "TSMC",
            "CoWoS"
        ]

        self.importance = 9

        self.ai_model = "TestModel"

        self.ai_version = "1.0"

        self.analyze_time = None

        self.confidence = 0.95


# ============================================================
# Repository Fixture
# ============================================================

@pytest.fixture
def repository():

    repo = object.__new__(
        ArticleRepository
    )

    repo.connection = MagicMock()

    return repo


# ============================================================
# Helper Cursor
# ============================================================

@pytest.fixture
def cursor(repository):

    cursor = MagicMock()

    repository.connection.cursor.return_value = (
        cursor
    )

    return cursor


# ============================================================
# SAVE
# ============================================================

def test_save(
    repository,
    cursor
):

    article = FakeArticle()

    # ==================================================
    # Duplicate Check
    #
    # ArticleRepository.save()
    #
    # save()
    #   ↓
    # exists()
    #   ↓
    # SELECT COUNT(*)
    #
    # 0 = Article 不存在，可以 INSERT
    # ==================================================

    cursor.fetchone.return_value = (
        0,
    )

    # ==================================================
    # INSERT lastrowid
    # ==================================================

    cursor.lastrowid = 123

    # ==================================================
    # Execute
    # ==================================================

    result = repository.save(
        article
    )

    # ==================================================
    # Result
    # ==================================================

    assert result is True

    # ==================================================
    # Article ID
    # ==================================================

    assert article.id == 123

    # ==================================================
    # Commit
    # ==================================================

    repository.connection.commit.assert_called_once()

    # ==================================================
    # Execute Count
    #
    # save() 會執行兩次 SQL：
    #
    # 1. exists()
    #    SELECT COUNT(*)
    #
    # 2. INSERT
    #    INSERT INTO articles
    #
    # ==================================================

    assert cursor.execute.call_count == 2

    # ==================================================
    # SQL Calls
    # ==================================================

    calls = cursor.execute.call_args_list

    # ==================================================
    # First SQL
    #
    # Duplicate Check
    # ==================================================

    first_sql = calls[0].args[0]

    assert "SELECT COUNT(*)" in first_sql

    assert "FROM articles" in first_sql

    assert "WHERE document_id=%s" in first_sql

    # ==================================================
    # Second SQL
    #
    # Article Insert
    # ==================================================

    second_sql = calls[1].args[0]

    assert "INSERT INTO articles" in second_sql

    assert "document_id" in second_sql

    assert "keyword" in second_sql

    assert "title" in second_sql

    assert "url" in second_sql

    assert "source" in second_sql

    assert "content" in second_sql

    # ==================================================
    # Cursor Close
    # ==================================================

    assert cursor.close.call_count == 2


# ============================================================
# SAVE DUPLICATE
# ============================================================

def test_save_duplicate(
    repository,
    cursor
):

    article = FakeArticle()

    cursor.fetchone.return_value = (
        1,
    )

    result = repository.save(
        article
    )

    assert result is False

    cursor.execute.assert_called_once()

    repository.connection.commit.assert_not_called()


# ============================================================
# INSERT
# ============================================================

def test_insert(
    repository
):

    article = FakeArticle()

    repository.save = MagicMock(
        return_value=True
    )

    result = repository.insert(
        article
    )

    assert result is article

    repository.save.assert_called_once_with(
        article
    )


# ============================================================
# INSERT DUPLICATE
# ============================================================

def test_insert_duplicate(
    repository
):

    article = FakeArticle()

    repository.save = MagicMock(
        return_value=False
    )

    result = repository.insert(
        article
    )

    assert result is None


# ============================================================
# FIND ALL
# ============================================================

def test_find_all(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "title": "Article 1"
        },
        {
            "id": 2,
            "title": "Article 2"
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_all(
        limit=10
    )

    assert result == expected

    cursor.execute.assert_called_once()

    cursor.close.assert_called_once()


# ============================================================
# FIND ALL WITHOUT LIMIT
# ============================================================

def test_find_all_without_limit(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "title": "Article 1"
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_all()

    assert result == expected

    cursor.execute.assert_called_once()


# ============================================================
# FIND BY ID
# ============================================================

def test_find_by_id(
    repository,
    cursor
):

    expected = {
        "id": 10,
        "title": "Test Article"
    }

    cursor.fetchone.return_value = expected

    result = repository.find_by_id(
        10
    )

    assert result == expected

    cursor.execute.assert_called_once_with(
        """

            SELECT *

            FROM articles

            WHERE id=%s

            """,
        (
            10,
        )
    )


# ============================================================
# FIND MODEL BY ID
# ============================================================

def test_find_model_by_id(
    repository
):

    repository.find_by_id = MagicMock(
        return_value={
            "id": 10,
            "document_id": "doc-10",
            "keyword": "TSMC",
            "title": "TSMC Article",
            "url": "https://example.com",
            "published": None,
            "source": "CNA",
            "content": "Content",
            "crawl_time": None,
            "status": "Success",
            "ai_status": "pending",
            "ai_summary": "",
            "ai_category": "",
            "ai_keywords": "[]",
            "ai_importance": 0,
            "ai_model": "",
            "ai_version": "",
            "ai_analyze_time": None,
            "ai_confidence": 0.0
        }
    )

    result = repository.find_model_by_id(
        10
    )

    assert result is not None

    assert result.id == 10

    assert result.document_id == "doc-10"

    assert result.keyword == "TSMC"

    assert result.ai_status == "pending"

    assert result.ai_analysis is None


# ============================================================
# FIND MODEL BY ID WITH AI
# ============================================================

def test_find_model_by_id_with_ai(
    repository
):

    repository.find_by_id = MagicMock(
        return_value={
            "id": 10,
            "document_id": "doc-10",
            "keyword": "TSMC",
            "title": "TSMC Article",
            "url": "https://example.com",
            "published": None,
            "source": "CNA",
            "content": "Content",
            "crawl_time": None,
            "status": "Success",
            "ai_status": "completed",
            "ai_summary": "Test summary",
            "ai_category": "Semiconductor",
            "ai_keywords": '["TSMC", "CoWoS"]',
            "ai_importance": 9,
            "ai_model": "TestModel",
            "ai_version": "1.0",
            "ai_analyze_time": None,
            "ai_confidence": 0.95
        }
    )

    result = repository.find_model_by_id(
        10
    )

    assert result is not None

    assert result.ai_analysis is not None

    assert (
        result.ai_analysis.summary
        == "Test summary"
    )

    assert (
        result.ai_analysis.category
        == "Semiconductor"
    )

    assert (
        result.ai_analysis.importance
        == 9
    )


# ============================================================
# FIND MODEL NOT FOUND
# ============================================================

def test_find_model_by_id_not_found(
    repository
):

    repository.find_by_id = MagicMock(
        return_value=None
    )

    result = repository.find_model_by_id(
        999
    )

    assert result is None


# ============================================================
# FIND PENDING AI
# ============================================================

def test_find_pending_ai(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "ai_status": "pending"
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_pending_ai(
        limit=20
    )

    assert result == expected

    cursor.execute.assert_called_once()

    cursor.close.assert_called_once()


# ============================================================
# UPDATE AI STATUS
# ============================================================

def test_update_ai_status(
    repository,
    cursor
):

    cursor.rowcount = 1

    result = repository.update_ai_status(
        10,
        "processing"
    )

    assert result is True

    repository.connection.commit.assert_called_once()

    cursor.execute.assert_called_once()


# ============================================================
# UPDATE AI STATUS NOT FOUND
# ============================================================

def test_update_ai_status_not_found(
    repository,
    cursor
):

    cursor.rowcount = 0

    result = repository.update_ai_status(
        999,
        "processing"
    )

    assert result is False


# ============================================================
# GET AI STATUS
# ============================================================

def test_get_ai_status(
    repository,
    cursor
):

    expected = {
        "id": 10,
        "ai_status": "completed"
    }

    cursor.fetchone.return_value = expected

    result = repository.get_ai_status(
        10
    )

    assert result == expected

    cursor.execute.assert_called_once()


# ============================================================
# UPDATE AI ANALYSIS
# ============================================================

def test_update_ai_analysis(
    repository,
    cursor
):

    article = FakeArticle(
        article_id=10
    )

    article.ai_analysis = (
        FakeAIAnalysis()
    )

    cursor.rowcount = 1

    result = repository.update_ai_analysis(
        article
    )

    assert result is True

    repository.connection.commit.assert_called_once()

    cursor.execute.assert_called_once()


# ============================================================
# UPDATE AI ANALYSIS WITHOUT ID
# ============================================================

def test_update_ai_analysis_without_id(
    repository
):

    article = FakeArticle()

    article.ai_analysis = (
        FakeAIAnalysis()
    )

    result = repository.update_ai_analysis(
        article
    )

    assert result is False


# ============================================================
# UPDATE AI ANALYSIS WITHOUT ANALYSIS
# ============================================================

def test_update_ai_analysis_without_analysis(
    repository
):

    article = FakeArticle(
        article_id=10
    )

    article.ai_analysis = None

    result = repository.update_ai_analysis(
        article
    )

    assert result is False


# ============================================================
# FIND FAILED AI
# ============================================================

def test_find_failed_ai(
    repository,
    cursor
):

    expected = [
        {
            "id": 10,
            "ai_status": "failed"
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_failed_ai(
        limit=20
    )

    assert result == expected

    cursor.execute.assert_called_once()


# ============================================================
# FIND BY IMPORTANCE
# ============================================================

def test_find_by_importance(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "ai_importance": 10
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_by_importance(
        8
    )

    assert result == expected

    cursor.execute.assert_called_once()


# ============================================================
# FIND BY CATEGORY
# ============================================================

def test_find_by_category(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "ai_category": "Semiconductor"
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_by_category(
        "Semiconductor"
    )

    assert result == expected

    cursor.execute.assert_called_once()


# ============================================================
# FIND BY AI KEYWORD
# ============================================================

def test_find_by_ai_keyword(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "ai_keywords": '["CoWoS"]'
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_by_ai_keyword(
        "CoWoS"
    )

    assert result == expected

    cursor.execute.assert_called_once()


# ============================================================
# FIND BY NORMAL KEYWORD
# ============================================================

def test_find_by_keyword(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "keyword": "TSMC"
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_by_keyword(
        "TSMC"
    )

    assert result == expected

    cursor.execute.assert_called_once()


# ============================================================
# FIND BY SOURCE
#
# P3.2 Article Management API
#
# ============================================================

def test_find_by_source(
    repository,
    cursor
):

    expected = [
        {
            "id": 1,
            "source": "CNA"
        }
    ]

    cursor.fetchall.return_value = expected

    result = repository.find_by_source(
        "CNA"
    )

    assert result == expected

    cursor.execute.assert_called_once()

    cursor.close.assert_called_once()


# ============================================================
# EXISTS
# ============================================================

def test_exists(
    repository,
    cursor
):

    cursor.fetchone.return_value = (
        1,
    )

    result = repository.exists(
        "doc-test-001"
    )

    assert result is True

    cursor.execute.assert_called_once()


# ============================================================
# EXISTS FALSE
# ============================================================

def test_exists_false(
    repository,
    cursor
):

    cursor.fetchone.return_value = (
        0,
    )

    result = repository.exists(
        "doc-not-found"
    )

    assert result is False


# ============================================================
# COUNT
# ============================================================

def test_count(
    repository,
    cursor
):

    cursor.fetchone.return_value = (
        25,
    )

    result = repository.count()

    assert result == 25

    cursor.execute.assert_called_once()


# ============================================================
# CLOSE
# ============================================================

def test_close(
    repository
):

    repository.close()

    repository.connection.close.assert_called_once()