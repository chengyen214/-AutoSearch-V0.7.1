"""
crawler.py

AutoSearch V2.2 P1
AutoSearch V5 compatible

Web Downloader

功能:

1. requests下載
2. timeout
3. retry
4. delay
5. redirect
6. encoding修正
7. SSL Certificate Error fallback
"""


import time

import requests

from urllib3.exceptions import InsecureRequestWarning
import urllib3


from config.settings import (
    TIMEOUT,
    CRAWL_DELAY
)


# =====================================
# Default Headers
# =====================================

DEFAULT_HEADERS = {

    "User-Agent":
    (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    ),

    "Accept-Language":
    "zh-TW,zh;q=0.9,en;q=0.8"

}


# =====================================
# SSL Warning
# =====================================

def _disable_ssl_warning():
    """
    停用 urllib3 的
    InsecureRequestWarning。

    只在 SSL fallback
    verify=False 時使用。
    """

    urllib3.disable_warnings(
        InsecureRequestWarning
    )


# =====================================
# Resolve Redirect URL
# =====================================

def resolve_url(
    url,
    headers=None
):
    """
    取得真正新聞網址。

    處理:

    - Google redirect
    - 新聞轉址
    - 短網址

    SSL:

    1. 正常 verify=True
    2. SSL Certificate Error
       → verify=False fallback
    """

    try:

        if headers is None:

            headers = DEFAULT_HEADERS


        # ---------------------------------
        # Normal Redirect
        # ---------------------------------

        response = requests.get(

            url,

            headers=headers,

            allow_redirects=True,

            timeout=10,

            verify=True

        )


        return response.url


    except requests.exceptions.SSLError as e:

        print(
            "SSL 憑證驗證失敗，"
            "Resolve URL 啟用 SSL fallback:"
        )

        print(e)


        try:

            _disable_ssl_warning()


            response = requests.get(

                url,

                headers=headers,

                allow_redirects=True,

                timeout=10,

                verify=False

            )


            print(
                "SSL fallback redirect 成功"
            )


            return response.url


        except requests.RequestException as fallback_error:

            print(
                "SSL fallback redirect 失敗:"
            )

            print(
                fallback_error
            )


            return url


    except requests.RequestException:

        return url


# =====================================
# Encoding Fix
# =====================================

def fix_encoding(response):
    """
    修正網站編碼。

    避免:

        UTF-8
        ↓
        ISO-8859-1
        ↓
        中文亂碼
    """

    encoding = response.apparent_encoding


    if encoding:

        response.encoding = encoding


    return response.text


# =====================================
# Normal HTTPS Request
# =====================================

def _download_request(
    url,
    headers
):
    """
    正常 HTTPS Download。

    使用:

        verify=True

    SSL 錯誤會交由上層
    進行 fallback。
    """

    response = requests.get(

        url,

        headers=headers,

        timeout=TIMEOUT,

        verify=True

    )


    response.raise_for_status()


    return response


# =====================================
# SSL Fallback Request
# =====================================

def _download_ssl_fallback(
    url,
    headers
):
    """
    SSL Certificate Error fallback。

    使用:

        verify=False

    注意:

        只有正常 SSL 驗證失敗
        時才會進入這裡。
    """

    print(
        "啟用 SSL fallback:"
    )

    print(
        f"URL: {url}"
    )


    _disable_ssl_warning()


    response = requests.get(

        url,

        headers=headers,

        timeout=TIMEOUT,

        verify=False

    )


    response.raise_for_status()


    return response


# =====================================
# Download HTML
# =====================================

def download(
    url,
    headers=None,
    retry=3
):
    """
    下載 HTML。

    Download Strategy:

        1. 正常 HTTPS
        2. SSL Certificate Error
           ↓
           SSL fallback
        3. Retry
        4. 最終失敗 → None

    Parameters
    ----------

    url:
        網頁網址

    headers:
        HTTP Header

    retry:
        重試次數

    Returns
    -------

    html:
        HTML文字

    None:
        下載失敗
    """


    if headers is None:

        headers = DEFAULT_HEADERS


    # =================================
    # Resolve Redirect
    # =================================

    url = resolve_url(

        url,

        headers

    )


    # =================================
    # Download
    # =================================

    for count in range(retry):

        try:

            # ---------------------------------
            # Normal HTTPS
            # ---------------------------------

            try:

                response = _download_request(

                    url,

                    headers

                )


            except requests.exceptions.SSLError as ssl_error:

                # ---------------------------------
                # SSL Certificate Error
                # ---------------------------------

                print(
                    "SSL 憑證驗證失敗:"
                )

                print(
                    ssl_error
                )

                print(
                    "嘗試 SSL fallback..."
                )


                try:

                    response = _download_ssl_fallback(

                        url,

                        headers

                    )


                    print(
                        "SSL fallback 成功"
                    )


                except requests.RequestException as fallback_error:

                    print(
                        "SSL fallback 失敗:"
                    )

                    print(
                        fallback_error
                    )


                    # 交給外層 retry

                    raise fallback_error


            # ---------------------------------
            # HTML Check
            # ---------------------------------

            content_type = response.headers.get(

                "Content-Type",

                ""

            )


            if "text/html" not in content_type.lower():

                print(

                    "非HTML頁面:",

                    content_type

                )

                return None


            # ---------------------------------
            # Encoding Fix
            # ---------------------------------

            html = fix_encoding(

                response

            )


            # ---------------------------------
            # Empty HTML
            # ---------------------------------

            if not html.strip():

                print(
                    "下載HTML為空"
                )

                return None


            # ---------------------------------
            # Delay
            # ---------------------------------

            time.sleep(

                CRAWL_DELAY

            )


            # ---------------------------------
            # Success
            # ---------------------------------

            return html


        except requests.RequestException as e:

            print(

                f"下載失敗 "
                f"{count + 1}/{retry}"

            )

            print(e)


            if count < retry - 1:

                time.sleep(2)


    # =================================
    # Final Failure
    # =================================

    return None