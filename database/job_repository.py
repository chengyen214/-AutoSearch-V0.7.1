"""
database/job_repository.py

AutoSearch V5

V5.4 P4.2

Job Repository

用途：

    管理 Target → Job 的資料庫 Persistence。

架構：

    Target
        ↓
       Job
        ↓
    JobRepository
        ↓
      MySQL
        ↓
    run.py

負責：

    - Job Create
    - Job Query
    - Job Update
    - Job Delete
    - Waiting Job Query
    - Running Job Query
    - Done Job Query
    - Failed Job Query
    - Target Job Query
    - Job Status Update
    - Retry Count Update
    - Database Row → Job Model

不負責：

    - Target Validation
    - Target Deduplication
    - Search Provider
    - Search API
    - SearchAdapter
    - Crawler
    - Parser
    - Archive
    - AI Analysis
    - Job Execution
    - Batch Execution
    - Scheduler
"""


from datetime import datetime

from database.connection import get_connection
from models.job import Job


class JobRepository:
    """
    Job Repository

    V5.4 P4.2

    Repository 只負責：

        Database Persistence
        Database Query
        DB Row → Job Model
    """

    # ==================================
    # Create
    # ==================================

    def save(self, job):
        """
        建立 Job。

        Job 初始狀態通常為：

            WAITING
        """

        if job is None:
            raise ValueError(
                "job cannot be None"
            )

        if not isinstance(job, Job):
            raise TypeError(
                "job must be an instance of Job"
            )

        if job.target_id is None:
            raise ValueError(
                "job.target_id cannot be None"
            )

        conn = get_connection()
        cursor = conn.cursor()

        try:

            sql = """
            INSERT INTO jobs
            (
                target_id,
                status,
                retry_count,
                created_time,
                started_time,
                finished_time,
                error_message
            )
            VALUES
            (
                %s,
                %s,
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
                    job.target_id,
                    job.status,
                    job.retry_count,
                    job.created_time,
                    job.started_time,
                    job.finished_time,
                    job.error_message,
                )
            )

            conn.commit()

            job.id = cursor.lastrowid

            return job

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Alias
    # ==================================

    def insert(self, job):
        """
        save() Alias。
        """

        return self.save(job)

    # ==================================
    # Get By ID
    # ==================================

    def get_by_id(self, job_id):
        """
        依 Job ID 查詢 Job。
        """

        if job_id is None:
            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM jobs
                WHERE id=%s
                LIMIT 1
                """,
                (
                    job_id,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:
            return None

        return self._to_model(result)

    # ==================================
    # Find All
    # ==================================

    def find_all(self):
        """
        取得所有 Job。

        最新建立的 Job 優先。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM jobs
                ORDER BY id DESC
                """
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]

    # ==================================
    # Find Waiting
    # ==================================

    def find_waiting(self):
        """
        取得 WAITING Job。

        未來 Batch Runner
        可從此處取得待執行工作。
        """

        return self.find_by_status(
            Job.STATUS_WAITING
        )

    # ==================================
    # Find Running
    # ==================================

    def find_running(self):
        """
        取得 RUNNING Job。
        """

        return self.find_by_status(
            Job.STATUS_RUNNING
        )

    # ==================================
    # Find Done
    # ==================================

    def find_done(self):
        """
        取得 DONE Job。
        """

        return self.find_by_status(
            Job.STATUS_DONE
        )

    # ==================================
    # Find Failed
    # ==================================

    def find_failed(self):
        """
        取得 FAILED Job。
        """

        return self.find_by_status(
            Job.STATUS_FAILED
        )

    # ==================================
    # Find By Status
    # ==================================

    def find_by_status(self, status):
        """
        依 Status 查詢 Job。
        """

        if not status:
            return []

        status = str(status).strip()

        if not status:
            return []

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM jobs
                WHERE status=%s
                ORDER BY id ASC
                """,
                (
                    status,
                )
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]

    # ==================================
    # Find By Target
    # ==================================

    def find_by_target_id(self, target_id):
        """
        取得指定 Target 的所有 Job。
        """

        if target_id is None:
            return []

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM jobs
                WHERE target_id=%s
                ORDER BY id DESC
                """,
                (
                    target_id,
                )
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]

    # ==================================
    # Find Waiting By Target
    # ==================================

    def find_waiting_by_target(self, target_id):
        """
        取得指定 Target 的 WAITING Job。
        """

        if target_id is None:
            return []

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM jobs
                WHERE target_id=%s
                  AND status=%s
                ORDER BY id ASC
                """,
                (
                    target_id,
                    Job.STATUS_WAITING,
                )
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]

    # ==================================
    # Update
    # ==================================

    def update(self, job):
        """
        更新完整 Job。
        """

        if job is None:
            raise ValueError(
                "job cannot be None"
            )

        if not isinstance(job, Job):
            raise TypeError(
                "job must be an instance of Job"
            )

        if job.id is None:
            raise ValueError(
                "job.id cannot be None"
            )

        conn = get_connection()

        cursor = conn.cursor()

        try:

            sql = """
            UPDATE jobs
            SET
                target_id=%s,
                status=%s,
                retry_count=%s,
                created_time=%s,
                started_time=%s,
                finished_time=%s,
                error_message=%s
            WHERE id=%s
            """

            cursor.execute(
                sql,
                (
                    job.target_id,
                    job.status,
                    job.retry_count,
                    job.created_time,
                    job.started_time,
                    job.finished_time,
                    job.error_message,
                    job.id,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Update Status
    # ==================================

    def update_status(
        self,
        job_id,
        status
    ):
        """
        更新 Job Status。

        RUNNING：
            更新 started_time

        DONE：
            更新 finished_time
        """

        if job_id is None:
            return False

        if not status:
            return False

        status = str(status).strip()

        if not status:
            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            started_time = None
            finished_time = None

            if status == Job.STATUS_RUNNING:

                started_time = datetime.now()

            elif status == Job.STATUS_DONE:

                finished_time = datetime.now()

            cursor.execute(
                """
                UPDATE jobs
                SET
                    status=%s,
                    started_time=
                        COALESCE(%s, started_time),
                    finished_time=
                        COALESCE(%s, finished_time)
                WHERE id=%s
                """,
                (
                    status,
                    started_time,
                    finished_time,
                    job_id,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Start
    # ==================================

    def start(self, job_id):
        """
        將 Job 設為 RUNNING。
        """

        return self.update_status(
            job_id,
            Job.STATUS_RUNNING
        )

    # ==================================
    # Complete
    # ==================================

    def complete(self, job_id):
        """
        將 Job 設為 DONE。
        """

        return self.update_status(
            job_id,
            Job.STATUS_DONE
        )

    # ==================================
    # Fail
    # ==================================

    def fail(
        self,
        job_id,
        error_message=""
    ):
        """
        將 Job 設為 FAILED，
        並增加 retry_count。
        """

        if job_id is None:
            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE jobs
                SET
                    status=%s,
                    retry_count=retry_count + 1,
                    error_message=%s
                WHERE id=%s
                """,
                (
                    Job.STATUS_FAILED,
                    error_message,
                    job_id,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Retry
    # ==================================

    def retry(self, job_id):
        """
        將 FAILED Job 重新設為 WAITING。

        Repository 只處理 Persistence。

        是否允許 Retry
        由 Job Service / Business Layer 判斷。

        注意：

            retry_count 不在這裡歸零。

            Retry 次數應保留，
            供後續 Retry Policy 使用。
        """

        if job_id is None:
            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE jobs
                SET
                    status=%s,
                    error_message=NULL,
                    started_time=NULL,
                    finished_time=NULL
                WHERE id=%s
                  AND status=%s
                """,
                (
                    Job.STATUS_WAITING,
                    job_id,
                    Job.STATUS_FAILED,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Delete
    # ==================================

    def delete_by_id(self, job_id):
        """
        依 ID 刪除 Job。
        """

        if job_id is None:
            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM jobs
                WHERE id=%s
                """,
                (
                    job_id,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Exists
    # ==================================

    def exists(self, job_id):
        """
        判斷 Job 是否存在。
        """

        if job_id is None:
            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM jobs
                WHERE id=%s
                LIMIT 1
                """,
                (
                    job_id,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        return result is not None

    # ==================================
    # Count
    # ==================================

    def count(self):
        """
        Job 總數。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM jobs
                """
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:
            return 0

        return result[0]

    # ==================================
    # Count By Status
    # ==================================

    def count_by_status(self, status):
        """
        取得指定 Status 的 Job 數量。
        """

        if not status:
            return 0

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM jobs
                WHERE status=%s
                """,
                (
                    status,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:
            return 0

        return result[0]

    # ==================================
    # Convert DB Row
    # ==================================

    def _to_model(self, result):
        """
        Database Row
            ↓
        Job Model

        Database Schema：

            finished_time
            error_message

        Job Model：

            finished_time
            error_message
        """

        if result is None:
            return None

        job = Job(

            target_id=result.get(
                "target_id"
            ),

            status=result.get(
                "status",
                Job.DEFAULT_STATUS
            ),

            retry_count=result.get(
                "retry_count",
                Job.DEFAULT_RETRY_COUNT
            ),

            created_time=result.get(
                "created_time"
            ),

            started_time=result.get(
                "started_time"
            ),

            finished_time=result.get(
                "finished_time"
            ),

            error_message=result.get(
                "error_message",
                ""
            ),
        )

        job.id = result.get(
            "id"
        )

        return job


# ==================================
# Public API
# ==================================

__all__ = [
    "JobRepository",
]
