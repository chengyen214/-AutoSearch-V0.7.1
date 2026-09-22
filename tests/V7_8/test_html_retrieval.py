"""
test_html_retrieval.py

AutoSearch V7

R1.1 HTML Retrieval Test

測試：

1. HTTP
2. HTTP Session
3. HTTP SSL Fallback
4. HTTP Referer
5. HTTP Cookie Session
6. Browser

測試目的：

    確認 R1.1 HTML Retrieval Strategy
    可以正常執行並回傳 HTMLRetrievalResult。

注意：

    本測試只測試 R1.1 HTML Retrieval。

    不測試：

        CSS Retrieval
        Image Retrieval
        Site Profile
        MongoDB
        R2
        R3
"""

from crawler.retrieval.html_retrieval import (
    HTMLRetrievalResult,
    retrieve_html,
)


TEST_URL = "https://example.com/"


def print_result(
    result: HTMLRetrievalResult,
):
    """
    顯示 HTML Retrieval Result。
    """

    print()
    print("=" * 70)

    print(
        f"Strategy      : "
        f"{result.strategy}"
    )

    print(
        f"Success       : "
        f"{result.success}"
    )

    print(
        f"URL           : "
        f"{result.url}"
    )

    print(
        f"Final URL     : "
        f"{result.final_url}"
    )

    print(
        f"Status Code   : "
        f"{result.status_code}"
    )

    print(
        f"Content Type  : "
        f"{result.content_type}"
    )

    print(
        f"Content Size  : "
        f"{result.content_size}"
    )

    print(
        f"Elapsed Time  : "
        f"{result.elapsed_time:.3f}s"
    )

    print(
        f"Error         : "
        f"{result.error}"
    )

    print("=" * 70)


def test_http():
    """
    Test 1

    HTTP
    """

    result = retrieve_html(
        TEST_URL,
        strategy="http",
    )

    print_result(result)

    assert isinstance(
        result,
        HTMLRetrievalResult,
    )

    return result


def test_session():
    """
    Test 2

    HTTP Session
    """

    result = retrieve_html(
        TEST_URL,
        strategy="session",
    )

    print_result(result)

    assert isinstance(
        result,
        HTMLRetrievalResult,
    )

    return result


def test_referer():
    """
    Test 3

    HTTP Referer
    """

    result = retrieve_html(
        TEST_URL,
        strategy="referer",
    )

    print_result(result)

    assert isinstance(
        result,
        HTMLRetrievalResult,
    )

    return result


def test_cookie_session():
    """
    Test 4

    HTTP Cookie Session
    """

    result = retrieve_html(
        TEST_URL,
        strategy="cookie_session",
    )

    print_result(result)

    assert isinstance(
        result,
        HTMLRetrievalResult,
    )

    return result


def test_ssl_fallback():
    """
    Test 5

    HTTP SSL Fallback
    """

    result = retrieve_html(
        TEST_URL,
        strategy="ssl_fallback",
    )

    print_result(result)

    assert isinstance(
        result,
        HTMLRetrievalResult,
    )

    return result


def test_browser():
    """
    Test 6

    Browser
    """

    result = retrieve_html(
        TEST_URL,
        strategy="browser",
    )

    print_result(result)

    assert isinstance(
        result,
        HTMLRetrievalResult,
    )

    return result


def main():
    """
    執行全部 R1.1 HTML Retrieval Tests。
    """

    print()
    print("=" * 70)
    print("AutoSearch V7")
    print("R1.1 HTML Retrieval Test")
    print("=" * 70)

    print(
        f"Test URL: "
        f"{TEST_URL}"
    )

    results = []

    results.append(
        test_http()
    )

    results.append(
        test_session()
    )

    results.append(
        test_referer()
    )

    results.append(
        test_cookie_session()
    )

    results.append(
        test_ssl_fallback()
    )

    results.append(
        test_browser()
    )

    print()
    print("=" * 70)
    print(
        "R1.1 HTML Retrieval "
        "Test Summary"
    )
    print("=" * 70)

    for result in results:

        status = (
            "PASS"
            if result.success
            else "FAIL"
        )

        print(
            f"{status:<6} "
            f"{result.strategy:<20} "
            f"{result.elapsed_time:.3f}s"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()