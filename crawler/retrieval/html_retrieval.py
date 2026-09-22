"""
html_retrieval.py

AutoSearch V5

R1.1 HTML Retrieval

用途：

    提供多種 HTML Retrieval Strategy，
    讓 R2 Site Profile 可以逐一測試：

        Completeness
        Speed

    再選擇最佳 HTML Retrieval Strategy。

HTML Retrieval Strategy：

    1. HTTP
    2. HTTP Session
    3. HTTP SSL Fallback
    4. HTTP Referer
    5. HTTP Cookie Session
    6. Browser

注意：

    本模組只負責 HTML Retrieval。

    不負責：

        CSS Retrieval
        Image Retrieval
        Site Profile
        MongoDB
        CrawlResult
        Parser
        Archive
        AI

    本模組不處理：

        CAPTCHA bypass
        Login bypass
        Access-control bypass
        其他網站存取限制繞過
"""

import time

from dataclasses import dataclass
from typing import Optional

from urllib.parse import urlparse

import requests
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from urllib3.exceptions import (
    InsecureRequestWarning,
)

import urllib3

from config.settings import (
    TIMEOUT,
    CRAWL_DELAY,
)


DEFAULT_HEADERS = {
    "User-Agent":
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120 Safari/537.36"
        ),
    "Accept":
        (
            "text/html,"
            "application/xhtml+xml,"
            "application/xml;q=0.9,"
            "image/avif,image/webp,"
            "*/*;q=0.8"
        ),
    "Accept-Language":
        "zh-TW,zh;q=0.9,en;q=0.8",
    "Connection":
        "keep-alive",
}


REFERER_HEADERS = {
    **DEFAULT_HEADERS,
    "Referer":
        "https://www.google.com/",
}


_SSL_FALLBACK_HOSTS = set()


@dataclass
class HTMLRetrievalResult:
    """
    HTML Retrieval 結果。

    R2 可以使用：

        success
        strategy
        status_code
        content_size
        elapsed_time

    進行 Strategy Evaluation。
    """

    success: bool

    strategy: str

    url: str

    final_url: Optional[str] = None

    html: Optional[str] = None

    status_code: Optional[int] = None

    content_type: Optional[str] = None

    content_size: int = 0

    elapsed_time: float = 0.0

    error: Optional[str] = None


def _get_hostname(
    url,
):
    """
    取得 URL Host。
    """

    if not url:
        return None

    try:
        hostname = urlparse(
            str(url)
        ).hostname

    except Exception:
        return None

    if not hostname:
        return None

    return hostname.lower()


def _is_ssl_fallback_host(
    url,
):
    """
    判斷 Host 是否已進入 SSL fallback cache。
    """

    hostname = _get_hostname(
        url
    )

    if not hostname:
        return False

    return (
        hostname
        in _SSL_FALLBACK_HOSTS
    )


def _mark_ssl_fallback_host(
    url,
):
    """
    將 Host 加入 SSL fallback cache。
    """

    hostname = _get_hostname(
        url
    )

    if not hostname:
        return

    _SSL_FALLBACK_HOSTS.add(
        hostname
    )


def clear_ssl_fallback_cache():
    """
    清除 SSL fallback cache。

    主要提供：

        Test
        Debug
    """

    _SSL_FALLBACK_HOSTS.clear()


def _disable_ssl_warning():
    """
    停用 verify=False 時的 SSL Warning。
    """

    urllib3.disable_warnings(
        InsecureRequestWarning
    )


def _fix_encoding(
    response,
):
    """
    修正 HTTP Response Encoding。
    """

    encoding = response.apparent_encoding

    if encoding:
        response.encoding = encoding

    return response.text


def _validate_html_response(
    response,
):
    """
    基本 HTML Response Validation。

    注意：

        這裡只做 Retrieval 層的基本驗證。

        Site Profile 的 Completeness Evaluation
        由 R2 負責。
    """

    content_type = response.headers.get(
        "Content-Type",
        "",
    )

    if (
        "text/html"
        not in content_type.lower()
        and
        "application/xhtml+xml"
        not in content_type.lower()
    ):
        return (
            False,
            "Response is not HTML",
        )

    return (
        True,
        None,
    )


def _build_result(
    *,
    success,
    strategy,
    url,
    start_time,
    response=None,
    html=None,
    error=None,
):
    """
    建立 HTMLRetrievalResult。
    """

    elapsed_time = (
        time.perf_counter()
        - start_time
    )

    if response is None:
        return HTMLRetrievalResult(
            success=success,
            strategy=strategy,
            url=url,
            elapsed_time=elapsed_time,
            error=error,
        )

    content_type = response.headers.get(
        "Content-Type",
        "",
    )

    content_size = 0

    if html:
        content_size = len(
            html.encode(
                "utf-8"
            )
        )

    return HTMLRetrievalResult(
        success=success,
        strategy=strategy,
        url=url,
        final_url=response.url,
        html=html,
        status_code=response.status_code,
        content_type=content_type,
        content_size=content_size,
        elapsed_time=elapsed_time,
        error=error,
    )


