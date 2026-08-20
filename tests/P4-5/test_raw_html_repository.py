"""
tests/P4-5/test_raw_html_repository.py

AutoSearch V4

P4-5

RawHTMLRepository MongoDB CRUD Test

測試：

1. save()
2. find_by_id()
3. find_by_article_id()
4. find_by_document_id()
5. find_by_url()
6. exists()
7. update_html()
8. delete_by_document_id()
9. count()
10. duplicate document_id
"""

from database.raw_html_repository import (
    RawHTMLRepository
)


def test_raw_html_repository():

    repository = RawHTMLRepository()

    # ==================================================
    # Test Data
    # ==================================================

    article_id = 999999999

    document_id = (
        "test_p4_5_raw_html_repository"
    )

    url = (
        "https://example.com/p4-5/raw-html"
    )

    html = (
        "<html>"
        "<body>"
        "<h1>AutoSearch V4</h1>"
        "<p>MongoDB Raw HTML Test</p>"
        "</body>"
        "</html>"
    )

    updated_html = (
        "<html>"
        "<body>"
        "<h1>AutoSearch V4 Updated</h1>"
        "<p>MongoDB Raw HTML Test Updated</p>"
        "</body>"
        "</html>"
    )

    # ==================================================
    # Cleanup Before Test
    # ==================================================

    repository.delete_by_document_id(
        document_id
    )

    # ==================================================
    # Count Before
    # ==================================================

    count_before = (
        repository.count()
    )

    assert count_before >= 0

    # ==================================================
    # Save
    # ==================================================

    mongo_id = (
        repository.save(
            article_id=article_id,
            document_id=document_id,
            url=url,
            html=html
        )
    )

    assert mongo_id is not None

    assert isinstance(
        mongo_id,
        str
    )

    # ==================================================
    # Count After Save
    # ==================================================

    count_after_save = (
        repository.count()
    )

    assert (
        count_after_save
        ==
        count_before + 1
    )

    # ==================================================
    # Find By MongoDB ID
    # ==================================================

    result_by_id = (
        repository.find_by_id(
            mongo_id
        )
    )

    assert result_by_id is not None

    assert (
        result_by_id["article_id"]
        ==
        article_id
    )

    assert (
        result_by_id["document_id"]
        ==
        document_id
    )

    assert (
        result_by_id["url"]
        ==
        url
    )

    assert (
        result_by_id["html"]
        ==
        html
    )

    assert (
        "_id"
        in
        result_by_id
    )

    # ==================================================
    # Find By Article ID
    # ==================================================

    result_by_article = (
        repository.find_by_article_id(
            article_id
        )
    )

    assert result_by_article is not None

    assert (
        result_by_article["document_id"]
        ==
        document_id
    )

    # ==================================================
    # Find By Document ID
    # ==================================================

    result_by_document = (
        repository.find_by_document_id(
            document_id
        )
    )

    assert result_by_document is not None

    assert (
        result_by_document["document_id"]
        ==
        document_id
    )

    assert (
        result_by_document["html"]
        ==
        html
    )

    # ==================================================
    # Find By URL
    # ==================================================

    result_by_url = (
        repository.find_by_url(
            url
        )
    )

    assert result_by_url is not None

    assert (
        result_by_url["document_id"]
        ==
        document_id
    )

    assert (
        result_by_url["url"]
        ==
        url
    )

    # ==================================================
    # Exists
    # ==================================================

    assert (
        repository.exists(
            document_id
        )
        is True
    )

    # ==================================================
    # Duplicate Detection
    #
    # Same document_id
    # should reuse existing document.
    # ==================================================

    duplicate_id = (
        repository.save(
            article_id=article_id,
            document_id=document_id,
            url=url,
            html=html
        )
    )

    assert duplicate_id is not None

    assert (
        duplicate_id
        ==
        mongo_id
    )

    # Count must NOT increase.
    # ==================================================

    count_after_duplicate = (
        repository.count()
    )

    assert (
        count_after_duplicate
        ==
        count_after_save
    )

    # ==================================================
    # Update HTML
    # ==================================================

    update_result = (
        repository.update_html(
            document_id=document_id,
            html=updated_html
        )
    )

    assert (
        update_result
        is True
    )

    # ==================================================
    # Verify Updated HTML
    # ==================================================

    updated_document = (
        repository.find_by_document_id(
            document_id
        )
    )

    assert updated_document is not None

    assert (
        updated_document["html"]
        ==
        updated_html
    )

    assert (
        updated_document["document_id"]
        ==
        document_id
    )

    # ==================================================
    # Verify Updated Timestamp
    # ==================================================

    assert (
        updated_document["updated_at"]
        is not None
    )

    assert (
        updated_document["created_at"]
        is not None
    )

    # ==================================================
    # Delete
    # ==================================================

    delete_result = (
        repository.delete_by_document_id(
            document_id
        )
    )

    assert (
        delete_result
        is True
    )

    # ==================================================
    # Verify Deleted
    # ==================================================

    deleted_document = (
        repository.find_by_document_id(
            document_id
        )
    )

    assert (
        deleted_document
        is None
    )

    # ==================================================
    # Exists After Delete
    # ==================================================

    assert (
        repository.exists(
            document_id
        )
        is False
    )

    # ==================================================
    # Count After Delete
    # ==================================================

    count_after_delete = (
        repository.count()
    )

    assert (
        count_after_delete
        ==
        count_before
    )