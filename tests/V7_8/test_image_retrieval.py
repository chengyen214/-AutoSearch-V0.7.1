"""
test_image_retrieval.py

AutoSearch V7

R1.3 Image Retrieval Test

測試：

1. HTTP Image Retrieval
2. Session Image Retrieval
3. Referer Image Retrieval
4. Cookie Session Image Retrieval
5. SSL Fallback Image Retrieval
6. Browser Image Retrieval
7. Image Content Validation
8. Image Content Hash
9. Image Metadata
"""

from crawler.retrieval.image_retrieval import (
    retrieve_image_http,
    retrieve_image_session,
    retrieve_image_referer,
    retrieve_image_cookie_session,
    retrieve_image_ssl_fallback,
    retrieve_image_browser,
)


# ---------------------------------------------------------
# Test Image
# ---------------------------------------------------------

IMAGE_URL = (
    "https://httpbin.org/image/png"
)


# ---------------------------------------------------------
# Test Helper
# ---------------------------------------------------------

def print_result(name, result):
    print(f"\n{name}")
    print("-" * 60)

    print(
        f"success       : {result.success}"
    )

    print(
        f"strategy      : {result.strategy}"
    )

    print(
        f"status_code   : {result.status_code}"
    )

    print(
        f"content_type  : {result.content_type}"
    )

    print(
        f"content_size  : {result.content_size}"
    )

    print(
        f"content_hash  : {result.content_hash}"
    )

    print(
        f"final_url     : {result.final_url}"
    )

    print(
        f"elapsed_time  : "
        f"{result.elapsed_time:.3f}s"
    )

    if result.error:
        print(
            f"error         : {result.error}"
        )


def validate_result(result, strategy):
    """
    驗證 Image Retrieval 結果。
    """

    if not result.success:
        return False

    if result.strategy != strategy:
        return False

    if result.status_code != 200:
        return False

    if not result.content:
        return False

    if result.content_size <= 0:
        return False

    if not result.content_hash:
        return False

    if not result.final_url:
        return False

    if (
        not result.content_type
        or not result.content_type.lower().startswith(
            "image/"
        )
    ):
        return False

    return True


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_http():
    result = retrieve_image_http(
        IMAGE_URL
    )

    print_result(
        "TEST 1 HTTP Image Retrieval",
        result,
    )

    assert validate_result(
        result,
        "http",
    )


def test_session():
    result = retrieve_image_session(
        IMAGE_URL
    )

    print_result(
        "TEST 2 Session Image Retrieval",
        result,
    )

    assert validate_result(
        result,
        "session",
    )


def test_referer():
    result = retrieve_image_referer(
        IMAGE_URL
    )

    print_result(
        "TEST 3 Referer Image Retrieval",
        result,
    )

    assert validate_result(
        result,
        "referer",
    )


def test_cookie_session():
    result = retrieve_image_cookie_session(
        IMAGE_URL
    )

    print_result(
        "TEST 4 Cookie Session Image Retrieval",
        result,
    )

    assert validate_result(
        result,
        "cookie_session",
    )


def test_ssl_fallback():
    result = retrieve_image_ssl_fallback(
        IMAGE_URL
    )

    print_result(
        "TEST 5 SSL Fallback Image Retrieval",
        result,
    )

    assert validate_result(
        result,
        "ssl_fallback",
    )


def test_browser():
    result = retrieve_image_browser(
        IMAGE_URL
    )

    print_result(
        "TEST 6 Browser Image Retrieval",
        result,
    )

    assert validate_result(
        result,
        "browser",
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    tests = [
        (
            "TEST 1 HTTP Image Retrieval",
            test_http,
        ),
        (
            "TEST 2 Session Image Retrieval",
            test_session,
        ),
        (
            "TEST 3 Referer Image Retrieval",
            test_referer,
        ),
        (
            "TEST 4 Cookie Session Image Retrieval",
            test_cookie_session,
        ),
        (
            "TEST 5 SSL Fallback Image Retrieval",
            test_ssl_fallback,
        ),
        (
            "TEST 6 Browser Image Retrieval",
            test_browser,
        ),
    ]

    passed = 0
    failed = 0

    print("=" * 60)
    print("AutoSearch V7")
    print("R1.3 Image Retrieval Test")
    print("=" * 60)

    for name, test_function in tests:

        try:
            test_function()

            passed += 1

            print(
                f"\n{name}: PASS"
            )

        except Exception as exc:

            failed += 1

            print(
                f"\n{name}: FAIL"
            )

            print(
                f"Error: {exc}"
            )

    print("\n" + "=" * 60)
    print(
        f"PASS: {passed}"
    )
    print(
        f"FAIL: {failed}"
    )
    print(
        f"TOTAL: {passed + failed}"
    )
    print("=" * 60)

    if failed > 0:
        raise SystemExit(1)