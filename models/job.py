"""
models/job.py

AutoSearch V5

V5.4 P4.1

Job Model

用途：

    表示 Target 的一次執行工作。

架構：

    Target
        ↓
       Job
        ↓
     run.py
        ↓
    Existing V4 Pipeline

Job 不負責：

    - Target Validation
    - Target Deduplication
    - Search Provider
    - Search API
    - Crawler
    - Parser
    - Archive
    - AI Analysis
    - Job Execution

Job 只負責描述：

    1. 哪一個 Target
    2. Job 目前狀態
    3. Retry 次數
    4. 執行時間
    5. 錯誤資訊

Database Schema：

    jobs
        id
        target_id
        status
        retry_count
        created_time
        started_time
        finished_time
        error_message
"""


from datetime import datetime


class Job:
    """
    V5 Job Model。

    Job 表示 Target 的一次執行工作。

    狀態：

        WAITING
            ↓
        RUNNING
            ↓
        DONE

        RUNNING
            ↓
        FAILED
            ↓
        retry
            ↓
        WAITING
    """

    # ==================================
    # Job Status
    # ==================================

    STATUS_WAITING = "WAITING"

    STATUS_RUNNING = "RUNNING"

    STATUS_DONE = "DONE"

    STATUS_FAILED = "FAILED"

    # ==================================
    # Default Values
    # ==================================

    DEFAULT_STATUS = STATUS_WAITING

    DEFAULT_RETRY_COUNT = 0

    # ==================================
    # Constructor
    # ==================================

    def __init__(
        self,
        target_id=None,
        status=None,
        retry_count=0,
        created_time=None,
        started_time=None,
        finished_time=None,
        error_message="",
    ):
        # ==============================
        # Database ID
        # ==============================

        self.id = None

        # ==============================
        # Target
        # ==============================

        self.target_id = target_id

        # ==============================
        # Job Status
        # ==============================

        self.status = (
            status
            if status
            else self.DEFAULT_STATUS
        )

        # ==============================
        # Retry
        # ==============================

        self.retry_count = (
            retry_count
            if retry_count is not None
            else self.DEFAULT_RETRY_COUNT
        )

        # ==============================
        # Time
        # ==============================

        self.created_time = (
            created_time
            if created_time is not None
            else datetime.now()
        )

        self.started_time = started_time

        self.finished_time = finished_time

        # ==============================
        # Error
        # ==============================

        self.error_message = (
            error_message
            if error_message is not None
            else ""
        )

    # ==================================
    # Status
    # ==================================

    @property
    def is_waiting(self):
        """
        判斷 Job 是否等待執行。
        """

        return (
            self.status
            == self.STATUS_WAITING
        )

    # ==================================

    @property
    def is_running(self):
        """
        判斷 Job 是否正在執行。
        """

        return (
            self.status
            == self.STATUS_RUNNING
        )

    # ==================================

    @property
    def is_done(self):
        """
        判斷 Job 是否完成。
        """

        return (
            self.status
            == self.STATUS_DONE
        )

    # ==================================

    @property
    def is_failed(self):
        """
        判斷 Job 是否失敗。
        """

        return (
            self.status
            == self.STATUS_FAILED
        )

    # ==================================
    # Retry
    # ==================================

    @property
    def can_retry(self):
        """
        判斷 Job 是否可以進行 Retry。

        P4.1 只表示 FAILED Job
        具備 Retry 資格。

        實際 Retry 次數限制
        由後續 Job Service / Configuration
        處理。
        """

        return self.is_failed

    # ==================================
    # Dictionary
    # ==================================

    def to_dict(self):
        """
        將 Job 轉成 dictionary。

        Dictionary 欄位名稱
        與 V5 jobs Database Schema 對齊。
        """

        return {

            "id":
                self.id,

            "target_id":
                self.target_id,

            "status":
                self.status,

            "retry_count":
                self.retry_count,

            "created_time":
                self.created_time,

            "started_time":
                self.started_time,

            "finished_time":
                self.finished_time,

            "error_message":
                self.error_message,
        }

    # ==================================
    # Representation
    # ==================================

    def __repr__(self):

        return (

            "Job("

            f"id={self.id}, "

            f"target_id={self.target_id}, "

            f"status={self.status}, "

            f"retry_count={self.retry_count}"

            ")"
        )


# ==================================
# Public API
# ==================================

__all__ = [
    "Job",
]
