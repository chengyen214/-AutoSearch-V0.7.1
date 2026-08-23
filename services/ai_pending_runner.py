"""
services/ai_pending_runner.py

AutoSearch V4

AI Pending Runner

用途：
    專門重新處理 SQL 中尚未完成 AI Analysis 的 Article。

流程：

    SQL articles
        |
        +--> ai_status IS NULL
        +--> ai_status = pending
        +--> ai_status = failed
        |
        v
    ArticleRepository
        |
        v
    AI Task
        |
        v
    AIWorkerPool
        |
        v
    AIWorker
        |
        v
    AIAnalysisService
        |
        v
    LLMClient
        |
        v
    Groq
        |
        v
    Knowledge / Score / Search Index
        |
        v
    DONE

使用：

    python -m services.ai_pending_runner

注意：

    本入口不重新 Crawl。
    本入口不重新 Search。
    本入口不直接呼叫 Groq。

    所有 AI Analysis 都交給既有 AIWorker。
"""


from database.article_repository import (
    ArticleRepository
)

from database.ai_task_repository import (
    AITaskRepository
)

from models.ai_task import (
    AITask
)

from services.ai_worker_pool import (
    AIWorkerPool
)

from utils.logger import logger


# ============================================================
# Config
# ============================================================

DEFAULT_BATCH_SIZE = 50


# ============================================================
# Find Pending / Failed Articles
# ============================================================

def get_pending_articles(
    article_repository,
    limit=DEFAULT_BATCH_SIZE
):
    """
    從 SQL 找尚未完成 AI Analysis 的 Article。

    包含：

        ai_status IS NULL
        ai_status = pending
        ai_status = failed

    不包含：

        processing
        completed
    """

    cursor = (
        article_repository
        .connection
        .cursor(
            dictionary=True
        )
    )

    try:

        cursor.execute(
            """
            SELECT
                id,
                title,
                source,
                ai_status
            FROM articles
            WHERE
                ai_status IS NULL
                OR ai_status = 'pending'
                OR ai_status = 'failed'
            ORDER BY id ASC
            LIMIT %s
            """,
            (
                int(limit),
            )
        )

        return cursor.fetchall()

    finally:

        cursor.close()


# ============================================================
# Find Existing AI Task
# ============================================================

def find_existing_ai_task(
    task_repository,
    article_id
):
    """
    使用目前 AITaskRepository 已存在的 API
    查詢 Article 是否已經有 AI Task。

    目前 Repository 沒有：

        find_by_article_id()

    因此直接使用 SQL 查詢。

    注意：

        Runner 只負責 Queue Recovery / Preparation。
        不負責 AI Processing。
    """

    conn = None

    cursor = None

    try:

        conn = (
            __import__(
                "database.connection",
                fromlist=[
                    "get_connection"
                ]
            )
            .get_connection()
        )

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM ai_tasks
            WHERE article_id=%s
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                article_id,
            )
        )

        row = cursor.fetchone()

        if row is None:

            return None

        return task_repository._row_to_model(
            row
        )

    finally:

        if cursor is not None:

            cursor.close()

        if conn is not None:

            conn.close()


# ============================================================
# Create AI Task
# ============================================================

def create_ai_task(
    task_repository,
    article_id
):
    """
    建立 WAITING AI Task。

    使用目前 AITaskRepository 真正存在的：

        insert()

    而不是不存在的：

        create_task()
    """

    task = AITask(

        article_id=article_id,

        task_type="analysis",

        status="WAITING",

        priority=0,

        retry_count=0

    )

    return task_repository.insert(
        task
    )


# ============================================================
# Ensure AI Tasks
# ============================================================

def ensure_ai_tasks(
    task_repository,
    articles
):
    """
    確保 SQL 中尚未分析的 Article
    有可以交給 AI Worker 的 Task。

    規則：

        沒有 Task
            ↓
        建立 WAITING

        已有 WAITING
            ↓
        保留

        已有 RUNNING
            ↓
        保留

        已有 DONE
            ↓
        不重新建立

        已有 FAILED
            ↓
        保留 FAILED

    注意：

        Runner 不直接執行 AI。

        Runner 只準備 Task。
    """

    created = 0

    skipped = 0

    for article in articles:

        article_id = article.get(
            "id"
        )

        if article_id is None:

            skipped += 1

            continue

        try:

            existing = find_existing_ai_task(
                task_repository,
                article_id
            )

            if existing is not None:

                skipped += 1

                logger.info(
                    "AI Task already exists: "
                    f"article={article_id}, "
                    f"task={existing.id}, "
                    f"status={existing.status}"
                )

                # ------------------------------------------------
                # FAILED Task
                #
                # 這裡不直接重複建立 Task。
                #
                # Runner 的目的不是製造 duplicate task。
                # ------------------------------------------------

                if existing.status == "FAILED":

                    logger.info(
                        "Existing FAILED task kept: "
                        f"article={article_id}, "
                        f"task={existing.id}"
                    )

                continue

            # ----------------------------------------------------
            # 沒有 Task
            # ----------------------------------------------------

            task = create_ai_task(
                task_repository,
                article_id
            )

            if task is not None:

                created += 1

                logger.info(
                    "AI Task created: "
                    f"article={article_id}, "
                    f"task={task.id}"
                )

            else:

                skipped += 1

                logger.warning(
                    "AI Task creation failed: "
                    f"article={article_id}"
                )

        except Exception as e:

            skipped += 1

            logger.exception(
                "Ensure AI Task failed: "
                f"article={article_id}, "
                f"error={e}"
            )

    return created, skipped


