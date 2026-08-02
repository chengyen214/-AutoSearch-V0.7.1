"""
crawler.py

AutoSearch V2.2 P1

Web Downloader

功能:

1. requests下載
2. timeout
3. retry
4. delay
5. redirect
6. encoding修正

"""


import time
import requests


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
# Resolve Redirect URL
# =====================================

def resolve_url(url, headers=None):
    """
    取得真正新聞網址

    處理:
    - Google redirect
    - 新聞轉址
    - 短網址

    """


    try:


        if headers is None:

            headers = DEFAULT_HEADERS



        response = requests.get(

            url,

            headers=headers,

            allow_redirects=True,

            timeout=10

        )


        return response.url



    except requests.RequestException:


        return url




# =====================================
# Encoding Fix
# =====================================

def fix_encoding(response):
    """
    修正網站編碼

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
# Download HTML
# =====================================

def download(url, headers=None, retry=3):
    """
    下載HTML

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



    # 先解析redirect

    url = resolve_url(

        url,

        headers

    )



    for count in range(retry):


        try:


            response = requests.get(

                url,

                headers=headers,

                timeout=TIMEOUT

            )



            # HTTP錯誤

            response.raise_for_status()




            # -------------------------
            # HTML檢查
            # -------------------------

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




            # -------------------------
            # Encoding修正
            # -------------------------

            html = fix_encoding(

                response

            )




            # -------------------------
            # Delay
            # -------------------------

            time.sleep(

                CRAWL_DELAY

            )



            return html




        except requests.RequestException as e:



            print(

                f"下載失敗 {count + 1}/{retry}"

            )


            print(e)



            time.sleep(2)




    return None