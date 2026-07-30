"""
app/main.py

功能：

    AutoSearch_V2 主流程控制。


負責：

    1. 讀取搜尋關鍵字

    2. 呼叫搜尋模組

    3. 下載文章HTML

    4. 解析文章內容

    5. 輸出Excel


版本：

    V2.0
"""


# ======================================
# 匯入設定
# ======================================


# 搜尋關鍵字

from config.keywords import SEARCH_KEYWORDS


# 系統設定

from config.settings import (
    MAX_RESULTS,
    HEADERS
)



# ======================================
# 匯入功能模組
# ======================================


# 搜尋功能

from search.search_engine import search


# 網頁下載功能

from crawler.crawler import download


# HTML解析功能

from parser.parser import parse


# Excel輸出功能

from exporter.excel import export





def main():
    """
    AutoSearch_V2 主流程


    流程：

    關鍵字

        ↓

    搜尋文章

        ↓

    取得網址

        ↓

    下載HTML

        ↓

    解析內容

        ↓

    Article物件

        ↓

    Excel輸出


    Returns
    -------

    None
    """



    # ==================================
    # 建立文章列表
    #
    # 用來保存所有Article物件
    # ==================================

    articles = []



    # ==================================
    # 逐一搜尋關鍵字
    #
    # 例如：
    #
    # IC semiconductor
    # SerDes
    # HBM
    #
    # ==================================

    for keyword in SEARCH_KEYWORDS:


        print()

        print("=" * 50)

        print(
            f"開始搜尋：{keyword}"
        )

        print("=" * 50)



        # ==================================
        # 搜尋文章
        #
        # 回傳：
        #
        # [
        #   {
        #       title:"",
        #       url:"",
        #       published:""
        #   }
        # ]
        #
        # ==================================

        search_results = search(
            keyword,
            MAX_RESULTS
        )



        # ==================================
        # 逐篇處理搜尋結果
        # ==================================

        for item in search_results:


            print(
                "處理文章：",
                item["title"]
            )


            # ------------------------------
            # 取得文章網址
            # ------------------------------

            url = item["url"]



            # ------------------------------
            # 下載HTML
            # ------------------------------

            html = download(
                url,
                HEADERS
            )



            # ------------------------------
            # 下載失敗跳過
            # ------------------------------

            if html is None:

                continue



            # ------------------------------
            # 解析HTML
            #
            # 回傳：
            #
            # Article物件
            #
            # ------------------------------

            article = parse(
                html,
                keyword
            )



            # ------------------------------
            # 補充搜尋結果資料
            #
            # Article是class物件
            #
            # 使用：
            #
            # article.url
            #
            # 不是：
            #
            # article["url"]
            #
            # ------------------------------

            article.url = url



            # 搜尋結果有日期
            # 補入Article

            article.published = item.get(
                "published",
                ""
            )



            # ------------------------------
            # 加入文章列表
            # ------------------------------

            articles.append(
                article
            )



    # ======================================
    # 全部搜尋完成
    #
    # 輸出Excel
    # ======================================

    export(
        articles
    )



    print()

    print(
        "AutoSearch V2 完成"
    )



# ======================================
# 測試入口
# ======================================

if __name__ == "__main__":

    main()