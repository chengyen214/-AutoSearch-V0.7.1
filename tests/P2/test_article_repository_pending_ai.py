"""
tests/P2/test_article_repository_pending_ai.py

AutoSearch V4

P2.4.1

Test:
    Article Storage 與 AI Analysis 解耦

驗證:

1. Article 沒有 AI Analysis 時仍可保存
2. Article 原始資料先寫入 articles
3. 未分析 AI fields 使用 NULL
4. ai_status = pending
5. find_pending_ai() 可以找到未分析 Article
6. find_model_by_id() 可以正確讀回未分析 Article
7. AI Analysis 尚未完成時，原始 Article 不受影響

注意:

    本測試使用實際 Database。
    不使用 Mock Repository。

執行:

    python -m pytest tests/P2/test_article_repository_pending_ai.py -v
"""

import uuid

import pytest

from database.article_repository import (
    ArticleRepository,
)

from models.article import (
    Article,
)


# ============================================================
# Helpers
# ============================================================


def create_test_article():
    """
    建立一筆沒有 AI Analysis 的測試 Article。

    注意:

        不設定 article.ai_analysis。

    這正是 P2.4.1
    SQL First 的測試情境。
    """

    unique_id = uuid.uuid4().hex

    article = Article(
        keyword="P2_TEST",
        title=f"P2 Pending AI Test {unique_id}",
        url=f"https://example.com/p2-test/{unique_id}",
        source="P2_TEST",
        content=(
            "This is a test article for "
            "P2.4.1 SQL First pending AI."
        ),
        status="Success",
    )

    article.document_id = (
        f"test-{unique_id}"
    )

    return article


# ============================================================
# Fixture
# ============================================================


@pytest.fixture
def repository():
    """
    建立 ArticleRepository。

    測試完成後關閉 connection。
    """

    repo = ArticleRepository()

    yield repo

    repo.close()


# ============================================================
# P2.4.1
# Test 1
# ============================================================


def test_article_without_ai_can_be_saved(
    repository,
):
    """
    P2.4.1

    Article 沒有 AI Analysis 時，
    仍然可以先保存到 SQL。
    """

    article = create_test_article()

    # --------------------------------------------------------
    # 確認測試前沒有 AI Analysis
    # --------------------------------------------------------

    assert getattr(
        article,
        "ai_analysis",
        None,
    ) is None

    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    result = repository.insert(
        article
    )

    # --------------------------------------------------------
    # Article 必須成功保存
    # --------------------------------------------------------

    assert result is article

    assert article.id is not None

    # --------------------------------------------------------
    # Database 必須真的存在
    # --------------------------------------------------------

    row = repository.find_by_id(
        article.id
    )

    assert row is not None

    assert row["id"] == article.id

    assert (
        row["document_id"]
        == article.document_id
    )

    assert (
        row["title"]
        == article.title
    )


# ============================================================
# P2.4.1
# Test 2
# ============================================================


def test_unsolved_ai_fields_are_null(
    repository,
):
    """
    P2.4.1

    Article 尚未 AI Analysis 時:

        ai_summary      = NULL
        ai_category     = NULL
        ai_keywords     = NULL
        ai_importance   = NULL
        ai_model        = NULL
        ai_version      = NULL
        ai_analyze_time = NULL
        ai_confidence   = NULL

        ai_status       = pending
    """

    article = create_test_article()

    result = repository.insert(
        article
    )

    assert result is article

    row = repository.find_by_id(
        article.id
    )

    assert row is not None

    # --------------------------------------------------------
    # AI fields
    # --------------------------------------------------------

    assert row["ai_summary"] is None

    assert row["ai_category"] is None

    assert row["ai_keywords"] is None

    assert row["ai_importance"] is None

    assert row["ai_model"] is None

    assert row["ai_version"] is None

    assert row["ai_analyze_time"] is None

    assert row["ai_confidence"] is None

    # --------------------------------------------------------
    # AI Status
    # --------------------------------------------------------

    assert (
        row["ai_status"]
        == "pending"
    )


# ============================================================
# P2.4.1
# Test 3
# ============================================================


def test_pending_ai_article_can_be_found(
    repository,
):
    """
    P2.4.1

    未完成 AI Analysis 的 Article
    必須可以透過 find_pending_ai() 找到。
    """

    article = create_test_article()

    result = repository.insert(
        article
    )

    assert result is article

    pending_articles = (
        repository.find_pending_ai(
            limit=100
        )
    )

    pending_ids = {
        row["id"]
        for row in pending_articles
    }

    assert article.id in pending_ids


# ============================================================
# P2.4.1
# Test 4
# ============================================================


