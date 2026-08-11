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


P2.4 Async AI Scaling

Worker 行為：

1. Claim WAITING AI Tasks
2. 取得 RUNNING AI Tasks
3. 持續處理 Queue
4. 每批處理完成後重新 Claim WAITING Tasks
5. 直到沒有 WAITING Task
6. Worker 才結束

例如：

WAITING = 45

Batch 1
    10 Tasks

Batch 2
    10 Tasks

Batch 3
    10 Tasks

Batch 4
    10 Tasks

Batch 5
    5 Tasks

最後：

WAITING = 0


P2.4.8 Worker Safety

正常 Pool：

    claim_waiting_tasks()
            |
            v
    WAITING -> RUNNING
            |
            v
       process_task()


直接呼叫 process_task()：

    WAITING
       |
       v
    mark_running()
       |
       v
    RUNNING
       |
       v
    process_task()

因此：

- Worker Pool 不會重複 Claim
- Unit Test 可以直接測 process_task()
- 多 Worker 可以安全 Claim Task
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

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self
    ):

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

    # ==================================================
    # Process Task
    # ==================================================

    def process_task(
        self,
        task
    ):
        """
        處理單一 AI Task。

        如果 Task 已經是：

            RUNNING

        表示：

            claim_waiting_tasks()

        已經完成 Claim。

        如果 Task 還是：

            WAITING

        表示 process_task()
        被直接呼叫。

        此時會執行：

            WAITING
                |
                v
            mark_running()
                |
                v
             RUNNING
        """

        article = None

        try:

            logger.info(
                f"Processing AI task={task.id}"
            )

            # ==========================================
            # Task Claim
            # ==========================================

            task_status = getattr(
                task,
                "status",
                None
            )

            # ------------------------------------------
            # Direct process_task() call
            #
            # WAITING -> RUNNING
            # ------------------------------------------

            if task_status == "WAITING":

                claimed = (
                    self.task_repository
                    .mark_running(
                        task.id
                    )
                )

                if not claimed:

                    logger.warning(
                        "AI Worker could not claim task: "
                        f"task={task.id}"
                    )

                    return False

            # ------------------------------------------
            # Pool path
            #
            # claim_waiting_tasks()
            # 已經完成：
            #
            # WAITING -> RUNNING
            #
            # 因此這裡不再次 Claim。
            # ------------------------------------------

            # ==========================================
            # Load Article
            # ==========================================

            article = (
                self.article_repository
                .find_model_by_id(
                    task.article_id
                )
            )

            if article is None:

                raise Exception(
                    f"Article not found "
                    f"id={task.article_id}"
                )

            # ==========================================
            # Article AI Processing
            # ==========================================

            self.article_repository.update_ai_status(
                article.id,
                "processing"
            )

            # ==========================================
            # AI Analysis
            # ==========================================

            analysis = (
                self.ai_service.analyze(
                    article
                )
            )

            if analysis is None:

                raise Exception(
                    "AI Analysis failed"
                )

            # ==========================================
            # Save AI Result
            # ==========================================

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

            # ==========================================
            # AI Analysis
            #
            # ->
            #
            # Knowledge
            # ==========================================

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

            # ==========================================
            # Save Knowledge
            #
            # ->
            # knowledge_archive
            #
            # ->
            # search_index
            # ==========================================

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

            # ==========================================
            # Knowledge Intelligence
            # ==========================================

            self.knowledge_intelligence.analyze_knowledge(
                knowledge,
                analysis
            )

            # ==========================================
            # Complete Article
            # ==========================================

            self.article_repository.update_ai_status(
                article.id,
                "completed"
            )

            # ==========================================
            # Complete Task
            #
            # RUNNING -> DONE
            # ==========================================

            done = (
                self.task_repository
                .mark_done(
                    task.id
                )
            )

            if not done:

                raise Exception(
                    f"AI Task DONE update failed "
                    f"task={task.id}"
                )

            logger.info(
                f"AI completed article={article.id}, "
                f"task={task.id}"
            )

            return True

        except Exception as e:

            logger.exception(
                f"AI Worker failed: {e}"
            )

            # ==========================================
            # Article Failure
            # ==========================================

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

            # ==========================================
            # Task Failure
            #
            # RUNNING -> FAILED
            # ==========================================

            try:

                self.task_repository.mark_failed(
                    task.id
                )

            except Exception:

                logger.exception(
                    "Update task failed"
                )

            return False

    # ==================================================
    # Run Waiting Queue
    # ==================================================

    def run_once(
        self
    ):
        """
        處理完整 WAITING AI Queue。

        方法名稱保留 run_once()
        以相容：

            AIWorkerPool
            AIScheduler

        實際行為：

            一次 Worker Lifecycle
            =
            持續 Claim + 處理 Queue

        每批最多：

            10 Tasks

        直到：

            WAITING = 0

        例如：

            WAITING = 45

            Batch 1 = 10
            Batch 2 = 10
            Batch 3 = 10
            Batch 4 = 10
            Batch 5 = 5

        Returns
        -------

        int
            本次 Worker Lifecycle
            成功處理的 Task 數量。
        """

        logger.info(
            "AI Worker start"
        )

        total_success = 0

        total_failed = 0

        batch_number = 0

        # ==================================================
        # Continuous Queue Processing
        # ==================================================

        while True:

            batch_number += 1

            # ==========================================
            # Claim Waiting Tasks
            #
            # P2.4.8
            #
            # 不直接：
            #
            #     get_waiting_tasks()
            #
            # 改用：
            #
            #     claim_waiting_tasks()
            #
            # 確保：
            #
            # WAITING -> RUNNING
            # ==========================================

            tasks = (
                self.task_repository
                .claim_waiting_tasks(
                    limit=10
                )
            )

            # ==========================================
            # Queue Empty
            # ==========================================

            if not tasks:

                logger.info(
                    "AI Worker queue empty"
                )

                break

            # ==========================================
            # Batch Information
            # ==========================================

            logger.info(
                "AI Worker processing "
                f"batch={batch_number}, "
                f"tasks={len(tasks)}"
            )

            batch_success = 0

            batch_failed = 0

            # ==========================================
            # Process Batch
            # ==========================================

            for task in tasks:

                result = (
                    self.process_task(
                        task
                    )
                )

                if result:

                    batch_success += 1

                    total_success += 1

                else:

                    batch_failed += 1

                    total_failed += 1

            # ==========================================
            # Batch Summary
            # ==========================================

            logger.info(
                "AI Worker batch completed "
                f"batch={batch_number}, "
                f"success={batch_success}, "
                f"failed={batch_failed}"
            )

            # ==========================================
            # Failure Safety
            #
            # 如果整批都失敗：
            #
            # RUNNING -> FAILED
            #
            # 正常情況下 Task 已經離開
            # WAITING Queue。
            #
            # 因此可以繼續抓下一批。
            #
            # 但如果完全沒有成功，
            # 可以結束目前 lifecycle，
            # 避免異常狀態下無限循環。
            # ==========================================

            if (
                batch_success == 0
                and batch_failed > 0
            ):

                logger.warning(
                    "AI Worker batch produced "
                    "no successful tasks. "
                    "Stopping current lifecycle "
                    "to avoid infinite retry loop."
                )

                break

        # ==================================================
        # Final Summary
        # ==================================================

        logger.info(
            "AI Worker finished "
            f"success={total_success}, "
            f"failed={total_failed}, "
            f"batches={batch_number}"
        )

        return total_success
