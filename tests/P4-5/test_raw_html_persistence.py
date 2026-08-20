"""
tests/P4-5/test_raw_html_persistence.py

AutoSearch V4

Raw HTML Persistence Test

用途：

    驗證 RawHTMLRepository 可以正常：

        1. 儲存 Raw HTML
        2. 依 Article ID 讀取
        3. 依 Document ID 讀取
        4. 依 URL 讀取
        5. 驗證 HTML 完整性
        6. 驗證 exists()
        7. 更新 HTML
        8. 刪除測試資料

架構：

    Test Data
        |
        v
    RawHTMLRepository
        |
        v
    MongoDB
        |
        v
    autosearch.raw_html

注意：

    本測試使用測試專用 document_id。

    測試結束後會刪除測試資料。

    不修改：

        MySQL articles
        Crawler
        archive/html
        AI Pipeline
"""


import uuid


from database.raw_html_repository import (
    RawHTMLRepository
)


# ==================================================
# Test Raw HTML Persistence
# ==================================================


def test_raw_html_persistence():
    """
    測試 Raw HTML MongoDB Persistence。
    """

    repository = (
        RawHTMLRepository()
    )

    # ==================================================
    # Test Data
    # ==================================================

    article_id = 999999

    document_id = (
        "TEST_MONGO_RAW_HTML_"
        + uuid.uuid4().hex
    )

    url = (
        "https://example.com/"
        "autosearch-mongodb-test"
    )

    original_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AutoSearch V4 MongoDB Test</title>
</head>
<body>
    <h1>AutoSearch V4</h1>
    <p>MongoDB Raw HTML Persistence Test</p>
</body>
</html>
"""

    updated_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AutoSearch V4 MongoDB Updated Test</title>
</head>
<body>
    <h1>AutoSearch V4</h1>
    <p>MongoDB Raw HTML Update Test</p>
</body>
</html>
"""

    try:

        # ==================================================
        # 1. Before Save
        # ==================================================

        assert (
            repository.exists(
                document_id
            )
            is False
        )

        # ==================================================
        # 2. Save Raw HTML
        # ==================================================

        mongo_id = (
            repository.save(
                article_id=article_id,
                document_id=document_id,
                url=url,
                html=original_html
            )
        )

        assert mongo_id is not None

        # ==================================================
        # 3. Exists
        # ==================================================

        assert (
            repository.exists(
                document_id
            )
            is True
        )

        # ==================================================
        # 4. Find By Document ID
        # ==================================================

        result = (
            repository.find_by_document_id(
                document_id
            )
        )

        assert result is not None

        assert (
            result["document_id"]
            == document_id
        )

        assert (
            result["article_id"]
            == article_id
        )

        assert (
            result["url"]
            == url
        )

        assert (
            result["html"]
            == original_html
        )

        # ==================================================
        # 5. Find By Article ID
        # ==================================================

        result_by_article = (
            repository.find_by_article_id(
                article_id
            )
        )

        assert result_by_article is not None

        assert (
            result_by_article["document_id"]
            == document_id
        )

        assert (
            result_by_article["html"]
            == original_html
        )

        # ==================================================
        # 6. Find By URL
        # ==================================================

        result_by_url = (
            repository.find_by_url(
                url
            )
        )

        assert result_by_url is not None

        assert (
            result_by_url["document_id"]
            == document_id
        )

        assert (
            result_by_url["html"]
            == original_html
        )

        # ==================================================
        # 7. Find By MongoDB ID
        # ==================================================

        result_by_id = (
            repository.find_by_id(
                mongo_id
            )
        )

        assert result_by_id is not None

        assert (
            result_by_id["document_id"]
            == document_id
        )

        assert (
            result_by_id["html"]
            == original_html
        )

        # ==================================================
        # 8. Update HTML
        # ==================================================

        updated = (
            repository.update_html(
                document_id,
                updated_html
            )
        )

        assert updated is True

        # ==================================================
        # 9. Verify Updated HTML
        # ==================================================

        updated_result = (
            repository.find_by_document_id(
                document_id
            )
        )

        assert updated_result is not None

        assert (
            updated_result["html"]
            == updated_html
        )

        assert (
            updated_result["html"]
            != original_html
        )

        # ==================================================
        # 10. MongoDB Metadata
        # ==================================================

        assert (
            updated_result["created_at"]
            is not None
        )

        assert (
            updated_result["updated_at"]
            is not None
        )

    finally:

        # ==================================================
        # Cleanup
        # ==================================================

        repository.delete_by_document_id(
            document_id
        )

        # ==================================================
        # Verify Cleanup
        # ==================================================

        assert (
            repository.exists(
                document_id
            )
            is False
        )
