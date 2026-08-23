"""
services/batch_job_status_service.py

AutoSearch V5

V5.6.2
P5.6 Batch Job Status Service

用途：

    管理 BatchExecutionService 中
    Job 的執行生命週期。

架構：

    BatchExecutionService
        ↓
    BatchJobStatusService
        ↓
    JobRepository
        ↓
    jobs

Job Lifecycle：

    WAITING
        ↓
    RUNNING
        ↓
    DONE

    RUNNING
        ↓
    FAILED

V5.6.2 Pipeline：

    WAITING
        ↓
    BatchExecutionService
        ↓
    RUNNING
        ↓
    JobExecutorBridge
        ↓
    TargetSourceService
        ↓
    SourceResolutionBridge
        ↓
    Resolved Source
        ↓
    DONE / FAILED

負責：

    - Job Status Query
    - Job Start
    - Job Complete
    - Job Fail
    - Status Lifecycle Delegation
    - JobRepository delegation

不負責：

    - Job Retrieval
    - Target Retrieval
    - Target Creation
    - Batch Execution
    - Source Definition
    - Source Resolution
    - Search Provider
    - Search API
    - Search Execution
    - SearchAdapter
    - Crawler
    - Parser
    - Archive
    - AI Analysis
    - Retry Policy
    - Scheduler

設計原則：

    BatchExecutionService
        負責：

            「什麼時候開始與完成 Job？」

    BatchJobStatusService
        負責：

            「如何變更 Job Status？」

    JobRepository
        負責：

            「如何將 Status 寫入 Database？」

因此：

    BatchJobStatusService
        不應直接知道：

            Provider
            Adapter
            SearchExecutionBridge
            Crawler
            Parser
            Article
"""


# ==================================================
#
# Job Repository
#
# ==================================================

from database.job_repository import (
    JobRepository,
)


# ==================================================
#
# Job Model
#
# ==================================================

from models.job import (
    Job,
)


class BatchJobStatusService:
    """
    V5.6.2 Batch Job Status Service。

    只負責管理 Batch Runner
    執行過程中的 Job Status。

    Job Lifecycle：

        WAITING
            ↓
        RUNNING
            ↓
        DONE

        RUNNING
            ↓
        FAILED

    本 Service 不執行實際 Job 工作。
    """

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        job_repository=None,
    ):
        """
        建立 BatchJobStatusService。

        Parameters
        ----------
        job_repository : JobRepository | None

            Job Persistence Layer。

            None：

                使用預設 JobRepository。
        """

        if job_repository is None:

            job_repository = (
                JobRepository()
            )

        self.job_repository = (
            job_repository
        )

    # ==================================================
    #
    # Get Job
    #
    # ==================================================

    def get_job(
        self,
        job_id,
    ):
        """
        取得 Job。

        本方法只負責查詢。

        不修改：

            Job Status
            Retry Count
            Error Message
        """

        if job_id is None:

            return None

        return (
            self.job_repository.get_by_id(
                job_id
            )
        )

    # ==================================================
    #
    # Start Job
    #
    # ==================================================

    def start_job(
        self,
        job_id,
    ):
        """
        將 Job 設為 RUNNING。

        Lifecycle：

            WAITING
                ↓
            RUNNING

        實際狀態更新由
        JobRepository.start() 負責。
        """

        if job_id is None:

            return False

        return (
            self.job_repository.start(
                job_id
            )
        )

    # ==================================================
    #
    # Complete Job
    #
    # ==================================================

    def complete_job(
        self,
        job_id,
    ):
        """
        將 Job 設為 DONE。

        Lifecycle：

            RUNNING
                ↓
            DONE

        實際狀態更新由
        JobRepository.complete() 負責。
        """

        if job_id is None:

            return False

        return (
            self.job_repository.complete(
                job_id
            )
        )

    # ==================================================
    #
    # Fail Job
    #
    # ==================================================

    def fail_job(
        self,
        job_id,
        error_message="",
    ):
        """
        將 Job 設為 FAILED。

        Lifecycle：

            RUNNING
                ↓
            FAILED

        實際狀態與錯誤資訊更新
        由 JobRepository.fail() 負責。

        Repository 可負責：

            - status = FAILED
            - retry_count + 1
            - error_message
        """

        if job_id is None:

            return False

        return (
            self.job_repository.fail(
                job_id,
                error_message,
            )
        )

    # ==================================================
    #
    # Get Status
    #
    # ==================================================

    def get_status(
        self,
        job_id,
    ):
        """
        取得 Job Status。

        Returns
        -------

        str | None

            Job 不存在：

                None
        """

        job = self.get_job(
            job_id
        )

        if job is None:

            return None

        return job.status

    # ==================================================
    #
    # Is Waiting
    #
    # ==================================================

    def is_waiting(
        self,
        job_id,
    ):
        """
        判斷 Job 是否為 WAITING。
        """

        job = self.get_job(
            job_id
        )

        if job is None:

            return False

        return (
            job.status
            == Job.STATUS_WAITING
        )

    # ==================================================
    #
    # Is Running
    #
    # ==================================================

    def is_running(
        self,
        job_id,
    ):
        """
        判斷 Job 是否為 RUNNING。
        """

        job = self.get_job(
            job_id
        )

        if job is None:

            return False

        return (
            job.status
            == Job.STATUS_RUNNING
        )

    # ==================================================
    #
    # Is Done
    #
    # ==================================================

    def is_done(
        self,
        job_id,
    ):
        """
        判斷 Job 是否為 DONE。
        """

        job = self.get_job(
            job_id
        )

        if job is None:

            return False

        return (
            job.status
            == Job.STATUS_DONE
        )

    # ==================================================
    #
    # Is Failed
    #
    # ==================================================

    def is_failed(
        self,
        job_id,
    ):
        """
        判斷 Job 是否為 FAILED。
        """

        job = self.get_job(
            job_id
        )

        if job is None:

            return False

        return (
            job.status
            == Job.STATUS_FAILED
        )

    # ==================================================
    #
    # Lifecycle Alias
    #
    # ==================================================

    def start(
        self,
        job_id,
    ):
        """
        start_job() Alias。
        """

        return self.start_job(
            job_id
        )

    def complete(
        self,
        job_id,
    ):
        """
        complete_job() Alias。
        """

        return self.complete_job(
            job_id
        )

    def fail(
        self,
        job_id,
        error_message="",
    ):
        """
        fail_job() Alias。
        """

        return self.fail_job(
            job_id,
            error_message,
        )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "BatchJobStatusService",
]