def _request(
    url,
    headers,
    *,
    session=None,
    verify=True,
):
    """
    執行 HTTP Request。
    """

    if not verify:
        _disable_ssl_warning()

    requester = (
        session
        if session is not None
        else requests
    )

    response = requester.get(
        url,
        headers=headers,
        allow_redirects=True,
        timeout=TIMEOUT,
        verify=verify,
    )

    response.raise_for_status()

    return response


def _retrieve_http(
    url,
    headers,
    *,
    strategy,
    session=None,
    verify=True,
    retry=3,
):
    """
    共用 HTTP HTML Retrieval。
    """

    start_time = time.perf_counter()

    last_error = None

    for attempt in range(
        retry
    ):
        try:
            response = _request(
                url,
                headers,
                session=session,
                verify=verify,
            )

            valid, validation_error = (
                _validate_html_response(
                    response
                )
            )

            if not valid:
                return _build_result(
                    success=False,
                    strategy=strategy,
                    url=url,
                    start_time=start_time,
                    response=response,
                    error=validation_error,
                )

            html = _fix_encoding(
                response
            )

            if not html or not html.strip():
                return _build_result(
                    success=False,
                    strategy=strategy,
                    url=url,
                    start_time=start_time,
                    response=response,
                    error="HTML is empty",
                )

            result = _build_result(
                success=True,
                strategy=strategy,
                url=url,
                start_time=start_time,
                response=response,
                html=html,
            )

            time.sleep(
                CRAWL_DELAY
            )

            return result

        except requests.exceptions.SSLError as error:

            last_error = str(
                error
            )

            if verify:
                try:
                    _mark_ssl_fallback_host(
                        url
                    )

                    return _retrieve_http(
                        url,
                        headers,
                        strategy=(
                            f"{strategy}_ssl_fallback"
                        ),
                        session=session,
                        verify=False,
                        retry=retry,
                    )

                except Exception as fallback_error:
                    last_error = str(
                        fallback_error
                    )

        except requests.RequestException as error:

            last_error = str(
                error
            )

        if attempt < retry - 1:
            time.sleep(
                2
            )

    return _build_result(
        success=False,
        strategy=strategy,
        url=url,
        start_time=start_time,
        error=last_error,
    )


def retrieve_html_http(
    url,
    headers=None,
    retry=3,
):
    """
    Strategy：

        HTTP

    一般 HTTP HTML Retrieval。
    """

    if headers is None:
        headers = DEFAULT_HEADERS

    verify = not _is_ssl_fallback_host(
        url
    )

    return _retrieve_http(
        url,
        headers,
        strategy="http",
        verify=verify,
        retry=retry,
    )


def retrieve_html_session(
    url,
    headers=None,
    retry=3,
):
    """
    Strategy：

        HTTP Session

    使用 requests.Session()
    保留 Cookie 與 Connection。
    """

    if headers is None:
        headers = DEFAULT_HEADERS

    start_time = time.perf_counter()

    session = requests.Session()

    try:
        verify = not _is_ssl_fallback_host(
            url
        )

        return _retrieve_http(
            url,
            headers,
            strategy="session",
            session=session,
            verify=verify,
            retry=retry,
        )

    finally:
        session.close()


def retrieve_html_referer(
    url,
    headers=None,
    retry=3,
):
    """
    Strategy：

        HTTP Referer

    使用 Referer Header 進行正常 HTTP Retrieval。
    """

    if headers is None:
        headers = REFERER_HEADERS

    else:
        headers = {
            **headers,
            "Referer":
                "https://www.google.com/",
        }

    verify = not _is_ssl_fallback_host(
        url
    )

    return _retrieve_http(
        url,
        headers,
        strategy="referer",
        verify=verify,
        retry=retry,
    )


def retrieve_html_cookie_session(
    url,
    headers=None,
    cookies=None,
    retry=3,
):
    """
    Strategy：

        Cookie Session

    使用 Session + Cookie。
    """

    if headers is None:
        headers = DEFAULT_HEADERS

    start_time = time.perf_counter()

    session = requests.Session()

    try:
        if cookies:
            session.cookies.update(
                cookies
            )

        verify = not _is_ssl_fallback_host(
            url
        )

        return _retrieve_http(
            url,
            headers,
            strategy="cookie_session",
            session=session,
            verify=verify,
            retry=retry,
        )

    finally:
        session.close()


def retrieve_html_ssl_fallback(
    url,
    headers=None,
    retry=3,
):
    """
    Strategy：

        SSL Fallback

    使用 verify=False 取得因憑證問題無法正常取得的 HTML。

    注意：

        僅處理 TLS Certificate Verification
        問題，不繞過網站其他存取限制。
    """

    if headers is None:
        headers = DEFAULT_HEADERS

    _mark_ssl_fallback_host(
        url
    )

    return _retrieve_http(
        url,
        headers,
        strategy="ssl_fallback",
        verify=False,
        retry=retry,
    )


