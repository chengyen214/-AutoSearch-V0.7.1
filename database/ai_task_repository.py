"""
database/ai_task_repository.py

AutoSearch V4

P2.4.1

AI Task Queue Repository

功能:

1. 建立 AI Task
2. 查詢 WAITING Task
3. Claim AI Task
4. 防止多 Worker 重複取得 Task
5. 查詢 Task
6. 更新 Task 狀態
7. Retry 管理

Table:

    ai_tasks

Task Lifecycle:

    WAITING
        |
        | claim
        v
    RUNNING
        |
        +------> DONE
        |
        +------> FAILED

P2.4.1 Queue 強化:

    Worker A
        |
        +--> claim Task
        |
        v
      RUNNING

    Worker B
        |
        +--> claim 同一 Task
        |
        v
      失敗

因此同一個 Task
只能被一個 Worker Claim。
"""


from database.connection import get_connection

from models.ai_task import AITask


class AITaskRepository:

    """
    AI Task Repository

    負責:

        ai_tasks table CRUD

    P2.4.1:

        Task Queue
        Task Claim
        Worker Safety
        Retry 基礎管理
    """

    # ==================================================
    # Insert Task
    # ==================================================

    def insert(
        self,
        task
    ):
        """
        建立新的 AI Task。

        初始狀態通常為:

            WAITING
        """

        conn = get_connection()

        cursor = conn.cursor()

        sql = """
        INSERT INTO ai_tasks
        (
            article_id,
            task_type,
            status,
            priority,
            retry_count
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        cursor.execute(
            sql,
            (
                task.article_id,
                task.task_type,
                task.status,
                task.priority,
                task.retry_count
            )
        )

        conn.commit()

        task.id = cursor.lastrowid

        cursor.close()
        conn.close()

        return task

    # ==================================================
    # Get Waiting Tasks
    # ==================================================

    def get_waiting_tasks(
        self,
        limit=10
    ):
        """
        取得 WAITING Tasks。

        注意:

        此方法只負責查詢。

        不會將 Task 改成 RUNNING。

        Worker 若要正式處理 Task，
        應使用:

            claim_waiting_tasks()
        """

        if limit is None or limit < 1:

            limit = 10

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        sql = """
        SELECT *
        FROM ai_tasks
        WHERE status='WAITING'
        ORDER BY
            priority DESC,
            created_time ASC
        LIMIT %s
        """

        cursor.execute(
            sql,
            (
                limit,
            )
        )

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        tasks = []

        for row in rows:

            task = self._row_to_model(
                row
            )

            tasks.append(
                task
            )

        return tasks

    # ==================================================
    # Claim Task
    # ==================================================

    def claim_task(
        self,
        task_id
    ):
        """
        Claim 一個 WAITING Task。

        P2.4.1 核心功能。

        只有目前狀態為 WAITING
        的 Task 才能被 Claim。

        SQL 使用:

            WHERE id=%s
            AND status='WAITING'

        這個條件非常重要。

        假設:

            Worker A
                |
                +--> claim Task 1
                |
                v
              RUNNING

            Worker B
                |
                +--> claim Task 1
                |
                v
              UPDATE 0 rows

        因此 Worker B Claim 失敗。

        Returns
        -------

        AITask
            Claim 成功

        None
            Claim 失敗
        """

        conn = get_connection()

        cursor = conn.cursor()

        sql = """
        UPDATE ai_tasks
        SET
            status='RUNNING'
        WHERE
            id=%s
            AND status='WAITING'
        """

        cursor.execute(
            sql,
            (
                task_id,
            )
        )

        affected = cursor.rowcount

        conn.commit()

        cursor.close()
        conn.close()

        # ----------------------------------------------
        # Claim Failed
        # ----------------------------------------------

        if affected != 1:

            return None

        # ----------------------------------------------
        # Claim Success
        #
        # 重新取得最新 Task
        # ----------------------------------------------

        return self.find_by_id(
            task_id
        )

    # ==================================================
    # Claim Waiting Tasks
    # ==================================================

    def claim_waiting_tasks(
        self,
        limit=10
    ):
        """
        取得並 Claim WAITING Tasks。

        P2.4.1 Worker 建議使用此方法。

        流程:

            WAITING
                |
                v
              Claim
                |
                v
             RUNNING
                |
                v
             Worker

        注意:

        get_waiting_tasks()
        只是取得候選 Task。

        真正的安全控制由:

            claim_task()

        負責。

        即使多個 Worker
        同時取得相同候選 Task，
        最終只有一個 Worker
        能成功 UPDATE:

            WAITING -> RUNNING
        """

        if limit is None or limit < 1:

            limit = 10

        waiting_tasks = (
            self.get_waiting_tasks(
                limit
            )
        )

        claimed_tasks = []

        for task in waiting_tasks:

            claimed = self.claim_task(
                task.id
            )

            if claimed is not None:

                claimed_tasks.append(
                    claimed
                )

        return claimed_tasks

    # ==================================================
    # Find Task By ID
    # ==================================================

    def find_by_id(
        self,
        task_id
    ):
        """
        依 ID 查詢 AI Task。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        sql = """
        SELECT *
        FROM ai_tasks
        WHERE id=%s
        """

        cursor.execute(
            sql,
            (
                task_id,
            )
        )

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row is None:

            return None

        return self._row_to_model(
            row
        )

    # ==================================================
    # Update Status
    # ==================================================

    def update_status(
        self,
        task_id,
        status
    ):
        """
        更新 Task 狀態。

        支援:

            WAITING
            RUNNING
            DONE
            FAILED

        DONE 時自動寫入:

            finished_time

        注意:

        此方法是一般狀態更新 API。

        Worker 若要 Claim Task，
        必須使用:

            claim_task()

        不應直接使用:

            update_status(
                task_id,
                "RUNNING"
            )
        """

        conn = get_connection()

        cursor = conn.cursor()

        if status == "DONE":

            sql = """
            UPDATE ai_tasks
            SET
                status=%s,
                finished_time=NOW()
            WHERE id=%s
            """

        else:

            sql = """
            UPDATE ai_tasks
            SET
                status=%s
            WHERE id=%s
            """

        cursor.execute(
            sql,
            (
                status,
                task_id
            )
        )

        affected = cursor.rowcount

        conn.commit()

        cursor.close()
        conn.close()

        # ------------------------------------------------
        # 使用 == 1
        #
        # 避免 MagicMock rowcount
        # 在測試環境出現:
        #
        # TypeError:
        # '>' not supported ...
        # ------------------------------------------------

        return affected == 1

    # ==================================================
    # Mark Running
    # ==================================================

    def mark_running(
        self,
        task_id
    ):
        """
        將 WAITING Task Claim 為 RUNNING。

        P2.4.1:

        不直接 UPDATE。

        必須確認原本狀態為:

            WAITING

        因此可以避免多 Worker
        同時處理相同 Task。
        """

        claimed = self.claim_task(
            task_id
        )

        return claimed is not None

    # ==================================================
    # Mark Done
    # ==================================================

    def mark_done(
        self,
        task_id
    ):
        """
        Task 完成。

        RUNNING
            |
            v
          DONE

        只有 RUNNING Task
        才能進入 DONE。

        這可以避免:

            WAITING -> DONE

        這種非法狀態跳轉。
        """

        conn = get_connection()

        cursor = conn.cursor()

        sql = """
        UPDATE ai_tasks
        SET
            status='DONE',
            finished_time=NOW()
        WHERE
            id=%s
            AND status='RUNNING'
        """

        cursor.execute(
            sql,
            (
                task_id,
            )
        )

        affected = cursor.rowcount

        conn.commit()

        cursor.close()
        conn.close()

        return affected == 1

    # ==================================================
    # Mark Failed
    # ==================================================

    def mark_failed(
        self,
        task_id
    ):
        """
        Task 失敗。

        RUNNING
            |
            v
          FAILED

        同時:

            retry_count + 1

        只有 RUNNING Task
        才能被標記為 FAILED。
        """

        conn = get_connection()

        cursor = conn.cursor()

        sql = """
        UPDATE ai_tasks
        SET
            status='FAILED',
            retry_count = retry_count + 1
        WHERE
            id=%s
            AND status='RUNNING'
        """

        cursor.execute(
            sql,
            (
                task_id,
            )
        )

        affected = cursor.rowcount

        conn.commit()

        cursor.close()
        conn.close()

        return affected == 1

    # ==================================================
    # Convert DB Row -> Model
    # ==================================================

    def _row_to_model(
        self,
        row
    ):
        """
        Database Row
            ↓
        AITask Model
        """

        task = AITask(

            article_id=row[
                "article_id"
            ],

            task_type=row[
                "task_type"
            ],

            status=row[
                "status"
            ],

            priority=row[
                "priority"
            ],

            retry_count=row[
                "retry_count"
            ],

            created_time=row.get(
                "created_time"
            ),

            finished_time=row.get(
                "finished_time"
            )

        )

        task.id = row[
            "id"
        ]

        return task
