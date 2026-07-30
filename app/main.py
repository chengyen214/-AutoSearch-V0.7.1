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

    V2.1 P5
"""



# ======================================
# 匯入設定
# ======================================

from config.keywords import SEARCH_KEYWORDS


from config.settings import (
    MAX_RESULTS,
    HEADERS
)



# ======================================
# 匯入功能模組
# ======================================


from search.search_engine import search


from crawler.crawler import download


from parser.parser import parse


from exporter.excel import export

from utils.hash import generate_hash

from utils.duplicate import (
    is_duplicate,
    save_document
)

from utils.history import save_history


def main():

    """
    AutoSearch_V2 主流程


    流程：

    Keyword

        ↓

    Search

        ↓

    Article

        ↓

    Download HTML

        ↓

    Parser

        ↓

    Cleaner

        ↓

    Export Excel
    """



    # 保存所有 Article

    articles = []



    # ==================================
    # 逐一搜尋關鍵字
    # ==================================

    for keyword in SEARCH_KEYWORDS:



        print()

        print("=" * 50)

        print(
            f"開始搜尋：{keyword}"
        )

        print("=" * 50)



        # ==================================
        # 搜尋
        #
        # 回傳:
        #
        # list[Article]
        #
        # ==================================

        search_results = search(

            keyword,

            MAX_RESULTS

        )

        new_count = 0

        duplicate_count = 0
        
        failed_count = 0


        # ==================================
        # 處理每篇文章
        # ==================================

        for item in search_results:



            print(
                "處理文章：",
                item.title
            )



            # ------------------------------
            # 取得網址
            # ------------------------------

            url = item.url



            # ------------------------------
            # 下載HTML
            # ------------------------------

            html = download(

                url,

                HEADERS

            )



            # ------------------------------
            # 下載失敗
            # ------------------------------

            if html is None:


                item.status = "Failed"

                item.error = "Download failed"
                failed_count += 1

                articles.append(

                    item

                )


                continue



            # ------------------------------
            # HTML解析
            #
            # 回傳 Article
            #
            # ------------------------------

            article = parse(

                html,

                keyword

            )
            
            article.document_id = generate_hash(
                article.title,
                article.content
            )   
            
            if is_duplicate(
                article.document_id
            ):

                print(
                    "重複資料，跳過：",
                    article.title
                )
                
                duplicate_count += 1

                continue



            save_document(
                article.document_id
            )
            
            new_count += 1


            # ------------------------------
            # 保留搜尋資料
            #
            # 因 parser 不一定知道
            # Google News資料
            #
            # ------------------------------

            article.keyword = item.keyword


            article.title = item.title


            article.url = item.url


            article.published = item.published


            article.source = item.source



            article.status = "Success"



            # ------------------------------
            # 加入結果
            # ------------------------------

            articles.append(

                article

            )
        
        
        save_history(

            keyword,

            len(search_results),

            new_count,

            duplicate_count,
            
            failed_count

        )


    # ======================================
    # Excel輸出
    # ======================================

    export(

        articles

    )



    print()

    print(
        "AutoSearch V2 完成"
    )





# ======================================
# 程式入口
# ======================================

if __name__ == "__main__":

    main()