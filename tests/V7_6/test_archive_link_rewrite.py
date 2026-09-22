"""
tests/V7_6/test_archive_link_rewrite.py

AutoSearch V7

Archive Viewer
Archive Link Rewrite Unit Test

用途：
    不連 MongoDB。

    只測試：

        rewrite_archive_links()

執行：

    python -m tests.V7_6.test_archive_link_rewrite
"""

from urllib.parse import quote

from api.routes.archive_viewer import (
    rewrite_archive_links,
)


def run_test(
    name: str,
    html: str,
    original_url: str,
    expected: str,
):
    print("=" * 70)
    print(f"TEST: {name}")
    print("=" * 70)

    result = rewrite_archive_links(
        html,
        original_url,
    )

    print("INPUT:")
    print(html)

    print()
    print("OUTPUT:")
    print(result)

    print()
    print("EXPECTED:")
    print(expected)

    print()

    if result != expected:
        print("❌ FAILED")
        print("Actual:")
        print(repr(result))
        print()
        print("Expected:")
        print(repr(expected))

        raise AssertionError(
            f"Test failed: {name}"
        )

    print("✅ PASSED")
    print()


def main():

    original_url = (
        "https://example.com/news/article-001"
    )

    # ========================================================
    # 1. HTTPS absolute URL
    # ========================================================

    target_url = (
        "https://example.com/news/article-002"
    )

    expected_archive_url = (
        "/archive/link?url="
        + quote(
            target_url,
            safe="",
        )
    )

    run_test(
        name="HTTPS absolute URL",
        html=(
            '<a href="'
            + target_url
            + '">Article</a>'
        ),
        original_url=original_url,
        expected=(
            '<a href="'
            + expected_archive_url
            + '">Article</a>'
        ),
    )

    # ========================================================
    # 2. HTTP absolute URL
    # ========================================================

    target_url = (
        "http://example.com/news/article-003"
    )

    expected_archive_url = (
        "/archive/link?url="
        + quote(
            target_url,
            safe="",
        )
    )

    run_test(
        name="HTTP absolute URL",
        html=(
            '<a href="'
            + target_url
            + '">Article</a>'
        ),
        original_url=original_url,
        expected=(
            '<a href="'
            + expected_archive_url
            + '">Article</a>'
        ),
    )

    # ========================================================
    # 3. Relative URL
    # ========================================================

    relative_url = (
        "/news/article-004"
    )

    absolute_url = (
        "https://example.com/news/article-004"
    )

    expected_archive_url = (
        "/archive/link?url="
        + quote(
            absolute_url,
            safe="",
        )
    )

    run_test(
        name="Relative URL",
        html=(
            '<a href="'
            + relative_url
            + '">Article</a>'
        ),
        original_url=original_url,
        expected=(
            '<a href="'
            + expected_archive_url
            + '">Article</a>'
        ),
    )

    # ========================================================
    # 4. mailto
    # ========================================================

    mailto_url = (
        "mailto:test@example.com"
    )

    run_test(
        name="mailto link is preserved",
        html=(
            '<a href="'
            + mailto_url
            + '">Email</a>'
        ),
        original_url=original_url,
        expected=(
            '<a href="'
            + mailto_url
            + '">Email</a>'
        ),
    )

    # ========================================================
    # 5. Anchor
    # ========================================================

    anchor_url = (
        "#section-2"
    )

    run_test(
        name="Anchor link is preserved",
        html=(
            '<a href="'
            + anchor_url
            + '">Section</a>'
        ),
        original_url=original_url,
        expected=(
            '<a href="'
            + anchor_url
            + '">Section</a>'
        ),
    )

    # ========================================================
    # 6. Archive internal URL
    # ========================================================

    internal_url = (
        "/archive/resource/css/"
        "https%3A%2F%2Fexample.com%2Fstyle.css"
    )

    run_test(
        name="Archive internal URL is preserved",
        html=(
            '<a href="'
            + internal_url
            + '">CSS</a>'
        ),
        original_url=original_url,
        expected=(
            '<a href="'
            + internal_url
            + '">CSS</a>'
        ),
    )

    # ========================================================
    # 7. Query + Fragment
    # ========================================================

    target_url = (
        "https://example.com/news/article-005"
        "?page=2"
        "#comments"
    )

    expected_archive_url = (
        "/archive/link?url="
        + quote(
            target_url,
            safe="",
        )
    )

    run_test(
        name="URL with query and fragment",
        html=(
            '<a href="'
            + target_url
            + '">Article</a>'
        ),
        original_url=original_url,
        expected=(
            '<a href="'
            + expected_archive_url
            + '">Article</a>'
        ),
    )

    print("=" * 70)
    print("ALL ARCHIVE LINK REWRITE TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()