"""
utils/check_archive_different_url.py

AutoSearch V4

Archive Different URL Check

測試：

    相同 Article
    +
    不同 URL
    +
    相同 HTML Content

預期：

    URL A + HTML
        ↓
    Version N

    URL B + 相同 HTML
        ↓
    Content Hash 相同
    但 URL 不同
        ↓
    NOT Duplicate
        ↓
    Version N+1


驗證 Duplicate Detection Policy：

    URL
    +
    content_hash

而不是：

    content_hash
"""

from services.archive_service import (
    ArchiveService
)


def main():

    print("=" * 60)
    print("AutoSearch V4")
    print("Archive Different URL Check")
    print("=" * 60)

    # ==========================================
    # Existing Article
    # ==========================================

    article_id = 89

    document_id_a = (
        "test-archive-different-url-a-20260820"
    )

    document_id_b = (
        "test-archive-different-url-b-20260820"
    )

    # ==========================================
    # Different URLs
    # ==========================================

    url_a = (
        "https://example.com/"
        "autosearch-v4-different-url-a-20260820"
    )

    url_b = (
        "https://example.com/"
        "autosearch-v4-different-url-b-20260820"
    )

    # ==========================================
    # IMPORTANT
    #
    # HTML 完全相同。
    #
    # 因此：
    #
    # content_hash A
    # =
    # content_hash B
    #
    # 但是 URL 不同。
    #
    # 預期：
    #
    # 不應判定 Duplicate。
    # ==========================================

    html = """
<!DOCTYPE html>
<html>
    <head>
        <title>AutoSearch V4 Different URL Test</title>
    </head>
    <body>
        <h1>AutoSearch V4 Archive Test</h1>
        <p>Same HTML content.</p>
        <p>Different URL test.</p>
        <p>Article ID: 89</p>
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
    # Existing Versions
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

    print(
        f"Existing versions: {existing_count}"
    )

    for version in existing_versions:

        print(
            f"  Version "
            f"{getattr(version, 'version_number', None)}"
        )

    # ==========================================
    # First Archive
    # ==========================================

    print()
    print("First Archive - URL A + HTML")
    print("-" * 60)

    first_version = (
        archive_service.save_html(
            article_id=article_id,
            url=url_a,
            html=html,
            document_id=document_id_a
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
    # Second Archive
    #
    # Different URL
    # Same HTML
    # ==========================================

    print()
    print("Second Archive - URL B + SAME HTML")
    print("-" * 60)

    second_version = (
        archive_service.save_html(
            article_id=article_id,
            url=url_b,
            html=html,
            document_id=document_id_b
        )
    )

    if second_version is None:

        print(
            "[FAIL] Second archive failed."
        )

        return

    second_version_number = getattr(
        second_version,
        "version_number",
        None
    )

    print(
        "[OK] Second archive completed."
    )

    print(
        f"Version: {second_version_number}"
    )

    # ==========================================
    # Get Final Versions
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
        f"Final versions: {final_count}"
    )

    for version in versions:

        print(
            f"  Version "
            f"{getattr(version, 'version_number', None)}"
        )

    # ==========================================
    # Expected
    # ==========================================

    expected_first_version = (
        existing_count + 1
    )

    expected_second_version = (
        expected_first_version + 1
    )

    expected_final_count = (
        existing_count + 2
    )

    # ==========================================
    # Validation
    # ==========================================

    print()
    print("Expected Result")
    print("-" * 60)

    # ------------------------------------------
    # First Version
    # ------------------------------------------

    if (
        first_version_number
        != expected_first_version
    ):

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
    # Second Version
    #
    # URL 不同，即使 HTML 相同，
    # 也必須建立新 Version。
    # ------------------------------------------

    if (
        second_version_number
        != expected_second_version
    ):

        print(
            "[FAIL] Different URL was incorrectly "
            "detected as duplicate."
        )

        print(
            f"Expected: {expected_second_version}"
        )

        print(
            f"Actual:   {second_version_number}"
        )

        return

    print(
        "[OK] Different URL created a new version"
    )

    # ------------------------------------------
    # Version Increment
    # ------------------------------------------

    if (
        second_version_number
        != first_version_number + 1
    ):

        print(
            "[FAIL] Version number did not "
            "increment correctly."
        )

        return

    print(
        "[OK] Version number increased by exactly 1"
    )

    # ------------------------------------------
    # Version Count
    # ------------------------------------------

    if (
        final_count
        != expected_final_count
    ):

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
        "[OK] Version count increased by exactly 2"
    )

    # ==========================================
    # PASS
    # ==========================================

    print()
    print("=" * 60)
    print(
        "[PASS] Archive Different URL test passed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
