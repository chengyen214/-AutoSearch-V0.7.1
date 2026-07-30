"""
crawler.py

負責下載網頁內容

功能：
1. requests下載
2. timeout
3. retry
4. delay
"""

import time
import requests

from config.settings import (
    TIMEOUT,
    CRAWL_DELAY
)

def resolve_url(url):
    """
    嘗試取得真正新聞網址
    """

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            allow_redirects=True,
            timeout=5
        )

        return response.url


    except requests.RequestException:

        return url

def download(url, headers, retry=3):
    """
    下載HTML

    url:
        網頁網址

    headers:
        HTTP Header

    retry:
        失敗重試次數
    """
    # url = "https://test-error-url-123456789.com" #test
    url = resolve_url(url)


    for count in range(retry):

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=TIMEOUT
            )

            response.raise_for_status()

            time.sleep(
                CRAWL_DELAY
            )

            return response.text


        except requests.RequestException as e:

            print(
                f"下載失敗 {count + 1}/{retry}"
            )

            print(e)

            time.sleep(1)


    return None