"""
services/target_job_service.py

AutoSearch V5

P5.6.3

Target Job Creation Service


用途：

    將 active Target 自動轉換成 Job。


Pipeline:

    targets
        |
        ▼
    TargetJobService
        |
        ▼
    jobs
        |
        ▼
    BatchExecutionService


自動巡檢模式：

    每次 run.py 啟動：

        active Target
              |
              ▼
        建立新的 WAITING Job


    Job 建立規則：

        只要 Target = active
        就建立新的 WAITING Job。

        不判斷：

            WAITING
            RUNNING
            DONE
            FAILED

        也就是：

            同一個 Target
                ↓
            可以存在多個 Job。


負責:

    - 查詢 active targets
    - 建立 WAITING Job


不負責:

    - Target Resolution
    - Search Provider
    - Google Search
    - Google News
    - SearchAdapter
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Job Execution

"""


from models.job import Job


class TargetJobService:
    """
    Target → Job Service

    自動巡檢模式：

        Target
          ↓
        Job
          ↓
        BatchExecutionService

    Job Creation Policy：

        active Target
            ↓
        每次建立新的 WAITING Job

    不檢查既有 Job。
    """

    def __init__(
        self,
        target_repository,
        job_repository,
    ):

        self.target_repository = (
            target_repository
        )

        self.job_repository = (
            job_repository
        )


    # ==================================================
    #
    # Create Jobs
    #
    # ==================================================

    def create_pending_jobs(self):
        """
        將所有 active Target
        建立 WAITING Job。

        Job 建立規則：

            只要 Target 是 active
            就建立新的 Job。

        不判斷 Target 是否已有：

            WAITING
            RUNNING
            DONE
            FAILED

        因此：

            同一個 Target
                ↓
            可以建立多個 Job。
        """

        targets = (
            self.target_repository
            .find_active()
        )


        created_jobs = []


        for target in targets:

            # ------------------------------------------
            #
            # 直接建立新的 WAITING Job
            #
            # 不檢查既有 Job
            #
            # ------------------------------------------

            job = Job(
                target_id=target.id
            )


            job = (
                self.job_repository
                .save(job)
            )


            created_jobs.append(
                job
            )


        return created_jobs


    # ==================================================
    #
    # Create Single Job
    #
    # ==================================================

    def create_job(
        self,
        target_id,
    ):
        """
        建立單一 Target Job。

        不判斷 Target 是否已有其他 Job。
        """

        if target_id is None:

            raise ValueError(
                "target_id cannot be None"
            )


        target = (
            self.target_repository
            .get_by_id(target_id)
        )


        if target is None:

            raise ValueError(
                f"Target not found: {target_id}"
            )


        job = Job(
            target_id=target_id
        )


        return (
            self.job_repository
            .save(job)
        )


    # ==================================================
    #
    # Check Active Job
    #
    # ==================================================

    def has_active_job(
        self,
        target_id,
    ):
        """
        查詢 Target 是否存在 WAITING / RUNNING Job。

        注意：

            此方法保留作為相容 API。

            create_pending_jobs()
            已經不再使用此判斷。

        因此：

            即使存在 WAITING / RUNNING Job，
            create_pending_jobs() 仍然會建立新的 Job。
        """

        jobs = (
            self.job_repository
            .find_by_target_id(
                target_id
            )
        )


        for job in jobs:

            if job.status in [

                Job.STATUS_WAITING,

                Job.STATUS_RUNNING,

            ]:

                return True


        return False


    # ==================================================
    #
    # Check Waiting
    #
    # ==================================================

    def has_waiting_job(
        self,
        target_id,
    ):
        """
        保留相容 API。

        判斷是否存在 WAITING Job。

        注意：

            此方法不會影響
            create_pending_jobs() 的 Job 建立。
        """

        jobs = (
            self.job_repository
            .find_waiting_by_target(
                target_id
            )
        )


        return len(jobs) > 0


    # ==================================================
    #
    # Refresh
    #
    # ==================================================

    def refresh_jobs(self):
        """
        Alias：

            create_pending_jobs()
        """

        return (
            self.create_pending_jobs()
        )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "TargetJobService",
]