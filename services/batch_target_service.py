"""
services/batch_target_service.py

AutoSearch V5

V5.6.2
Batch Target Retrieval Service

用途：

    負責 BatchExecutionService 執行 Job 時，
    根據 Job 的 target_id 取得對應 Target。

架構：

    BatchExecutionService
        ↓
    BatchTargetService
        ↓
    TargetRepository
        ↓
    Target

V5.6.2 Pipeline：

    Job
        ↓
    target_id
        ↓
    BatchTargetService
        ↓
    Target
        ↓
    JobExecutorBridge
        ↓
    TargetSourceService

負責：

    - Job → Target
    - target_id → Target
    - Target Retrieval
    - TargetRepository delegation

不負責：

    - Target Creation
    - Target Validation
    - Target Deduplication
    - Job Creation
    - Job Execution
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

設計原則：

    BatchExecutionService
        負責：

            「這個 Job 要取得哪一個 Target？」

    BatchTargetService
        負責：

            「根據 Job.target_id 取得 Target。」

    JobExecutorBridge
        負責：

            「取得 Target 後，
             將 Target 接到 V5 Pipeline。」

因此：

    BatchTargetService
        不應知道：

            SourceResolutionBridge
            SearchExecutionBridge
            Provider
            ProviderSearchAdapter
            Crawler
            Parser
""" 


# ==================================================
#
# Target Repository
#
# ==================================================

from database.target_repository import (
    TargetRepository,
)


# ==================================================
#
# Job Model
#
# ==================================================

from models.job import (
    Job,
)


class BatchTargetService:
    """
    V5.6.2 Batch Target Retrieval Service。

    主要責任：

        Job
            ↓
        target_id
            ↓
        TargetRepository
            ↓
        Target

    Service 只負責 Target Retrieval。

    不負責：

        Target Validation
        Source Resolution
        Search
        Crawl
        Parser
    """

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        target_repository=None,
    ):
        """
        建立 BatchTargetService。

        Parameters
        ----------
        target_repository : TargetRepository | None

            可注入 TargetRepository，
            方便測試與未來替換 Persistence Layer。

            None：

                使用預設 TargetRepository。
        """

        if target_repository is None:

            target_repository = (
                TargetRepository()
            )

        self.target_repository = (
            target_repository
        )

    # ==================================================
    #
    # Get Target For Job
    #
    # ==================================================

    def get_target_for_job(
        self,
        job,
    ):
        """
        根據 Job 取得 Target。

        Pipeline：

            Job
                ↓
            target_id
                ↓
            BatchTargetService
                ↓
            TargetRepository
                ↓
            Target

        Parameters
        ----------
        job : Job

            要取得 Target 的 Job。

        Returns
        -------
        Target | None

            找到 Target：

                回傳 Target。

            Job 為 None：

                回傳 None。

            target_id 為 None：

                回傳 None。

            Target 不存在：

                回傳 None。

        Raises
        ------
        TypeError

            job 不是 Job instance。
        """

        # ----------------------------------------------
        # Job None
        # ----------------------------------------------

        if job is None:

            return None

        # ----------------------------------------------
        # Job Type Validation
        # ----------------------------------------------

        if not isinstance(
            job,
            Job,
        ):

            raise TypeError(
                "job must be an instance of Job"
            )

        # ----------------------------------------------
        # Target ID
        # ----------------------------------------------

        target_id = getattr(
            job,
            "target_id",
            None,
        )

        if target_id is None:

            return None

        # ----------------------------------------------
        # Repository Retrieval
        # ----------------------------------------------

        return self.get_target_by_id(
            target_id
        )

    # ==================================================
    #
    # Get Target By ID
    #
    # ==================================================

    def get_target_by_id(
        self,
        target_id,
    ):
        """
        根據 Target ID 取得 Target。

        Parameters
        ----------
        target_id : int

            Target Database ID。

        Returns
        -------
        Target | None

            找到：

                Target

            target_id 為 None：

                None

            Target 不存在：

                None

        注意：

            Persistence Layer 的實際查詢
            由 TargetRepository 負責。
        """

        if target_id is None:

            return None

        return (
            self.target_repository.get_by_id(
                target_id
            )
        )

    # ==================================================
    #
    # Get Target
    #
    # ==================================================

    def get_target(
        self,
        job,
    ):
        """
        get_target_for_job() Alias。

        等同：

            get_target_for_job(job)
        """

        return self.get_target_for_job(
            job
        )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "BatchTargetService",
]
