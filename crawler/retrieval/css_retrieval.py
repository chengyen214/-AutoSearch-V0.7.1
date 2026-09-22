"""
css_retrieval.py

AutoSearch V5

R1.2 CSS Retrieval

功能：

1. HTTP CSS Retrieval
2. Session CSS Retrieval
3. Referer CSS Retrieval
4. Cookie Session CSS Retrieval
5. SSL Fallback CSS Retrieval
6. HTML Linked CSS Discovery
7. CSS @import Discovery
8. Browser CSS Retrieval
9. Inline / Embedded CSS Extraction

設計原則：

    R1.2 只負責 CSS Retrieval。

    不負責：
        - Site Profile
        - Strategy Selection
        - MongoDB Profile
        - Crawler Integration
        - R2 Probe

    R2 之後會使用本模組的 Retrieval Result
    評估不同 CSS Retrieval Strategy 的：

        1. Completeness
        2. Speed
"""

from __future__ import annotations

import hashlib
import re
import time

from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
import urllib3
from bs4 import BeautifulSoup
from requests.exceptions import SSLError


DEFAULT_TIMEOUT = 15

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept": "text/css,*/*;q=0.1",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}


_SSL_FALLBACK_HOSTS = set()


@dataclass
class CSSRetrievalResult:
    """
    CSS Retrieval 統一結果。
    """

    success: bool
    strategy: str
    url: str

    final_url: Optional[str] = None
    css: Optional[str] = None

    status_code: Optional[int] = None
    content_type: Optional[str] = None
    content_size: int = 0

    content_hash: Optional[str] = None

    elapsed_time: float = 0.0
    error: Optional[str] = None


@dataclass
class CSSDiscoveryResult:
    """
    HTML / CSS 中發現的 CSS 資源。
    """

    success: bool
    strategy: str

    base_url: str

    css_urls: List[str]
    inline_css: List[str]

    import_urls: List[str]

    elapsed_time: float = 0.0
    error: Optional[str] = None


def _get_hostname(url: str) -> str:
    """
    取得 URL hostname。
    """

    return (urlparse(url).hostname or "").lower()


def _is_ssl_fallback_host(url: str) -> bool:
    """
    判斷 host 是否已進入 SSL fallback。
    """

    return _get_hostname(url) in _SSL_FALLBACK_HOSTS


def _mark_ssl_fallback_host(url: str) -> None:
    """
    將 host 加入 SSL fallback cache。
    """

    hostname = _get_hostname(url)

    if hostname:
        _SSL_FALLBACK_HOSTS.add(hostname)


def _fix_encoding(response: requests.Response) -> str:
    """
    修正 CSS encoding。
    """

    if not response.encoding:
        response.encoding = response.apparent_encoding or "utf-8"

    return response.text


def _generate_content_hash(content: str) -> str:
    """
    產生 CSS Content Hash。
    """

    return hashlib.sha256(
        content.encode("utf-8", errors="ignore")
    ).hexdigest()


def _validate_css_response(
    response,
) -> bool:
    """
    驗證 Response 是否為 CSS。

    同時支援：

        requests.Response
        Playwright APIResponse
    """

    if hasattr(response, "status_code"):
        status_code = response.status_code

        content_type = (
            response.headers.get(
                "Content-Type",
                "",
            )
            .lower()
        )

    else:
        status_code = response.status

        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
            .lower()
        )

    if status_code >= 400:
        return False

    if "text/css" in content_type:
        return True

    text = response.text[:2000].lower()

    css_markers = (
        "{",
        "}",
        "@import",
        "@charset",
    )

    return any(
        marker in text
        for marker in css_markers
    )


def _build_result(
    *,
    success: bool,
    strategy: str,
    url: str,
    response=None,
    css: Optional[str] = None,
    elapsed_time: float = 0.0,
    error: Optional[str] = None,
) -> CSSRetrievalResult:
    """
    建立統一 CSS Retrieval Result。

    支援：

        requests.Response
        Playwright APIResponse
    """

    if response is None:
        return CSSRetrievalResult(
            success=success,
            strategy=strategy,
            url=url,
            elapsed_time=elapsed_time,
            error=error,
        )

    final_url = response.url

    if hasattr(response, "status_code"):
        status_code = response.status_code

        content_type = response.headers.get(
            "Content-Type"
        )

    else:
        status_code = response.status

        content_type = response.headers.get(
            "content-type"
        )

    content_size = (
        len(
            css.encode(
                "utf-8",
                errors="ignore",
            )
        )
        if css
        else 0
    )

    content_hash = (
        _generate_content_hash(css)
        if css
        else None
    )

    return CSSRetrievalResult(
        success=success,
        strategy=strategy,
        url=url,
        final_url=final_url,
        css=css,
        status_code=status_code,
        content_type=content_type,
        content_size=content_size,
        content_hash=content_hash,
        elapsed_time=elapsed_time,
        error=error,
    )


def _retrieve_request(
    url: str,
    *,
    strategy: str,
    headers: Optional[Dict[str, str]] = None,
    session: Optional[requests.Session] = None,
    cookies: Optional[Dict[str, str]] = None,
    verify: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
) -> CSSRetrievalResult:
    """
    共用 HTTP CSS Retrieval。
    """

    start_time = time.perf_counter()

    request_headers = dict(DEFAULT_HEADERS)

    if headers:
        request_headers.update(headers)

    client = session or requests.Session()

    try:
        response = client.get(
            url,
            headers=request_headers,
            cookies=cookies,
            timeout=timeout,
            allow_redirects=True,
            verify=verify,
        )

        css = _fix_encoding(response)

        elapsed_time = time.perf_counter() - start_time

        if not _validate_css_response(response):
            return _build_result(
                success=False,
                strategy=strategy,
                url=url,
                response=response,
                css=css,
                elapsed_time=elapsed_time,
                error=(
                    "Response is not a valid CSS resource"
                ),
            )

        return _build_result(
            success=True,
            strategy=strategy,
            url=url,
            response=response,
            css=css,
            elapsed_time=elapsed_time,
        )

    except Exception as exc:
        elapsed_time = time.perf_counter() - start_time

        return CSSRetrievalResult(
            success=False,
            strategy=strategy,
            url=url,
            elapsed_time=elapsed_time,
            error=str(exc),
        )


def retrieve_css_http(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> CSSRetrievalResult:
    """
    R1.2 CSS Strategy 1

    HTTP

    一般 HTTP/HTTPS CSS 下載。
    """

    return _retrieve_request(
        url,
        strategy="http",
        timeout=timeout,
    )


def retrieve_css_session(
    url: str,
    *,
    session: Optional[requests.Session] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> CSSRetrievalResult:
    """
    R1.2 CSS Strategy 2

    Session

    使用 HTTP Session 維持 Cookie / Connection。
    """

    client = session or requests.Session()

    return _retrieve_request(
        url,
        strategy="session",
        session=client,
        timeout=timeout,
    )


def retrieve_css_referer(
    url: str,
    *,
    referer: Optional[str] = None,
    session: Optional[requests.Session] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> CSSRetrievalResult:
    """
    R1.2 CSS Strategy 3

    Referer

    加入 Referer Header。
    """

    headers = {}

    if referer:
        headers["Referer"] = referer

    return _retrieve_request(
        url,
        strategy="referer",
        headers=headers,
        session=session,
        timeout=timeout,
    )


def retrieve_css_cookie_session(
    url: str,
    *,
    cookies: Optional[Dict[str, str]] = None,
    session: Optional[requests.Session] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> CSSRetrievalResult:
    """
    R1.2 CSS Strategy 4

    Cookie Session

    使用指定 Cookie + Session。
    """

    client = session or requests.Session()

    if cookies:
        client.cookies.update(cookies)

    return _retrieve_request(
        url,
        strategy="cookie_session",
        session=client,
        timeout=timeout,
    )


def retrieve_css_ssl_fallback(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> CSSRetrievalResult:
    """
    R1.2 CSS Strategy 5

    SSL Fallback

    SSL 驗證失敗時使用 verify=False。
    """

    start_time = time.perf_counter()

    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
            verify=True,
        )

        css = _fix_encoding(response)

        elapsed_time = time.perf_counter() - start_time

        if not _validate_css_response(response):
            return _build_result(
                success=False,
                strategy="ssl_fallback",
                url=url,
                response=response,
                css=css,
                elapsed_time=elapsed_time,
                error=(
                    "Response is not a valid CSS resource"
                ),
            )

        return _build_result(
            success=True,
            strategy="ssl_fallback",
            url=url,
            response=response,
            css=css,
            elapsed_time=elapsed_time,
        )

    except SSLError:
        _mark_ssl_fallback_host(url)

        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning
        )

        result = _retrieve_request(
            url,
            strategy="ssl_fallback",
            verify=False,
            timeout=timeout,
        )

        return result

    except Exception as exc:
        elapsed_time = time.perf_counter() - start_time

        return CSSRetrievalResult(
            success=False,
            strategy="ssl_fallback",
            url=url,
            elapsed_time=elapsed_time,
            error=str(exc),
        )


def discover_css_from_html(
    html: str,
    *,
    base_url: str,
) -> CSSDiscoveryResult:
    """
    CSS Discovery Strategy

    從 HTML：

        <link rel="stylesheet">

    找出 CSS URL。

    同時取得：

        <style>

    中的 Inline CSS。
    """

    start_time = time.perf_counter()

    try:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        css_urls = []
        inline_css = []

        for link in soup.find_all("link"):
            rel = link.get("rel", [])

            if isinstance(rel, str):
                rel = [rel]

            rel = [
                str(value).lower()
                for value in rel
            ]

            if "stylesheet" not in rel:
                continue

            href = link.get("href")

            if not href:
                continue

            css_url = urljoin(
                base_url,
                href,
            )

            if css_url not in css_urls:
                css_urls.append(css_url)

        for style in soup.find_all("style"):
            content = style.get_text()

            if content.strip():
                inline_css.append(content)

        elapsed_time = (
            time.perf_counter() - start_time
        )

        return CSSDiscoveryResult(
            success=True,
            strategy="html_linked_css",
            base_url=base_url,
            css_urls=css_urls,
            inline_css=inline_css,
            import_urls=[],
            elapsed_time=elapsed_time,
        )

    except Exception as exc:
        return CSSDiscoveryResult(
            success=False,
            strategy="html_linked_css",
            base_url=base_url,
            css_urls=[],
            inline_css=[],
            import_urls=[],
            elapsed_time=(
                time.perf_counter() - start_time
            ),
            error=str(exc),
        )


def discover_css_imports(
    css: str,
    *,
    base_url: str,
) -> CSSDiscoveryResult:
    """
    CSS Discovery Strategy

    從 CSS 中找出：

        @import "..."
        @import url("...")
        @import url(...)

    """

    start_time = time.perf_counter()

    try:
        import_urls = []

        patterns = [
            r'@import\s+(?:url\(\s*)?["\']([^"\']+)["\']',
            r'@import\s+url\(\s*["\']?([^"\')\s]+)',
        ]

        for pattern in patterns:
            for match in re.findall(
                pattern,
                css,
                flags=re.IGNORECASE,
            ):
                import_url = urljoin(
                    base_url,
                    match.strip(),
                )

                if import_url not in import_urls:
                    import_urls.append(import_url)

        elapsed_time = (
            time.perf_counter() - start_time
        )

        return CSSDiscoveryResult(
            success=True,
            strategy="css_import",
            base_url=base_url,
            css_urls=[],
            inline_css=[],
            import_urls=import_urls,
            elapsed_time=elapsed_time,
        )

    except Exception as exc:
        return CSSDiscoveryResult(
            success=False,
            strategy="css_import",
            base_url=base_url,
            css_urls=[],
            inline_css=[],
            import_urls=[],
            elapsed_time=(
                time.perf_counter() - start_time
            ),
            error=str(exc),
        )


def retrieve_css_browser(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> CSSRetrievalResult:
    """
    R1.2 CSS Strategy 6

    Browser

    使用 Playwright + Chromium Headless
    取得 CSS Resource。

    Browser 使用 Headless 模式。
    """

    start_time = time.perf_counter()

    browser = None
    context = None

    try:
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=True,
            )

            context = browser.new_context(
                user_agent=DEFAULT_HEADERS[
                    "User-Agent"
                ],
                extra_http_headers={
                    "Accept": DEFAULT_HEADERS[
                        "Accept"
                    ],
                    "Accept-Language": DEFAULT_HEADERS[
                        "Accept-Language"
                    ],
                },
            )

            response = context.request.get(
                url,
                timeout=timeout * 1000,
                max_redirects=10,
            )

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            css = response.text()

            if not _validate_css_response(
                response
            ):
                return _build_result(
                    success=False,
                    strategy="browser",
                    url=url,
                    response=response,
                    css=css,
                    elapsed_time=elapsed_time,
                    error=(
                        "Response is not a valid "
                        "CSS resource"
                    ),
                )

            if not css or not css.strip():
                return _build_result(
                    success=False,
                    strategy="browser",
                    url=url,
                    response=response,
                    css=css,
                    elapsed_time=elapsed_time,
                    error="CSS is empty",
                )

            return _build_result(
                success=True,
                strategy="browser",
                url=url,
                response=response,
                css=css,
                elapsed_time=elapsed_time,
            )

    except PlaywrightTimeoutError as exc:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        return CSSRetrievalResult(
            success=False,
            strategy="browser",
            url=url,
            elapsed_time=elapsed_time,
            error=f"Browser timeout: {exc}",
        )

    except Exception as exc:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        return CSSRetrievalResult(
            success=False,
            strategy="browser",
            url=url,
            elapsed_time=elapsed_time,
            error=str(exc),
        )

    finally:

        if context is not None:
            try:
                context.dispose()
            except Exception:
                pass

        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass


CSS_RETRIEVAL_STRATEGIES = {
    "http": retrieve_css_http,
    "session": retrieve_css_session,
    "referer": retrieve_css_referer,
    "cookie_session": retrieve_css_cookie_session,
    "ssl_fallback": retrieve_css_ssl_fallback,
    "browser": retrieve_css_browser,
}


def get_css_retrieval_strategies():
    """
    取得 CSS Retrieval Strategies。
    """

    return dict(CSS_RETRIEVAL_STRATEGIES)


def retrieve_css(
    url: str,
    strategy: str = "http",
    **kwargs,
) -> CSSRetrievalResult:
    """
    依指定 Strategy 取得 CSS。
    """

    retrieval_strategy = (
        CSS_RETRIEVAL_STRATEGIES.get(strategy)
    )

    if retrieval_strategy is None:
        return CSSRetrievalResult(
            success=False,
            strategy=strategy,
            url=url,
            error=(
                f"Unknown CSS retrieval strategy: "
                f"{strategy}"
            ),
        )

    return retrieval_strategy(
        url,
        **kwargs,
    )


__all__ = [
    "CSSRetrievalResult",
    "CSSDiscoveryResult",
    "retrieve_css_http",
    "retrieve_css_session",
    "retrieve_css_referer",
    "retrieve_css_cookie_session",
    "retrieve_css_ssl_fallback",
    "retrieve_css_browser",
    "discover_css_from_html",
    "discover_css_imports",
    "get_css_retrieval_strategies",
    "retrieve_css",
]