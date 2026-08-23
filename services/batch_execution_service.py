"""
services/batch_execution_service.py

AutoSearch V5

V5.6.2
P5.6 Batch Execution Foundation

Batch Execution Service

用途：

    執行一批 WAITING Job。

架構：

    BatchExecutionService
        ↓
    BatchConfig
        ↓
    BatchJobService
        ↓
    WAITING Jobs
        ↓
    Batch Size
        ↓
    BatchTargetService
        ↓
    Target
        ↓
    BatchJobStatusService
        ↓
    RUNNING
        ↓
    JobExecutorBridge
        ↓
    TargetSourceService
        ↓
    Source Definition
        ↓
    SourceResolutionBridge
        ↓
    Resolved Source

P5.6.2：

    Job
      ↓
    JobExecutorBridge
      ↓
    TargetSourceService
      ↓
    Source Definition
      ↓
    SourceResolutionBridge
      ↓
    Resolved Source

注意：

    P5.6.2 尚未執行實際 Search。

    SearchExecutionBridge
    屬於後續 P5.6.3 Pipeline。

負責：

    - Batch Execution Orchestration
    - Batch Job Retrieval
    - Batch Size Control
    - Target Retrieval
    - Job Lifecycle
    - Executor Delegation
    - Execution Result Handling

不負責：

    - Target Validation
    - Target Creation
    - Target Deduplication
    - Search Provider
    - Search API
    - SearchAdapter
    - Source Resolution
    - Search Execution
    - Crawler
    - Parser
    - Archive
    - AI Analysis
    - Retry Policy
    - Scheduler
    - Web UI
"""


# ==================================================
#
# Batch Configuration
#
# ==================================================

from config.batch_config import (
    BatchConfig,
)


# ==================================================
#
# Batch Job Service
#
# ==================================================

from services.batch_job_service import (
    BatchJobService,
)


# ==================================================
#
# Batch Target Service
#
# ==================================================

from services.batch_target_service import (
    BatchTargetService,
)


# ==================================================
#
# Batch Job Status Service
#
# ==================================================

from services.batch_job_status_service import (
    BatchJobStatusService,
)


# ==================================================
#
# Job Executor Bridge
#
# ==================================================

from services.job_executor_bridge import (
    JobExecutorBridge,
)