def test_find_model_by_id_restores_pending_article(
    repository,
):
    """
    P2.4.1

    Database:

        articles
            ↓
        find_model_by_id()
            ↓
        Article Model

    尚未 AI Analysis 時:

        article.ai_analysis = None
    """

    article = create_test_article()

    result = repository.insert(
        article
    )

    assert result is article

    restored = repository.find_model_by_id(
        article.id
    )

    assert restored is not None

    assert restored.id == article.id

    assert (
        restored.document_id
        == article.document_id
    )

    assert (
        restored.title
        == article.title
    )

    assert (
        restored.content
        == article.content
    )

    assert (
        restored.ai_status
        == "pending"
    )

    assert (
        restored.ai_analysis
        is None
    )


# ============================================================
# P2.4.1
# Test 5
# ============================================================


def test_original_article_data_exists_before_ai_analysis(
    repository,
):
    """
    P2.4.1

    核心測試:

        Article
            ↓
        SQL
            ↓
        AI 尚未完成

    即使 AI Analysis 尚未存在，
    Article 原始資料仍然必須存在。
    """

    article = create_test_article()

    result = repository.insert(
        article
    )

    assert result is article

    # --------------------------------------------------------
    # 直接從 Database 讀取
    # --------------------------------------------------------

    row = repository.find_by_id(
        article.id
    )

    assert row is not None

    # --------------------------------------------------------
    # Original Article Data
    # --------------------------------------------------------

    assert (
        row["document_id"]
        == article.document_id
    )

    assert (
        row["keyword"]
        == article.keyword
    )

    assert (
        row["title"]
        == article.title
    )

    assert (
        row["url"]
        == article.url
    )

    assert (
        row["source"]
        == article.source
    )

    assert (
        row["content"]
        == article.content
    )

    assert (
        row["status"]
        == "Success"
    )

    # --------------------------------------------------------
    # AI 尚未完成
    # --------------------------------------------------------

    assert (
        row["ai_status"]
        == "pending"
    )

    assert (
        row["ai_summary"]
        is None
    )


# ============================================================
# P2.4.1
# Test 6
# ============================================================


def test_ai_analysis_is_not_required_for_insert(
    repository,
):
    """
    P2.4.1

    明確驗證:

        insert(article)

    不需要:

        article.ai_analysis
    """

    article = create_test_article()

    # --------------------------------------------------------
    # 明確移除任何可能存在的 AI Analysis
    # --------------------------------------------------------

    if hasattr(
        article,
        "ai_analysis",
    ):
        article.ai_analysis = None

    # --------------------------------------------------------
    # Repository 必須仍然可以 INSERT
    # --------------------------------------------------------

    result = repository.insert(
        article
    )

    assert result is article

    assert article.id is not None

    row = repository.find_by_id(
        article.id
    )

    assert row is not None

    assert (
        row["ai_status"]
        == "pending"
    )

    assert (
        row["ai_summary"]
        is None
    )


# ============================================================
# P2.4.1
# Test 7
# ============================================================


def test_duplicate_document_is_not_inserted_twice(
    repository,
):
    """
    P2.4.1

    驗證 SQL First 的同時，
    document_id duplicate protection
    仍然有效。

    第一筆:

        INSERT -> 成功

    第二筆:

        相同 document_id
        -> 不重複 INSERT
    """

    article1 = create_test_article()

    result1 = repository.insert(
        article1
    )

    assert result1 is article1

    assert article1.id is not None

    # --------------------------------------------------------
    # 建立第二個 Article
    # --------------------------------------------------------

    article2 = create_test_article()

    # 使用相同 document_id
    article2.document_id = (
        article1.document_id
    )

    result2 = repository.insert(
        article2
    )

    # --------------------------------------------------------
    # Duplicate 必須被拒絕
    # --------------------------------------------------------

    assert result2 is None

    # --------------------------------------------------------
    # 第一筆仍然存在
    # --------------------------------------------------------

    row = repository.find_by_id(
        article1.id
    )

    assert row is not None

    assert (
        row["document_id"]
        == article1.document_id
    )

    assert (
        row["ai_status"]
        == "pending"
    )


# ============================================================
# P2.4.1
# Test 8
# ============================================================


def test_pending_ai_does_not_require_ai_fields_for_query(
    repository,
):
    """
    P2.4.1

    未分析 Article 可以正常存在，
    即使所有 AI fields 都是 NULL。

    AI Query 不應該把 SQL First Article
    視為不存在。
    """

    article = create_test_article()

    result = repository.insert(
        article
    )

    assert result is article

    # --------------------------------------------------------
    # Pending AI
    # --------------------------------------------------------

    pending = repository.find_pending_ai(
        limit=100
    )

    pending_ids = {
        row["id"]
        for row in pending
    }

    assert article.id in pending_ids

    # --------------------------------------------------------
    # Article 本身仍然可以查詢
    # --------------------------------------------------------

    by_id = repository.find_by_id(
        article.id
    )

    assert by_id is not None

    assert (
        by_id["title"]
        == article.title
    )

    assert (
        by_id["content"]
        == article.content
    )
