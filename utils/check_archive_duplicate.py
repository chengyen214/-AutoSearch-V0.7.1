"""
utils/check_archive_duplicate.py

AutoSearch V4

Archive Duplicate Detection Check

測試：

    第一次：
        新 URL + 新 HTML
        → 建立新的 Archive Version

    第二次：
        相同 URL
        +
        相同 HTML Content Hash

        → Duplicate
        → 不建立新的 Version

重要：

    本測試不假設 Version Number = 1。

    因為 Article 89 已經存在歷史測試資料。

預期：

    First Version = 原本最新 Version + 1

    Second Version = First Version

    Article Version 總數只增加 1
"""

from services.archive_service import (
    ArchiveService
)


def main():

    print("=" * 60)
    print("AutoSearch V4")
    print("Archive Duplicate Detection Check")
    print("=" * 60)

    # ==========================================
    # Test Article
    # ==========================================

    article_id = 89

    document_id = (
        "test-archive-duplicate-20260820"
    )

    # ==========================================
    # IMPORTANT
    #
    # 使用全新的 URL。
    #
    # 避免受到之前測試：
    #
    #     autosearch-v4-article-89-test
    #
    # 的 Version 1 / Version 2 影響。
    # ==========================================

    url = (
        "https://example.com/"
        "autosearch-v4-duplicate-test-20260820"
    )

    # ==========================================
    # 固定 HTML
    #
    # First / Second Archive
    # 必須使用完全相同 HTML。
    #
    # 因此 generate_content_hash(html)
    # 會產生相同 Hash。
    # ==========================================

    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>AutoSearch V4 Duplicate Test</title>
    </head>
    <body>
        <h1>AutoSearch V4 Duplicate Detection Test</h1>
        <p>Duplicate detection verification.</p>
    </body>
</html>
"""

    # ==========================================
    # Archive Service
    # ==========================================

    archive_service = (
        ArchiveService()
    )

    # ==========================================
    # Get Existing Versions
    #
    # 不假設 Article 89 從 Version 1 開始。
    # ==========================================

    print()
    print("Checking Existing Article Versions")
    print("-" * 60)

    existing_versions = (
        archive_service.get_versions(
            article_id
        )
    )

    existing_count = len(
        existing_versions
    )

    existing_version_numbers = [
        getattr(
            version,
            "version_number",
            None
        )
        for version in existing_versions
    ]

    print(
        f"Existing versions: {existing_count}"
    )

    for version_number in (
        existing_version_numbers
    ):

        print(
            f"  Version {version_number}"
        )

    # ==========================================
    # First Save
    # ==========================================

    print()
    print("First Archive - New URL + New HTML")
    print("-" * 60)

    first_version = (
        archive_service.save_html(
            article_id=article_id,
            url=url,
            html=html,
            document_id=document_id
        )
    )

    if first_version is None:

        print(
            "[FAIL] First archive failed."
        )

        return

    first_version_number = getattr(
        first_version,
        "version_number",
        None
    )

    print(
        "[OK] First archive completed."
    )

    print(
        f"Version: {first_version_number}"
    )

    # ==========================================
    # Expected First Version
    # ==========================================

    if existing_version_numbers:

        expected_first_version = max(
            existing_version_numbers
        ) + 1

    else:

        expected_first_version = 1

    print(
        f"Expected Version: "
        f"{expected_first_version}"
    )

    # ==========================================
    # Second Save
    #
    # Same URL
    # +
    # Same HTML
    #
    # → Duplicate
    # ==========================================

    print()
    print("Second Archive - Same URL + Same HTML")
    print("-" * 60)

    second_version = (
        archive_service.save_html(
            article_id=article_id,
            url=url,
            html=html,
            document_id=document_id
        )
    )

    if second_version is None:

        print(
            "[FAIL] Second archive returned None."
        )

        return

    second_version_number = getattr(
        second_version,
        "version_number",
        None
    )

    print(
        "[OK] Second archive returned."
    )

    print(
        f"Version: {second_version_number}"
    )

    # ==========================================
    # Get Versions After Test
    # ==========================================

    print()
    print("Checking Article Versions")
    print("-" * 60)

    versions = (
        archive_service.get_versions(
            article_id
        )
    )

    final_count = len(
        versions
    )

    print(
        f"Total versions: {final_count}"
    )

    for version in versions:

        print(
            f"  Version "
            f"{getattr(version, 'version_number', None)}"
        )

    # ==========================================
    # Validation
    # ==========================================

    print()
    print("Expected Result")
    print("-" * 60)

    # ------------------------------------------
    # First Archive
    # ------------------------------------------

    if first_version_number != expected_first_version:

        print(
            "[FAIL] First archive version mismatch."
        )

        print(
            f"Expected: {expected_first_version}"
        )

        print(
            f"Actual:   {first_version_number}"
        )

        return

    print(
        "[OK] First archive created a new version"
    )

    # ------------------------------------------
    # Second Archive
    #
    # 必須回傳相同 Version。
    # ------------------------------------------

    if second_version_number != first_version_number:

        print(
            "[FAIL] Duplicate archive created "
            "a new version."
        )

        print(
            f"First Version:  {first_version_number}"
        )

        print(
            f"Second Version: {second_version_number}"
        )

        return

    print(
        "[OK] Second archive detected as duplicate"
    )

    print(
        "[OK] Second archive returned the "
        "existing version"
    )

    # ------------------------------------------
    # Version Count
    #
    # 兩次 save：
    #
    #     第一次 → +1
    #     第二次 → +0
    #
    # 所以最終：
    #
    #     existing_count + 1
    # ------------------------------------------

    expected_final_count = (
        existing_count + 1
    )

    if final_count != expected_final_count:

        print(
            "[FAIL] Unexpected archive version count."
        )

        print(
            f"Expected: {expected_final_count}"
        )

        print(
            f"Actual:   {final_count}"
        )

        return

    print(
        "[OK] Version count increased by exactly 1"
    )

    # ==========================================
    # Final PASS
    # ==========================================

    print()
    print("=" * 60)
    print(
        "[PASS] Archive Duplicate Detection test passed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()