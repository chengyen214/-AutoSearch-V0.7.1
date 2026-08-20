"""
utils/check_archive_new_version.py

AutoSearch V4

Archive New Version Check

測試：

    相同 Article
    +
    相同 URL
    +
    不同 HTML Content Hash

預期：

    第一次 → 建立新 Version
    第二次 → HTML 不同
              Content Hash 不同
              不判定為 Duplicate
              建立新的 Version

驗證：

    Same URL
    +
    Different HTML
        ↓
    New Archive Version
"""


from services.archive_service import (
    ArchiveService
)


def main():

    print("=" * 60)
    print("AutoSearch V4")
    print("Archive New Version Check")
    print("=" * 60)

    # ==========================================
    # Existing Article
    # ==========================================

    article_id = 89

    document_id = (
        "test-archive-new-version-20260820"
    )

    url = (
        "https://example.com/"
        "autosearch-v4-new-version-test"
    )

    # ==========================================
    # HTML Version 1
    # ==========================================

    html_v1 = """
<!DOCTYPE html>
<html>
    <head>
        <title>AutoSearch V4 New Version Test V1</title>
    </head>
    <body>
        <h1>AutoSearch V4 Archive Version Test</h1>
        <p>This is archive HTML version 1.</p>
        <p>Article ID: 89</p>
        <p>Content Version: 1</p>
    </body>
</html>
"""

    # ==========================================
    # HTML Version 2
    #
    # SAME URL
    # DIFFERENT HTML
    # ==========================================

    html_v2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>AutoSearch V4 New Version Test V2</title>
    </head>
    <body>
        <h1>AutoSearch V4 Archive Version Test</h1>
        <p>This is archive HTML version 2.</p>
        <p>Article ID: 89</p>
        <p>Content Version: 2</p>
        <p>Updated content.</p>
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
    print("First Archive - URL + HTML V1")
    print("-" * 60)

    first_version = (
        archive_service.save_html(
            article_id=article_id,
            url=url,
            html=html_v1,
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
    # Second Archive
    # ==========================================

    print()
    print("Second Archive - SAME URL + DIFFERENT HTML")
    print("-" * 60)

    second_version = (
        archive_service.save_html(
            article_id=article_id,
            url=url,
            html=html_v2,
            document_id=document_id
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
    # Get Versions
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
    # Expected Values
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
    # ------------------------------------------

    if (
        second_version_number
        != expected_second_version
    ):

        print(
            "[FAIL] Different HTML did not "
            "create a new version."
        )

        print(
            f"Expected: {expected_second_version}"
        )

        print(
            f"Actual:   {second_version_number}"
        )

        return

    print(
        "[OK] Different HTML created a new version"
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
        "[PASS] Archive New Version test passed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
