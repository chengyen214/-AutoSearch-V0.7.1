"""
test_css_retrieval.py

AutoSearch V7

R1.2 CSS Retrieval Test

測試：

1. HTTP CSS Retrieval
2. Session CSS Retrieval
3. Referer CSS Retrieval
4. Cookie Session CSS Retrieval
5. SSL Fallback CSS Retrieval
6. Browser CSS Retrieval
7. HTML Linked CSS Discovery
8. CSS @import Discovery
9. Inline CSS Extraction

執行：

    python -m tests.V7_8.test_css_retrieval
"""

from crawler.retrieval.css_retrieval import (
    CSSRetrievalResult,
    CSSDiscoveryResult,
    retrieve_css,
    discover_css_from_html,
    discover_css_imports,
)


TEST_CSS_URL = (
    "https://germanfrelo.github.io/"
    "base-css-stylesheet/base.css"
)

TEST_BASE_URL = (
    "https://germanfrelo.github.io/"
    "base-css-stylesheet/"
)

TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="/css/main.css">
    <link
        rel="stylesheet"
        href="https://example.com/theme.css"
    >

    <style>
        body {
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>
    <h1>CSS Retrieval Test</h1>
</body>
</html>
"""


TEST_CSS = """
@import "base.css";
@import url("theme.css");
@import url(layout.css);

body {
    margin: 0;
    padding: 0;
}
"""


def print_css_result(result: CSSRetrievalResult) -> None:
    print(f"Strategy      : {result.strategy}")
    print(f"Success       : {result.success}")
    print(f"URL           : {result.url}")
    print(f"Final URL     : {result.final_url}")
    print(f"Status Code   : {result.status_code}")
    print(f"Content Type  : {result.content_type}")
    print(f"Content Size  : {result.content_size}")
    print(f"Content Hash  : {result.content_hash}")
    print(f"Elapsed Time  : {result.elapsed_time:.3f}s")
    print(f"Error         : {result.error}")


def print_discovery_result(
    result: CSSDiscoveryResult,
) -> None:
    print(f"Strategy          : {result.strategy}")
    print(f"Success           : {result.success}")
    print(f"Base URL          : {result.base_url}")

    print(f"CSS URL Count     : {len(result.css_urls)}")

    for index, css_url in enumerate(
        result.css_urls,
        start=1,
    ):
        print(f"  CSS[{index}]      : {css_url}")

    print(f"Inline CSS Count  : {len(result.inline_css)}")

    for index, css in enumerate(
        result.inline_css,
        start=1,
    ):
        print(
            f"  Inline[{index}]   : "
            f"{len(css)} chars"
        )

    print(f"Import URL Count  : {len(result.import_urls)}")

    for index, import_url in enumerate(
        result.import_urls,
        start=1,
    ):
        print(
            f"  Import[{index}]   : "
            f"{import_url}"
        )

    print(
        f"Elapsed Time      : "
        f"{result.elapsed_time:.3f}s"
    )

    print(f"Error             : {result.error}")


def test_http() -> CSSRetrievalResult:
    print("\n" + "=" * 70)
    print("TEST 1: HTTP CSS Retrieval")
    print("=" * 70)

    result = retrieve_css(
        TEST_CSS_URL,
        strategy="http",
    )

    print_css_result(result)

    assert isinstance(
        result,
        CSSRetrievalResult,
    )

    assert result.strategy == "http"
    assert result.success is True
    assert result.css
    assert result.content_size > 0
    assert result.content_hash

    return result


def test_session() -> CSSRetrievalResult:
    print("\n" + "=" * 70)
    print("TEST 2: Session CSS Retrieval")
    print("=" * 70)

    result = retrieve_css(
        TEST_CSS_URL,
        strategy="session",
    )

    print_css_result(result)

    assert isinstance(
        result,
        CSSRetrievalResult,
    )

    assert result.strategy == "session"
    assert result.success is True
    assert result.css
    assert result.content_size > 0
    assert result.content_hash

    return result


def test_referer() -> CSSRetrievalResult:
    print("\n" + "=" * 70)
    print("TEST 3: Referer CSS Retrieval")
    print("=" * 70)

    result = retrieve_css(
        TEST_CSS_URL,
        strategy="referer",
        referer=TEST_BASE_URL,
    )

    print_css_result(result)

    assert isinstance(
        result,
        CSSRetrievalResult,
    )

    assert result.strategy == "referer"
    assert result.success is True
    assert result.css
    assert result.content_size > 0
    assert result.content_hash

    return result


def test_cookie_session() -> CSSRetrievalResult:
    print("\n" + "=" * 70)
    print("TEST 4: Cookie Session CSS Retrieval")
    print("=" * 70)

    result = retrieve_css(
        TEST_CSS_URL,
        strategy="cookie_session",
        cookies={
            "autos_test": "1",
        },
    )

    print_css_result(result)

    assert isinstance(
        result,
        CSSRetrievalResult,
    )

    assert result.strategy == "cookie_session"
    assert result.success is True
    assert result.css
    assert result.content_size > 0
    assert result.content_hash

    return result


def test_ssl_fallback() -> CSSRetrievalResult:
    print("\n" + "=" * 70)
    print("TEST 5: SSL Fallback CSS Retrieval")
    print("=" * 70)

    result = retrieve_css(
        TEST_CSS_URL,
        strategy="ssl_fallback",
    )

    print_css_result(result)

    assert isinstance(
        result,
        CSSRetrievalResult,
    )

    assert result.strategy == "ssl_fallback"
    assert result.success is True
    assert result.css
    assert result.content_size > 0
    assert result.content_hash

    return result


def test_browser() -> CSSRetrievalResult:
    print("\n" + "=" * 70)
    print("TEST 6: Browser CSS Retrieval")
    print("=" * 70)

    result = retrieve_css(
        TEST_CSS_URL,
        strategy="browser",
    )

    print_css_result(result)

    assert isinstance(
        result,
        CSSRetrievalResult,
    )

    assert result.strategy == "browser"
    assert result.success is True
    assert result.css
    assert result.content_size > 0
    assert result.content_hash

    return result


def test_html_linked_css() -> CSSDiscoveryResult:
    print("\n" + "=" * 70)
    print("TEST 7: HTML Linked CSS Discovery")
    print("=" * 70)

    result = discover_css_from_html(
        TEST_HTML,
        base_url=TEST_BASE_URL,
    )

    print_discovery_result(result)

    assert isinstance(
        result,
        CSSDiscoveryResult,
    )

    assert result.strategy == "html_linked_css"
    assert result.success is True

    assert len(result.css_urls) == 3

    assert (
        "https://germanfrelo.github.io/"
        "base-css-stylesheet/style.css"
        in result.css_urls
    )

    assert (
        "https://germanfrelo.github.io/css/main.css"
        in result.css_urls
    )

    assert (
        "https://example.com/theme.css"
        in result.css_urls
    )

    return result


def test_css_import() -> CSSDiscoveryResult:
    print("\n" + "=" * 70)
    print("TEST 8: CSS @import Discovery")
    print("=" * 70)

    result = discover_css_imports(
        TEST_CSS,
        base_url=TEST_BASE_URL,
    )

    print_discovery_result(result)

    assert isinstance(
        result,
        CSSDiscoveryResult,
    )

    assert result.strategy == "css_import"
    assert result.success is True

    assert len(result.import_urls) == 3

    assert (
        "https://germanfrelo.github.io/"
        "base-css-stylesheet/base.css"
        in result.import_urls
    )

    assert (
        "https://germanfrelo.github.io/"
        "base-css-stylesheet/theme.css"
        in result.import_urls
    )

    assert (
        "https://germanfrelo.github.io/"
        "base-css-stylesheet/layout.css"
        in result.import_urls
    )

    return result


def test_inline_css() -> CSSDiscoveryResult:
    print("\n" + "=" * 70)
    print("TEST 9: Inline CSS Extraction")
    print("=" * 70)

    result = discover_css_from_html(
        TEST_HTML,
        base_url=TEST_BASE_URL,
    )

    print_discovery_result(result)

    assert isinstance(
        result,
        CSSDiscoveryResult,
    )

    assert result.success is True
    assert len(result.inline_css) > 0

    assert "margin: 0" in result.inline_css[0]
    assert "padding: 0" in result.inline_css[0]

    return result


def main() -> None:
    print("=" * 70)
    print("AutoSearch V7")
    print("R1.2 CSS Retrieval Test")
    print("=" * 70)

    results = []

    tests = [
        ("HTTP", test_http),
        ("Session", test_session),
        ("Referer", test_referer),
        ("Cookie Session", test_cookie_session),
        ("SSL Fallback", test_ssl_fallback),
        ("Browser", test_browser),
        ("HTML Linked CSS", test_html_linked_css),
        ("CSS @import", test_css_import),
        ("Inline CSS", test_inline_css),
    ]

    for name, test_func in tests:
        try:
            result = test_func()

            results.append(
                (
                    name,
                    result.success,
                    None,
                )
            )

        except Exception as error:
            print("\nTEST ERROR")
            print(f"{name}: {error}")

            results.append(
                (
                    name,
                    False,
                    str(error),
                )
            )

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0

    for name, success, error in results:

        if success:
            print(f"{name:<25} PASS")
            passed += 1

        else:
            print(f"{name:<25} FAIL")

            if error:
                print(f"  Error: {error}")

            failed += 1

    print("-" * 70)
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")
    print(f"TOTAL: {len(results)}")
    print("=" * 70)

    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()