# ============================================================
# Recover Existing RUNNING Tasks
# ============================================================

def recover_running_tasks(
    task_repository
):
    """
    Recovery：

        RUNNING
            ↓
        WAITING

    使用既有 P2.4 Queue Recovery。

    目的：

        如果上一個程序中斷，
        避免 Task 永遠卡在 RUNNING。
    """

    try:

        recovered = (
            task_repository
            .recover_running_tasks()
        )

        if recovered > 0:

            logger.info(
                "Recovered RUNNING AI tasks: "
                f"{recovered}"
            )

        else:

            logger.info(
                "No RUNNING AI tasks require recovery."
            )

        return recovered

    except Exception as e:

        logger.exception(
            "AI Task recovery failed: "
            f"{e}"
        )

        return 0


# ============================================================
# Wait Worker Pool
# ============================================================

def wait_for_worker_pool(
    worker_pool
):
    """
    等待 AI Worker Pool 完成。

    AIWorkerPool 目前沒有：

        wait()

    正確 API 是：

        join()

    Queue Drain 仍然由：

        AIWorker.run_once()

    負責。
    """

    logger.info(
        "Waiting for AI Worker Pool..."
    )

    worker_pool.join()

    logger.info(
        "AI Worker Pool completed."
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    AI Pending Runner 主入口。
    """

    logger.info(
        "=================================================="
    )

    logger.info(
        "AI Pending Runner START"
    )

    logger.info(
        "=================================================="
    )

    article_repository = None

    task_repository = None

    worker_pool = None

    try:

        # ==================================================
        # Repository
        # ==================================================

        article_repository = (
            ArticleRepository()
        )

        task_repository = (
            AITaskRepository()
        )

        # ==================================================
        # Recover Previous RUNNING Tasks
        # ==================================================

        recover_running_tasks(
            task_repository
        )

        # ==================================================
        # Find SQL Articles
        # ==================================================

        articles = (
            get_pending_articles(
                article_repository,
                DEFAULT_BATCH_SIZE
            )
        )

        logger.info(
            "SQL pending articles: "
            f"{len(articles)}"
        )

        if not articles:

            logger.info(
                "No pending AI articles found."
            )

            return 0

        # ==================================================
        # Print Articles
        # ==================================================

        for article in articles:

            logger.info(
                "Pending Article: "
                f"id={article.get('id')}, "
                f"status={article.get('ai_status')}, "
                f"source={article.get('source')}, "
                f"title={article.get('title')}"
            )

        # ==================================================
        # Ensure AI Tasks
        # ==================================================

        created, skipped = (
            ensure_ai_tasks(
                task_repository,
                articles
            )
        )

        logger.info(
            "AI Task preparation completed: "
            f"created={created}, "
            f"skipped={skipped}"
        )

        # ==================================================
        # Check WAITING Queue
        # ==================================================

        waiting_count = (
            task_repository
            .count_waiting_tasks()
        )

        logger.info(
            "WAITING AI tasks: "
            f"{waiting_count}"
        )

        if waiting_count <= 0:

            logger.info(
                "No WAITING AI tasks available."
            )

            return 0

        # ==================================================
        # Start AI Worker Pool
        # ==================================================

        logger.info(
            "Starting AI Worker Pool..."
        )

        worker_pool = (
            AIWorkerPool(
                worker_count=1
            )
        )

        started = (
            worker_pool.start()
        )

        if not started:

            logger.error(
                "AI Worker Pool failed to start."
            )

            return 1

        logger.info(
            "AI Worker Pool started."
        )

        # ==================================================
        # Wait
        # ==================================================

        wait_for_worker_pool(
            worker_pool
        )

        # ==================================================
        # Final Status
        # ==================================================

        remaining = (
            get_pending_articles(
                article_repository,
                DEFAULT_BATCH_SIZE
            )
        )

        remaining_count = len(
            remaining
        )

        logger.info(
            "Remaining pending articles: "
            f"{remaining_count}"
        )

        logger.info(
            "AI Worker Pool status: "
            f"{worker_pool.get_status()}"
        )

        logger.info(
            "=================================================="
        )

        logger.info(
            "AI Pending Runner FINISHED"
        )

        logger.info(
            "=================================================="
        )

        return 0

    except KeyboardInterrupt:

        logger.warning(
            "AI Pending Runner interrupted by user."
        )

        if worker_pool is not None:

            try:

                worker_pool.stop()

            except Exception:

                logger.exception(
                    "AI Worker Pool stop failed."
                )

        return 1

    except Exception as e:

        logger.exception(
            "AI Pending Runner failed: "
            f"{e}"
        )

        return 1

    finally:

        # ==================================================
        # Stop Worker Pool
        # ==================================================

        if worker_pool is not None:

            try:

                if worker_pool.is_running():

                    worker_pool.stop()

            except Exception:

                logger.exception(
                    "AI Worker Pool cleanup failed."
                )

        # ==================================================
        # Close Article Repository
        # ==================================================

        if article_repository is not None:

            try:

                article_repository.close()

            except Exception:

                logger.exception(
                    "ArticleRepository close failed."
                )

        # ==================================================
        # AITaskRepository
        # ==================================================
        #
        # 注意：
        #
        # AITaskRepository 沒有 close()
        #
        # 每一個 Repository method
        # 都自行管理 connection。
        #
        # 因此這裡不能：
        #
        # task_repository.close()
        #

        logger.info(
            "AI Pending Runner cleanup completed."
        )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )