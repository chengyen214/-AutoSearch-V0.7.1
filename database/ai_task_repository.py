"""
database/ai_task_repository.py

AutoSearch V4

P2.4.1
P2.4 Async AI Queue Recovery

AI Task Queue Repository

功能:

1. 建立 AI Task
2. 查詢 WAITING Task
3. 查詢 RUNNING Task
4. Claim AI Task
5. 防止多 Worker 重複取得 Task
6. 查詢 Task
7. 更新 Task 狀態
8. Retry 管理
9. Startup Queue Recovery

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

P2.4 Queue Recovery:

    Application 啟動
          |
          v
    檢查 RUNNING Tasks
          |
          v
    前一次程序可能中斷
          |
          v
    RUNNING -> WAITING
          |
          v
    Scheduler Resume
          |
          v
    Worker Queue Drain

注意:

Recovery 只負責恢復：

    RUNNING -> WAITING

不會處理：

    DONE
    FAILED
    WAITING

真正的 Task Processing
仍由 AIWorker 負責。
"""


from database.connection import get_connection

from models.ai_task import AITask


class AITaskRepository:

    """
    AI Task Repository

    負責:

        ai_tasks table CRUD
        Queue Claim
        Queue Recovery
        Retry 基礎管理

    P2.4:

        Startup Queue Recovery
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

        try:

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

            return task

        finally:

            cursor.close()
            conn.close()

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

        try:

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

        finally:

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
    # Count Waiting Tasks
    # ==================================================

    def count_waiting_tasks(
        self
    ):
        """
        取得目前 WAITING AI Task 數量。

        P2.4.2

        用於:

            AIBatchTriggerService

        直接使用:

            SELECT COUNT(*)

        Returns
        -------

        int

            WAITING Task 數量
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            sql = """
            SELECT COUNT(*) AS count
            FROM ai_tasks
            WHERE status='WAITING'
            """

            cursor.execute(sql)

            row = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if row is None:

            return 0

        return int(
            row.get(
                "count",
                0
            )
        )

    # ==================================================
    # Get Running Tasks
    # ==================================================

    def get_running_tasks(
        self,
        limit=None
    ):
        """
        取得目前 RUNNING Tasks。

        P2.4 Startup Recovery。

        用途:

            Application 啟動時
            檢查上一個程序是否留下
            未完成的 RUNNING Tasks。

        注意:

            本方法只查詢。

        不會修改 Task 狀態。

        Parameters
        ----------

        limit:
            最大 Task 數量。

            None:
                取得全部 RUNNING Tasks

        Returns
        -------

        list[AITask]
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            if limit is None:

                sql = """
                SELECT *
                FROM ai_tasks
                WHERE status='RUNNING'
                ORDER BY
                    priority DESC,
                    created_time ASC
                """

                cursor.execute(sql)

            else:

                if limit < 1:

                    limit = 1

                sql = """
                SELECT *
                FROM ai_tasks
                WHERE status='RUNNING'
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

        finally:

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
    # Count Running Tasks
    # ==================================================

    def count_running_tasks(
        self
    ):
        """
        取得目前 RUNNING AI Task 數量。

        P2.4 Startup Recovery / Monitoring。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            sql = """
            SELECT COUNT(*) AS count
            FROM ai_tasks
            WHERE status='RUNNING'
            """

            cursor.execute(sql)

            row = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if row is None:

            return 0

        return int(
            row.get(
                "count",
                0
            )
        )

    # ==================================================
    # Recover Running Tasks
    # ==================================================

    def recover_running_tasks(
        self
    ):
        """
        恢復上一個程序中斷時留下的 RUNNING Tasks。

        P2.4 Startup Queue Recovery。

        狀態轉換:

            RUNNING
                |
                v
            WAITING

        用途:

            python run.py
                |
                v
            Application Startup
                |
                v
            recover_running_tasks()
                |
                v
            Scheduler Resume

        安全原則:

            只處理目前 status='RUNNING'
            的 Task。

        不會修改:

            WAITING
            DONE
            FAILED

        Returns
        -------

        int

            本次成功恢復的 Task 數量。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            sql = """
            UPDATE ai_tasks
            SET
                status='WAITING',
                finished_time=NULL
            WHERE
                status='RUNNING'
            """

            cursor.execute(sql)

            affected = cursor.rowcount

            conn.commit()

            # ------------------------------------------------
            # 使用 == 0 判斷
            #
            # 避免測試環境 MagicMock rowcount
            # 造成比較問題。
            # ------------------------------------------------

            if affected is None:

                return 0

            return int(
                affected
            )

        finally:

            cursor.close()
            conn.close()

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

        Returns
        -------

        AITask
            Claim 成功

        None
            Claim 失敗
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

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

        finally:

            cursor.close()
            conn.close()

        # ----------------------------------------------
        # Claim Failed
        # ----------------------------------------------

        if affected != 1:

            return None

        # ----------------------------------------------
        # Claim Success
        # ----------------------------------------------
        #
        # 重新取得最新 Task
        #

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

        try:

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

        finally:

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
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

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

        finally:

            cursor.close()
            conn.close()

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
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

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

        finally:

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

        try:

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

        finally:

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