def retrieve_html_browser(
    url,
    headers=None,
):
    """
    Strategy：

        Browser

    使用 Playwright + Chromium Headless
    執行 JavaScript 後取得 Rendered HTML。

    注意：

        Browser 使用 Headless 模式。
        不開啟可見瀏覽器視窗。

        本策略只負責正常 Browser Retrieval，
        不處理：

            CAPTCHA bypass
            Login bypass
            Access-control bypass
            其他網站存取限制繞過
    """

    start_time = time.perf_counter()

    if headers is None:
        headers = DEFAULT_HEADERS

    browser = None

    try:
        browser_headers = dict(
            headers
        )

        user_agent = browser_headers.pop(
            "User-Agent",
            None,
        )

        browser_headers.pop(
            "Connection",
            None,
        )

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=True,
            )

            context_kwargs = {
                "extra_http_headers":
                    browser_headers,
            }

            if user_agent:
                context_kwargs[
                    "user_agent"
                ] = user_agent

            context = browser.new_context(
                **context_kwargs
            )

            page = context.new_page()

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=int(
                    TIMEOUT * 1000
                ),
            )

            page.wait_for_load_state(
                "load",
                timeout=int(
                    TIMEOUT * 1000
                ),
            )

            html = page.content()

            final_url = page.url

            status_code = None
            content_type = "text/html"

            if response is not None:
                status_code = response.status

                response_content_type = (
                    response.headers.get(
                        "content-type"
                    )
                )

                if response_content_type:
                    content_type = (
                        response_content_type
                    )

            if not html or not html.strip():
                elapsed_time = (
                    time.perf_counter()
                    - start_time
                )

                return HTMLRetrievalResult(
                    success=False,
                    strategy="browser",
                    url=url,
                    final_url=final_url,
                    status_code=status_code,
                    content_type=content_type,
                    content_size=0,
                    elapsed_time=elapsed_time,
                    error="Rendered HTML is empty",
                )

            content_size = len(
                html.encode(
                    "utf-8"
                )
            )

            elapsed_time = (
                time.perf_counter()
                - start_time
            )

            result = HTMLRetrievalResult(
                success=True,
                strategy="browser",
                url=url,
                final_url=final_url,
                html=html,
                status_code=status_code,
                content_type=content_type,
                content_size=content_size,
                elapsed_time=elapsed_time,
                error=None,
            )

            time.sleep(
                CRAWL_DELAY
            )

            context.close()

            return result

    except PlaywrightTimeoutError as error:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        return HTMLRetrievalResult(
            success=False,
            strategy="browser",
            url=url,
            elapsed_time=elapsed_time,
            error=(
                f"Browser timeout: {error}"
            ),
        )

    except Exception as error:

        elapsed_time = (
            time.perf_counter()
            - start_time
        )

        return HTMLRetrievalResult(
            success=False,
            strategy="browser",
            url=url,
            elapsed_time=elapsed_time,
            error=str(error),
        )

    finally:

        if browser is not None:
            try:
                browser.close()

            except Exception:
                pass


HTML_RETRIEVAL_STRATEGIES = {
    "http":
        retrieve_html_http,

    "session":
        retrieve_html_session,

    "referer":
        retrieve_html_referer,

    "cookie_session":
        retrieve_html_cookie_session,

    "ssl_fallback":
        retrieve_html_ssl_fallback,

    "browser":
        retrieve_html_browser,
}


def get_html_retrieval_strategies():
    """
    取得目前所有 HTML Retrieval Strategies。

    R2 Site Profile 可以使用此函式
    進行 Strategy Probe。
    """

    return dict(
        HTML_RETRIEVAL_STRATEGIES
    )


def retrieve_html(
    url,
    strategy="http",
    headers=None,
    retry=3,
):
    """
    使用指定 Strategy 取得 HTML。
    """

    retrieval = (
        HTML_RETRIEVAL_STRATEGIES.get(
            strategy
        )
    )

    if retrieval is None:
        return HTMLRetrievalResult(
            success=False,
            strategy=strategy,
            url=url,
            error=(
                f"Unknown HTML Retrieval "
                f"Strategy: {strategy}"
            ),
        )

    if strategy == "browser":
        return retrieval(
            url,
            headers=headers,
        )

    return retrieval(
        url,
        headers=headers,
        retry=retry,
    )


__all__ = [
    "DEFAULT_HEADERS",
    "HTMLRetrievalResult",
    "HTML_RETRIEVAL_STRATEGIES",
    "clear_ssl_fallback_cache",
    "get_html_retrieval_strategies",
    "retrieve_html",
    "retrieve_html_http",
    "retrieve_html_session",
    "retrieve_html_referer",
    "retrieve_html_cookie_session",
    "retrieve_html_ssl_fallback",
    "retrieve_html_browser",
]