class BatchExecutionService:
    """
    V5.6 Batch Execution Service。

    主要責任：

        1. 取得 WAITING Jobs
        2. 套用 Batch Size
        3. 取得 Job 對應 Target
        4. 將 Job 設為 RUNNING
        5. 呼叫 JobExecutorBridge
        6. 處理 Executor 結果
        7. 更新 Job Status
        8. 回傳 Batch Execution Result

    P5.6.2 Pipeline：

        Job
          ↓
        Target
          ↓
        JobExecutorBridge
          ↓
        TargetSourceService
          ↓
        Source Definition
          ↓
        SourceResolutionBridge
          ↓
        Resolved Source

    注意：

        本 Service 不直接處理：

            Search
            SearchExecutionBridge
            Crawl
            Parser
            Article
            Archive
            AI
    """

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        batch_config=None,
        job_service=None,
        target_service=None,
        status_service=None,
        executor=None,
    ):
        """
        建立 BatchExecutionService。

        Parameters
        ----------
        batch_config : BatchConfig | None

            Batch Configuration。

            負責：

                Batch Size

        job_service : BatchJobService | None

            WAITING Job Retrieval Service。

        target_service : BatchTargetService | None

            Job → Target Retrieval Service。

        status_service : BatchJobStatusService | None

            Job Lifecycle / Status Service。

        executor : callable | object | None

            Job Executor。

            Signature：

                executor(job, target)

            或：

                executor.execute(job, target)

            P5.6.2 預設：

                JobExecutorBridge.execute()

            JobExecutorBridge 負責：

                Job
                  ↓
                Target
                  ↓
                TargetSourceService
                  ↓
                Source Definition
                  ↓
                SourceResolutionBridge
                  ↓
                Resolved Source

            注意：

                此 Executor 尚不代表實際 Search
                或 Crawl 已完成。
        """

        # ==================================================
        #
        # Batch Config
        #
        # ==================================================

        if batch_config is None:

            batch_config = BatchConfig()

        self.batch_config = (
            batch_config
        )

        # ==================================================
        #
        # Job Service
        #
        # ==================================================

        if job_service is None:

            job_service = BatchJobService(
                batch_config=self.batch_config,
            )

        self.job_service = (
            job_service
        )

        # ==================================================
        #
        # Target Service
        #
        # ==================================================

        if target_service is None:

            target_service = (
                BatchTargetService()
            )

        self.target_service = (
            target_service
        )

        # ==================================================
        #
        # Status Service
        #
        # ==================================================

        if status_service is None:

            status_service = (
                BatchJobStatusService()
            )

        self.status_service = (
            status_service
        )

        # ==================================================
        #
        # Executor
        #
        # ==================================================

        if executor is None:

            executor = (
                JobExecutorBridge()
            )

        self.executor = (
            executor
        )

    # ==================================================
    #
    # Batch Size
    #
    # ==================================================

    def get_batch_size(self):
        """
        取得目前 Batch Size。

        Batch Size 由 BatchConfig 控制。

        Returns
        -------

        int

            本次 Batch 最多執行的 Job 數量。
        """

        batch_size = (
            self.batch_config.get_batch_size()
        )

        try:

            batch_size = int(
                batch_size
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "batch_size must be "
                "a positive integer"
            )

        if batch_size <= 0:

            raise ValueError(
                "batch_size must be "
                "greater than zero"
            )

        return batch_size

    # ==================================================
    #
    # Job Retrieval
    #
    # ==================================================

    def get_waiting_jobs(self):
        """
        取得目前 WAITING Jobs。

        注意：

            BatchJobService 負責：

                「有哪些 WAITING Jobs？」

            BatchExecutionService 負責：

                「本批最多執行多少 Jobs？」

        因此本方法：

            1. 先取得全部 WAITING Jobs
            2. 再套用 Batch Size
        """

        jobs = (
            self.job_service
            .get_waiting_jobs()
        )

        if not jobs:

            return []

        batch_size = (
            self.get_batch_size()
        )

        return list(
            jobs[:batch_size]
        )

    # ==================================================
    #
    # Target Retrieval
    #
    # ==================================================

    def get_target_for_job(
        self,
        job,
    ):
        """
        取得 Job 對應 Target。

        Flow：

            Job
             ↓
            target_id
             ↓
            BatchTargetService
             ↓
            TargetRepository
             ↓
            Target
        """

        if job is None:

            return None

        return (
            self.target_service
            .get_target_for_job(
                job
            )
        )

    # ==================================================
    #
    # Execute One Job
    #
    # ==================================================

    def execute_job(
        self,
        job,
    ):
        """
        執行單一 Job。

        P5.6.2 Flow：

            WAITING
                ↓
            Target
                ↓
            RUNNING
                ↓
            JobExecutorBridge
                ↓
            TargetSourceService
                ↓
            Source Definition
                ↓
            SourceResolutionBridge
                ↓
            Resolved Source
                ↓
            DONE / FAILED

        注意：

            本方法不直接執行：

                SearchExecutionBridge
                adapter.search()
                Crawler
                Parser
                Article

        Returns
        -------

        bool

            True：

                Executor 成功。

            False：

                Executor 失敗。
        """

        # ==================================================
        #
        # Validate Job
        #
        # ==================================================

        if job is None:

            return False

        if not hasattr(
            job,
            "id",
        ):

            return False

        if job.id is None:

            return False

        # ==================================================
        #
        # Retrieve Target
        #
        # ==================================================

        target = (
            self.get_target_for_job(
                job
            )
        )

        if target is None:

            self.status_service.fail_job(
                job.id,
                "Target not found",
            )

            return False

        # ==================================================
        #
        # Start Job
        #
        # ==================================================

        started = (
            self.status_service.start_job(
                job.id
            )
        )

        if not started:

            return False

        # ==================================================
        #
        # Executor Validation
        #
        # ==================================================

        if self.executor is None:

            self.status_service.fail_job(
                job.id,
                "Job executor is not configured",
            )

            return False

        # ==================================================
        #
        # Execute
        #
        # ==================================================

        try:

            # ----------------------------------------------
            # Callable Executor
            # ----------------------------------------------

            if callable(
                self.executor
            ):

                result = self.executor(
                    job,
                    target,
                )

            # ----------------------------------------------
            # Object Executor
            # ----------------------------------------------

            elif callable(
                getattr(
                    self.executor,
                    "execute",
                    None,
                )
            ):

                result = (
                    self.executor.execute(
                        job,
                        target,
                    )
                )

            # ----------------------------------------------
            # Invalid Executor
            # ----------------------------------------------

            else:

                self.status_service.fail_job(
                    job.id,
                    "Invalid job executor",
                )

                return False

        except Exception as exc:

            self.status_service.fail_job(
                job.id,
                str(exc),
            )

            return False

        # ==================================================
        #
        # Executor Result
        #
        # ==================================================

        if result is False or result is None:

            self.status_service.fail_job(
                job.id,
                "Job execution failed",
            )

            return False

        # ==================================================
        #
        # Success
        #
        # ==================================================

        completed = (
            self.status_service
            .complete_job(
                job.id
            )
        )

        return completed

    # ==================================================
    #
    # Execute Batch
    #
    # ==================================================

    def execute_batch(self):
        """
        執行一批 WAITING Jobs。

        Batch Size 由本 Service 控制。

        Flow：

            WAITING Jobs
                ↓
            Batch Size
                ↓
            Job 1
                ↓
            Target
                ↓
            RUNNING
                ↓
            JobExecutorBridge
                ↓
            TargetSourceService
                ↓
            Source Definition
                ↓
            SourceResolutionBridge
                ↓
            Resolved Source
                ↓
            DONE / FAILED

        Returns
        -------

        dict

            {
                "total": int,
                "success": int,
                "failed": int,
            }
        """

        # ==================================================
        #
        # Get Batch Jobs
        #
        # ==================================================

        jobs = (
            self.get_waiting_jobs()
        )

        total = len(
            jobs
        )

        success = 0

        failed = 0

        # ==================================================
        #
        # Execute Jobs
        #
        # ==================================================

        for job in jobs:

            result = (
                self.execute_job(
                    job
                )
            )

            if result:

                success += 1

            else:

                failed += 1

        # ==================================================
        #
        # Result
        #
        # ==================================================

        return {
            "total": total,
            "success": success,
            "failed": failed,
        }

    # ==================================================
    #
    # Run
    #
    # ==================================================

    def run(self):
        """
        Batch Runner Entry。

        等同：

            execute_batch()

        P5.6.2：

            Job
              ↓
            Target
              ↓
            Source Definition
              ↓
            Resolved Source

        尚未執行：

            Search
            Crawl
            Parser
            Article
            Archive
            AI
        """

        return (
            self.execute_batch()
        )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "BatchExecutionService",
]