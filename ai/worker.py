"""
ai/worker.py

AutoSearch V4

P2.2.6 Async AI Pipeline

Pipeline:

AITask
|
v
Article
|
v
AI Analysis
|
v
Knowledge Model
|
v
KnowledgeService
|
v
KnowledgeIntelligenceService
|
+--> knowledge_archive
+--> knowledge_scores
+--> search_index
|
v
Task DONE

"""

from database.article_repository import (
    ArticleRepository
)

from database.ai_task_repository import (
    AITaskRepository
)

from services.ai_analysis_service import (
    AIAnalysisService
)

from services.knowledge_service import (
    KnowledgeService
)

from services.knowledge_intelligence_service import (
    KnowledgeIntelligenceService
)

from models.knowledge import Knowledge

from utils.logger import logger



class AIWorker:



    def __init__(self):


        self.article_repository = (
            ArticleRepository()
        )


        self.task_repository = (
            AITaskRepository()
        )


        self.ai_service = (
            AIAnalysisService()
        )


        self.knowledge_service = (
            KnowledgeService()
        )


        self.knowledge_intelligence = (
            KnowledgeIntelligenceService()
        )





    # ==================================
    #
    # Process Task
    #
    # ==================================


    def process_task(
        self,
        task
    ):


        article = None


        try:


            logger.info(
                f"Processing AI task={task.id}"
            )



            # ------------------------------
            # Task Running
            # ------------------------------


            self.task_repository.mark_running(
                task.id
            )





            # ------------------------------
            # Load Article
            # ------------------------------


            article = (

                self.article_repository
                .find_model_by_id(

                    task.article_id

                )

            )



            if article is None:


                raise Exception(

                    f"Article not found id={task.article_id}"

                )






            self.article_repository.update_ai_status(

                article.id,

                "processing"

            )







            # ------------------------------
            #
            # AI Analysis
            #
            # ------------------------------


            analysis = (

                self.ai_service.analyze(

                    article

                )

            )



            if analysis is None:


                raise Exception(

                    "AI Analysis failed"

                )







            # ------------------------------
            #
            # Save AI Result
            #
            # AIAnalysis
            #
            # ->
            #
            # articles
            #
            # ------------------------------


            article.ai_analysis = analysis



            result = (

                self.article_repository
                .update_ai_analysis(

                    article

                )

            )



            if not result:


                raise Exception(

                    "Save AI Analysis failed"

                )







            # ------------------------------
            #
            # AIAnalysis
            #
            # ->
            #
            # Knowledge
            #
            # ------------------------------



            knowledge = Knowledge(



                article_id=article.id,



                topic=getattr(

                    analysis,

                    "category",

                    ""

                ),



                entities=getattr(

                    analysis,

                    "entities",

                    []

                ),



                relations=getattr(

                    analysis,

                    "relations",

                    []

                ),



                knowledge_version="1.0"


            )








            # ------------------------------
            #
            # Save Knowledge
            #
            # knowledge_archive
            #
            # search_index
            #
            # ------------------------------


            knowledge = (

                self.knowledge_service
                .create_with_index(

                    knowledge

                )

            )




            if knowledge is None:


                raise Exception(

                    "Knowledge create failed"

                )








            # ------------------------------
            #
            # Knowledge Intelligence
            #
            # ------------------------------


            self.knowledge_intelligence.analyze_knowledge(

                knowledge,
                analysis

            )








            # ------------------------------
            #
            # Complete
            #
            # ------------------------------


            self.article_repository.update_ai_status(

                article.id,

                "completed"

            )



            self.task_repository.mark_done(

                task.id

            )





            logger.info(

                f"AI completed article={article.id}"

            )



            return True







        except Exception as e:



            logger.exception(

                f"AI Worker failed: {e}"

            )





            if article:


                try:


                    self.article_repository.update_ai_status(

                        article.id,

                        "failed"

                    )


                except Exception:


                    logger.exception(

                        "Update article failed"

                    )






            try:


                self.task_repository.mark_failed(

                    task.id

                )


            except Exception:


                logger.exception(

                    "Update task failed"

                )



            return False











    # ==================================
    #
    # Run Waiting Queue
    #
    # ==================================


    def run_once(
        self
    ):


        logger.info(

            "AI Worker start"

        )





        tasks = (

            self.task_repository
            .get_waiting_tasks()

        )





        if not tasks:


            logger.info(

                "No pending AI task"

            )


            return 0






        success = 0





        for task in tasks:


            if self.process_task(task):


                success += 1






        logger.info(

            f"AI Worker finished success={success}"

        )



        return success