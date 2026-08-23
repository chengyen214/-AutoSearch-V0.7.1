"""
services/batch_job_service.py

AutoSearch V5

V5.5
P5.5.3

Batch Job Retrieval Service

用途：

    負責 Batch Runner 取得
    WAITING Jobs。

架構：

    BatchExecutionService
        ↓
    BatchJobService
        ↓
    JobRepository
        ↓
    WAITING Jobs

負責：

    - Job Retrieval
    - WAITING Job Retrieval
    - Repository delegation

不負責：

    - Batch Size 決策
    - Target Retrieval
    - Target Validation
    - Job Creation
    - Job Execution
    - Job Status Management
    - Search Provider
    - Search API
    - Crawler
    - Parser
    - Archive
    - AI Analysis


設計原則：

    BatchExecutionService
        負責：

            「這一批最多執行多少 Job？」

    BatchJobService
        負責：

            「目前有哪些 WAITING Job？」

    JobRepository
        負責：

            「從 Database 取得 WAITING Job。」

"""


from config.batch_config import BatchConfig
from database.job_repository import JobRepository


class BatchJobService:
    """
    V5 Batch Job Retrieval Service。

    P5.5.3

    負責：

        從 JobRepository 取得 WAITING Jobs。

    本 Service 不決定本次 Batch 執行數量。

    Batch Size 由：

        BatchExecutionService

    統一控制。
    """

    # ==================================
    # Constructor
    # ==================================

    def __init__(
        self,
        job_repository=None,
        batch_config=None,
    ):
        """
        建立 BatchJobService。

        Parameters
        ----------

        job_repository : JobRepository | None

            Job Persistence Layer。

            None：
                使用預設 JobRepository。

        batch_config : BatchConfig | None

            保留此參數以維持既有相容性。

            P5.5.5 起 Batch Size
            由 BatchExecutionService 控制。

            因此本 Service 不再使用
            batch_config 限制結果數量。
        """

        if job_repository is None:

            job_repository = (
                JobRepository()
            )

        if batch_config is None:

            batch_config = (
                BatchConfig()
            )

        self.job_repository = (
            job_repository
        )

        self.batch_config = (
            batch_config
        )

    # ==================================
    # Find Waiting Jobs
    # ==================================

    def find_waiting(self):
        """
        取得目前全部 WAITING Jobs。

        這是 BatchExecutionService
        使用的主要 Retrieval API。

        Flow：

            BatchExecutionService
                ↓
            BatchJobService.find_waiting()
                ↓
            JobRepository.find_waiting()
                ↓
            WAITING Jobs

        Returns
        -------

        list

            目前所有 WAITING Jobs。

        注意：

            本方法不：

                - 限制 Batch Size
                - 修改 Job
                - 改變 Job Status
                - 執行 Job
                - 取得 Target

            Batch Size 由：

                BatchExecutionService

            負責。
        """

        jobs = (
            self.job_repository.find_waiting()
        )

        if not jobs:

            return []

        return jobs

    # ==================================
    # Retrieve Waiting Jobs
    # ==================================

    def get_waiting_jobs(self):
        """
        取得 WAITING Jobs。

        相容 API。

        P5.5.3 原本此方法會同時執行
        Batch Size 限制。

        現在改由：

            BatchExecutionService

        統一負責 Batch Size。

        因此本方法等同於：

            find_waiting()
        """

        return self.find_waiting()

    # ==================================
    # Alias
    # ==================================

    def get_jobs(self):
        """
        get_waiting_jobs() Alias。

        取得目前 WAITING Jobs。

        Batch Size 不在此處限制。
        """

        return self.find_waiting()

    # ==================================
    # Count
    # ==================================

    def count_waiting_jobs(self):
        """
        取得目前 WAITING Job 數量。

        注意：

            這裡取得的是全部 WAITING Job 數量。

            不受 Batch Size 限制。
        """

        return (
            self.job_repository.count_by_status(
                "WAITING"
            )
        )


# ==================================
# Public API
# ==================================

__all__ = [
    "BatchJobService",
]
