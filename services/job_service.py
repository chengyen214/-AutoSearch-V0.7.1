"""
services/job_service.py

AutoSearch V5

V5.4 P4.3

Job Service

用途：

    管理 Target → Job 的 Business Flow。

架構：

    Target
        ↓
    JobService
        ↓
    JobRepository
        ↓
    MySQL

負責：

    - Target → Job 建立
    - Job Query
    - Target Job Query
    - Waiting Job Query
    - Job Start
    - Job Complete
    - Job Fail
    - Job Retry
    - Job Lifecycle 管理

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

設計原則：

    JobRepository
        ↓
    Database Persistence

    JobService
        ↓
    Job Business Flow

    JobService 不直接執行 Crawl。

    實際執行將由後續：

        Job Executor
            ↓
        Batch Runner
            ↓
        V4 Crawl Pipeline

    處理。
"""


from database.job_repository import JobRepository
from models.job import Job


class JobService:
    """
    Job Service

    V5.4 P4.3

    負責：

        Target → Job
        Job Lifecycle
        Job Query

    不負責：

        Crawl
        Search
        Parser
        Archive
        AI
        Batch
        Scheduler
    """

    def __init__(
        self,
        repository=None,
    ):
        """
        建立 JobService。

        Parameters
        ----------
        repository :
            JobRepository

        若未提供 Repository，
        預設建立 JobRepository。
        """

        self.repository = (
            repository
            if repository is not None
            else JobRepository()
        )

    # ==================================
    # Create Job
    # ==================================

    def create_job(
        self,
        target_id,
    ):
        """
        為指定 Target 建立 Job。

        Job 初始狀態：

            WAITING

        Parameters
        ----------
        target_id :
            Target ID

        Returns
        -------
        Job
            建立成功的 Job。
        """

        if target_id is None:

            raise ValueError(
                "target_id cannot be None"
            )

        job = Job(
            target_id=target_id
        )

        return self.repository.save(
            job
        )

    # ==================================
    # Alias
    # ==================================

    def create(
        self,
        target_id,
    ):
        """
        create_job() Alias。
        """

        return self.create_job(
            target_id
        )

    # ==================================
    # Get By ID
    # ==================================

    def get_job(
        self,
        job_id,
    ):
        """
        取得指定 Job。
        """

        if job_id is None:

            return None

        return self.repository.get_by_id(
            job_id
        )

    # ==================================
    # Alias
    # ==================================

    def get_by_id(
        self,
        job_id,
    ):
        """
        get_job() Alias。
        """

        return self.get_job(
            job_id
        )

    # ==================================
    # Find All
    # ==================================

    def find_all(
        self,
    ):
        """
        取得所有 Job。
        """

        return self.repository.find_all()

    # ==================================
    # Find Waiting
    # ==================================

    def find_waiting(
        self,
    ):
        """
        取得所有 WAITING Job。

        未來 Batch Runner
        將從此處取得待執行 Job。
        """

        return self.repository.find_waiting()

    # ==================================
    # Find Running
    # ==================================

    def find_running(
        self,
    ):
        """
        取得所有 RUNNING Job。
        """

        return self.repository.find_running()

    # ==================================
    # Find Done
    # ==================================

    def find_done(
        self,
    ):
        """
        取得所有 DONE Job。
        """

        return self.repository.find_done()

    # ==================================
    # Find Failed
    # ==================================

    def find_failed(
        self,
    ):
        """
        取得所有 FAILED Job。
        """

        return self.repository.find_failed()

    # ==================================
    # Find By Target
    # ==================================

    def find_by_target(
        self,
        target_id,
    ):
        """
        取得指定 Target 的所有 Job。
        """

        if target_id is None:

            return []

        return self.repository.find_by_target_id(
            target_id
        )

    # ==================================
    # Find Waiting By Target
    # ==================================

    def find_waiting_by_target(
        self,
        target_id,
    ):
        """
        取得指定 Target 的 WAITING Job。
        """

        if target_id is None:

            return []

        return self.repository.find_waiting_by_target(
            target_id
        )

    # ==================================
    # Start Job
    # ==================================

    def start_job(
        self,
        job_id,
    ):
        """
        將 Job 設為 RUNNING。

        Repository 會：

            status = RUNNING
            started_time = now
        """

        if job_id is None:

            return False

        return self.repository.start(
            job_id
        )

    # ==================================
    # Complete Job
    # ==================================

    def complete_job(
        self,
        job_id,
    ):
        """
        將 Job 設為 DONE。

        Repository 會：

            status = DONE
            finished_time = now
        """

        if job_id is None:

            return False

        return self.repository.complete(
            job_id
        )

    # ==================================
    # Fail Job
    # ==================================

    def fail_job(
        self,
        job_id,
        error_message="",
    ):
        """
        將 Job 設為 FAILED。

        同時由 Repository
        增加 retry_count。
        """

        if job_id is None:

            return False

        return self.repository.fail(
            job_id,
            error_message
        )

    # ==================================
    # Retry Job
    # ==================================

    def retry_job(
        self,
        job_id,
    ):
        """
        Retry FAILED Job。

        狀態：

            FAILED
                ↓
            WAITING

        retry_count 保留。
        """

        if job_id is None:

            return False

        job = self.repository.get_by_id(
            job_id
        )

        if job is None:

            return False

        if not job.can_retry:

            return False

        return self.repository.retry(
            job_id
        )

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        job_id,
    ):
        """
        判斷 Job 是否存在。
        """

        if job_id is None:

            return False

        return self.repository.exists(
            job_id
        )

    # ==================================
    # Count
    # ==================================

    def count(
        self,
    ):
        """
        取得 Job 總數。
        """

        return self.repository.count()

    # ==================================
    # Count By Status
    # ==================================

    def count_by_status(
        self,
        status,
    ):
        """
        取得指定 Status 的 Job 數量。
        """

        if not status:

            return 0

        return self.repository.count_by_status(
            status
        )


# ==================================
# Public API
# ==================================

__all__ = [
    "JobService",
]
