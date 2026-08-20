"""
utils/check_raw_html_write.py

AutoSearch V4

Raw HTML MongoDB Actual Write Check

用途：

    實際測試：

        ArchiveService
            ↓
        RawHTMLRepository
            ↓
        MongoDB raw_html

確認：

    1. ArchiveService 可以成功保存 HTML
    2. MongoDB raw_html 有資料
    3. content_hash 有實際寫入
    4. URL 正確
    5. document_id 正確
"""

from services.archive_service import (
    ArchiveService
)

from database.raw_html_repository import (
    RawHTMLRepository
)

from utils.hash import (
    generate_content_hash
)


def main():

    print("=" * 60)
    print("AutoSearch V4")
    print("Raw HTML MongoDB Actual Write Check")
    print("=" * 60)

    # ==========================================
    # Test Data
    # ==========================================

    article_id = 89

    document_id = (
        "test-5ba342ff9d0e4e1fb72dd7ebb2325a57"
    )

    url = (
        "https://example.com/autosearch-v4-article-89-test"
    )

    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AutoSearch V4 Article 89 Raw HTML Test</title>
        </head>
        <body>
            <h1>AutoSearch V4 Article 89 MongoDB Test</h1>
            <p>Raw HTML write verification.</p>
            <p>Article ID: 89</p>
        </body>
    </html>
    """

    # ==========================================
    # Expected Hash
    # ==========================================

    expected_hash = (
        generate_content_hash(
            html
        )
    )

    print()
    print("Test Data")
    print("-" * 60)
    print(f"article_id   : {article_id}")
    print(f"document_id  : {document_id}")
    print(f"url          : {url}")
    print(f"content_hash : {expected_hash}")

    # ==========================================
    # ArchiveService
    # ==========================================

    print()
    print("Calling ArchiveService.save_html()...")
    print("-" * 60)

    archive_service = (
        ArchiveService()
    )

    saved_version = (
        archive_service.save_html(
            article_id=article_id,
            url=url,
            html=html,
            document_id=document_id
        )
    )

    if saved_version is None:

        print()
        print("[FAIL] ArchiveService.save_html() failed.")
        return

    print()
    print("[OK] ArchiveService.save_html() succeeded.")

    # ==========================================
    # MongoDB Verification
    # ==========================================

    print()
    print("Checking MongoDB raw_html...")
    print("-" * 60)

    raw_html_repo = (
        RawHTMLRepository()
    )

    document = (
        raw_html_repo.find_by_document_id(
            document_id
        )
    )

    if document is None:

        print(
            "[FAIL] Raw HTML document "
            "was not found in MongoDB."
        )

        return

    print("[OK] MongoDB raw_html document found.")

    # ==========================================
    # Verify Fields
    # ==========================================

    actual_hash = (
        document.get(
            "content_hash"
        )
    )

    actual_url = (
        document.get(
            "url"
        )
    )

    actual_document_id = (
        document.get(
            "document_id"
        )
    )

    actual_article_id = (
        document.get(
            "article_id"
        )
    )

    print()
    print("MongoDB Document Verification")
    print("-" * 60)

    print(
        f"article_id   : {actual_article_id}"
    )

    print(
        f"document_id  : {actual_document_id}"
    )

    print(
        f"url          : {actual_url}"
    )

    print(
        f"content_hash : {actual_hash}"
    )

    # ==========================================
    # Assertions
    # ==========================================

    print()
    print("Expected Result")
    print("-" * 60)

    checks = {

        "article_id":
            actual_article_id == article_id,

        "document_id":
            actual_document_id == document_id,

        "url":
            actual_url == url,

        "content_hash exists":
            bool(actual_hash),

        "content_hash correct":
            actual_hash == expected_hash,

    }

    all_passed = True

    for name, passed in checks.items():

        if passed:

            print(
                f"[OK] {name}"
            )

        else:

            print(
                f"[FAIL] {name}"
            )

            all_passed = False

    # ==========================================
    # Final Result
    # ==========================================

    print()
    print("=" * 60)

    if all_passed:

        print(
            "[PASS] Raw HTML MongoDB actual write test passed."
        )

    else:

        print(
            "[FAIL] Raw HTML MongoDB actual write test failed."
        )

    print("=" * 60)


if __name__ == "__main__":
    main()