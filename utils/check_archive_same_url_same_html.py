"""
utils/check_archive_same_url_same_html.py

AutoSearch V4

Archive Same URL + Same HTML Check

驗證：

    相同 URL
    +
    相同 HTML
    ↓
    相同 File Hash
    ↓
    不建立新的 Archive Version


Archive Version Duplicate Policy：

    URL
    +
    File Hash

因此：

    相同 URL + 相同 HTML
        ↓
    不建立新的 Version


測試流程：

    1. 取得目前 Version 數量

    2. 第一次 Archive
           URL A + HTML A
       → 建立新 Version

    3. 第二次 Archive
           URL A + HTML A
       → 不建立新 Version

    4. 驗證：
           Version count 不增加
           Latest Version 不變
"""


from services.archive_service import (
    ArchiveService
)


def get_value(
    obj,
    name,
    default=None
):
    """
    安全取得 Model / Object 欄位。
    """

    return getattr(
        obj,
        name,
        default
    )


def main():

    print("=" * 60)
    print("AutoSearch V4")
    print("Archive Same URL + Same HTML Check")
    print("=" * 60)

    # ==========================================
    # Test Data
    # ==========================================

    article_id = 89

    test_url = (
        "https://example.com/"
        "autosearch-v4-same-url-same-html-20260820"
    )

    test_html = """
<html>
<head>
    <title>AutoSearch V4 Same Archive Test</title>
</head>
<body>
    <h1>AutoSearch V4 Archive Test</h1>
    <p>Same URL + Same HTML.</p>
</body>
</html>
""".strip()

    document_id = (
        "test-archive-same-url-same-html-20260820"
    )

    # ==========================================
    # Initialize
    # ==========================================

    print()
    print("Initializing ArchiveService")
    print("-" * 60)

    archive_service = ArchiveService()

    print(
        "[OK] ArchiveService initialized."
    )

    # ==========================================
    # Existing Versions
    # ==========================================

    print()
    print("Checking Existing Article Versions")
    print("-" * 60)

    versions_before = (
        archive_service.get_versions(
            article_id
        )
    )

    before_count = len(
        versions_before
    )

    print(
        f"Existing versions: {before_count}"
    )

    for version in versions_before:

        print(
            f"  Version "
            f"{get_value(version, 'version_number')}"
        )

    # ==========================================
    # First Archive
    # ==========================================

    print()
    print("First Archive - URL A + HTML A")
    print("-" * 60)

    first_version = (
        archive_service.save_html(
            article_id=article_id,
            document_id=document_id,
            url=test_url,
            html=test_html
        )
    )

    if first_version is None:

        print(
            "[FAIL] First archive did not "
            "return an ArchiveVersion."
        )

        return

    first_version_number = get_value(
        first_version,
        "version_number"
    )

    first_hash = get_value(
        first_version,
        "file_hash"
    )

    print(
        "[OK] First archive completed."
    )

    print(
        f"Version: {first_version_number}"
    )

    print(
        f"Hash   : {first_hash}"
    )

    # ==========================================
    # Version Count After First Archive
    # ==========================================

    versions_after_first = (
        archive_service.get_versions(
            article_id
        )
    )

    count_after_first = len(
        versions_after_first
    )

    print()
    print(
        "Checking Version Count After First Archive"
    )
    print("-" * 60)

    if count_after_first != (
        before_count + 1
    ):

        print(
            "[FAIL] First archive did not "
            "create exactly one new version."
        )

        print(
            f"       Before  : {before_count}"
        )

        print(
            f"       After   : {count_after_first}"
        )

        print(
            f"       Expected: {before_count + 1}"
        )

        return

    print(
        "[OK] First archive created a new version."
    )

    # ==========================================
    # Second Archive
    # ==========================================

    print()
    print("Second Archive - SAME URL + SAME HTML")
    print("-" * 60)

    second_version = (
        archive_service.save_html(
            article_id=article_id,
            document_id=document_id,
            url=test_url,
            html=test_html
        )
    )

    # ==========================================
    # Version Count After Second Archive
    # ==========================================

    versions_after_second = (
        archive_service.get_versions(
            article_id
        )
    )

    count_after_second = len(
        versions_after_second
    )

    print()
    print(
        "Checking Version Count After Second Archive"
    )
    print("-" * 60)

    print(
        f"After first archive : {count_after_first}"
    )

    print(
        f"After second archive: {count_after_second}"
    )

    # ==========================================
    # Validation
    # ==========================================

    print()
    print("Duplicate Validation")
    print("-" * 60)

    passed = True

    # ==========================================
    # 1. Version Count Must Not Increase
    # ==========================================

    if count_after_second != count_after_first:

        print(
            "[FAIL] Same URL + same HTML "
            "created a new version."
        )

        print(
            f"       After first  : "
            f"{count_after_first}"
        )

        print(
            f"       After second : "
            f"{count_after_second}"
        )

        passed = False

    else:

        print(
            "[OK] Same URL + same HTML "
            "did not create a new version."
        )

    # ==========================================
    # 2. Latest Version
    # ==========================================

    latest_version = (
        archive_service.get_latest_version(
            article_id
        )
    )

    latest_version_number = get_value(
        latest_version,
        "version_number"
    )

    latest_hash = get_value(
        latest_version,
        "file_hash"
    )

    print()
    print("Latest Version Validation")
    print("-" * 60)

    print(
        f"First Version  : "
        f"{first_version_number}"
    )

    print(
        f"Latest Version : "
        f"{latest_version_number}"
    )

    print(
        f"First Hash     : "
        f"{first_hash}"
    )

    print(
        f"Latest Hash    : "
        f"{latest_hash}"
    )

    if latest_version_number != (
        first_version_number
    ):

        print(
            "[FAIL] Latest version changed "
            "after duplicate archive."
        )

        passed = False

    else:

        print(
            "[OK] Latest version unchanged."
        )

    # ==========================================
    # 3. Hash
    # ==========================================

    if latest_hash != first_hash:

        print(
            "[FAIL] Latest version hash changed."
        )

        passed = False

    else:

        print(
            "[OK] File hash unchanged."
        )

    # ==========================================
    # 4. Returned Result
    # ==========================================

    print()
    print("Second Archive Result")
    print("-" * 60)

    if second_version is None:

        print(
            "[OK] Duplicate archive returned "
            "no new ArchiveVersion."
        )

    else:

        second_version_number = get_value(
            second_version,
            "version_number"
        )

        second_hash = get_value(
            second_version,
            "file_hash"
        )

        print(
            f"Returned Version : "
            f"{second_version_number}"
        )

        print(
            f"Returned Hash    : "
            f"{second_hash}"
        )

        if second_version_number != (
            first_version_number
        ):

            print(
                "[FAIL] Duplicate archive returned "
                "a different version number."
            )

            passed = False

        else:

            print(
                "[OK] Returned version number "
                "matches existing version."
            )

        if second_hash != first_hash:

            print(
                "[FAIL] Duplicate archive returned "
                "a different hash."
            )

            passed = False

        else:

            print(
                "[OK] Returned hash matches "
                "existing version."
            )

    # ==========================================
    # Expected Result
    # ==========================================

    print()
    print("Expected Result")
    print("-" * 60)

    if count_after_first == (
        before_count + 1
    ):

        print(
            "[OK] First archive created "
            "exactly one new version."
        )

    else:

        print(
            "[FAIL] First archive version "
            "count is incorrect."
        )

        passed = False

    if count_after_second == (
        count_after_first
    ):

        print(
            "[OK] Same URL + same HTML "
            "did not create a new version."
        )

    else:

        print(
            "[FAIL] Same URL + same HTML "
            "created an unexpected version."
        )

        passed = False

    if latest_version_number == (
        first_version_number
    ):

        print(
            "[OK] Version number remained unchanged."
        )

    else:

        print(
            "[FAIL] Version number changed."
        )

        passed = False

    # ==========================================
    # Final Result
    # ==========================================

    print()
    print("=" * 60)

    if not passed:

        print(
            "[FAIL] Archive Same URL + Same HTML "
            "test failed."
        )

        print("=" * 60)

        return

    print(
        "[PASS] Archive Same URL + Same HTML "
        "test passed."
    )

    print("=" * 60)


if __name__ == "__main__":

    main()
