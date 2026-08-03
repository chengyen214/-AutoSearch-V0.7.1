"""
app/main.py

AutoSearch_V3

P4.3

主流程控制


Pipeline:

Keyword

↓

Search

↓

Download HTML

↓

Parser

↓

Article

↓

AI Analyzer

↓

AIAnalysis

↓

MySQL

↓

Excel

"""



# ======================================
# Config
# ======================================


from config.keywords import SEARCH_KEYWORDS


from config.settings import (
    MAX_RESULTS,
    HEADERS
)




# ======================================
# Database
# ======================================


from database.article_repository import (
    ArticleRepository
)





# ======================================
# AI
# ======================================


from ai.analyzer import (
    AIAnalyzer
)


from models.ai_analysis import (
    AIAnalysis
)






# ======================================
# Core Modules
# ======================================


from search.search_engine import search


from crawler.crawler import download


from parser.parser import parse


from exporter.excel import export







# ======================================
# Utils
# ======================================


from utils.hash import (
    generate_hash
)


from utils.duplicate import (
    is_duplicate,
    save_document
)


from utils.history import (
    save_history
)


from utils.logger import logger










def main():



    logger.info(
        "========== AutoSearch V3 Start =========="
    )



    articles = []



    repo = ArticleRepository()



    ai_analyzer = AIAnalyzer()







    try:



        # ==================================
        # Keyword Loop
        # ==================================


        for keyword in SEARCH_KEYWORDS:



            logger.info(

                f"開始搜尋：{keyword}"

            )



            search_results = search(

                keyword,

                MAX_RESULTS

            )



            new_count = 0

            duplicate_count = 0

            failed_count = 0







            # ==================================
            # Article Loop
            # ==================================


            for item in search_results:



                try:



                    logger.info(

                        f"處理文章：{item.title}"

                    )



                    url = item.url






                    # ==========================
                    # Download
                    # ==========================


                    html = download(

                        url,

                        HEADERS

                    )



                    if html is None:



                        failed_count += 1


                        logger.warning(

                            f"Download failed: {url}"

                        )


                        continue







                    # ==========================
                    # Parser
                    # ==========================


                    article = parse(

                        html,

                        keyword

                    )



                    if article is None:



                        failed_count += 1


                        continue







                    # ==========================
                    # Search Metadata
                    # ==========================


                    article.keyword = item.keyword


                    article.title = item.title


                    article.url = item.url


                    article.published = item.published


                    article.source = item.source


                    article.status = "Success"








                    # ==========================
                    # Document ID
                    # ==========================


                    article.document_id = generate_hash(

                        article.title,

                        article.content

                    )









                    # ==========================
                    # Duplicate
                    # ==========================


                    if is_duplicate(

                        article.document_id

                    ):



                        duplicate_count += 1



                        logger.info(

                            f"Duplicate: {article.title}"

                        )


                        continue







                    save_document(

                        article.document_id

                    )


                    new_count += 1











                    # ==========================
                    # AI Analysis P4.3
                    #
                    # 修正:
                    #
                    # 傳入 article.content
                    #
                    # ==========================


                    try:



                        analysis = ai_analyzer.analyze(

                            article.content

                        )



                        article.ai_analysis = analysis






                        # Debug

                        print()

                        print(
                            "========== AI RESULT =========="
                        )

                        print(

                            article.ai_analysis.to_dict()

                        )

                        print(
                            "=============================="
                        )

                        print()





                        logger.info(

                            f"AI完成: {article.ai_analysis.category}"

                        )






                    except Exception as e:



                        logger.error(

                            f"AI Analysis Error: {e}"

                        )


                        article.ai_analysis = AIAnalysis()












                    # ==========================
                    # Database
                    # ==========================


                    result = repo.save(

                        article

                    )


                    logger.info(

                        f"Database Save: {result}"

                    )



                    articles.append(

                        article

                    )







                except Exception as e:



                    failed_count += 1


                    logger.exception(e)












            # ==================================
            # History
            # ==================================


            save_history(

                keyword,

                len(search_results),

                new_count,

                duplicate_count,

                failed_count

            )









    finally:



        repo.close()










    # ======================================
    # Excel Export
    # ======================================


    if articles:



        export(

            articles

        )





    logger.info(

        "========== AutoSearch V3 Finish =========="

    )













if __name__ == "__main__":


    main()