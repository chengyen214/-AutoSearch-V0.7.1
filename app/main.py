"""
app/main.py

AutoSearch V4

P2.2.6 Async AI Pipeline

Pipeline:

Keyword
↓
ArticleService
↓
Search
↓
Download HTML
↓
Parser
↓
ArticleRepository
↓
articles
↓
AITaskRepository
↓
ai_tasks WAITING
↓
AI Scheduler
↓
AI Worker
↓
AI Analysis
↓
Knowledge Archive
↓
Knowledge Intelligence
↓
Search Index
↓
ai_tasks DONE

"""


# ======================================
# Config
# ======================================

from config.keywords import SEARCH_KEYWORDS


# ======================================
# Services
# ======================================

from services.article_service import ArticleService

from services.ai_scheduler import AIScheduler

from services.knowledge_intelligence_service import (
    KnowledgeIntelligenceService
)


# ======================================
# Export
# ======================================

from exporter.excel import export


# ======================================
# Utils
# ======================================

from utils.history import save_history

from utils.logger import logger



class AutoSearchApplication:


    def __init__(self):


        # Article Pipeline

        self.article_service = (
            ArticleService()
        )


        # AI Pipeline

        self.ai_scheduler = (
            AIScheduler()
        )


        # Knowledge Layer

        self.knowledge_service = (
            KnowledgeIntelligenceService()
        )



    # ==================================
    #
    # Main Pipeline
    #
    # ==================================

    def run(self):


        logger.info(
            "========== AutoSearch V4 Start =========="
        )


        articles = []



        try:



            # ==================================
            #
            # Step 1
            #
            # Article Collection
            #
            # Search
            # Crawl
            # Parser
            # Save Article
            # Create AI Task
            #
            # ==================================


            for keyword in SEARCH_KEYWORDS:


                logger.info(
                    f"開始搜尋：{keyword}"
                )



                result = (
                    self.article_service.create(
                        keyword
                    )
                )



                if result:


                    articles.extend(
                        result["articles"]
                    )



                save_history(

                    keyword,

                    result.get(
                        "total",
                        0
                    ),

                    result.get(
                        "new",
                        0
                    ),

                    result.get(
                        "duplicate",
                        0
                    ),

                    result.get(
                        "failed",
                        0
                    )

                )



            logger.info(

                f"Articles collected={len(articles)}"

            )





            # ==================================
            #
            # Step 2
            #
            # Async AI Pipeline
            #
            # ai_tasks WAITING
            #
            # ==================================


            logger.info(

                "Start Async AI Pipeline"

            )


            ai_result = (

                self.ai_scheduler
                .run_once()

            )


            logger.info(

                f"AI Pipeline finished={ai_result}"

            )






            # ==================================
            #
            # Step 3
            #
            # Knowledge Intelligence
            #
            # ==================================


            logger.info(

                "Start Knowledge Intelligence"

            )


            self.knowledge_service.run()



            logger.info(

                "Knowledge Intelligence finished"

            )





        except Exception as e:


            logger.exception(e)




        finally:



            logger.info(

                "========== AutoSearch V4 Finish =========="

            )





        # ==================================
        #
        # Export
        #
        # ==================================


        if articles:


            export(

                articles

            )



        return articles






# ======================================
#
# Backward Compatible Entry
#
# ======================================


def main():


    app = AutoSearchApplication()


    app.run()





if __name__ == "__main__":


    main()