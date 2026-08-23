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


    但：

        WAITING / RUNNING

    不重複建立。


    DONE:

        允許下一輪巡檢重新建立。


負責:

    - 查詢 active targets
    - 判斷是否已有執行中 Job
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
    # Create Jobs
    # ==================================================

    def create_pending_jobs(self):
        """
        將所有 active Target
        建立 WAITING Job。

        自動巡檢模式：

            DONE Job

        不會阻擋下一次建立。

        只有：

            WAITING
            RUNNING

        會阻擋。
        """

        targets = (
            self.target_repository
            .find_active()
        )


        created_jobs = []


        for target in targets:


            if self.has_active_job(
                target.id
            ):
                continue


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
    # Create Single Job
    # ==================================================

    def create_job(
        self,
        target_id,
    ):
        """
        建立單一 Target Job。
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
    # Check Active Job
    # ==================================================

    def has_active_job(
        self,
        target_id,
    ):
        """
        判斷 Target 是否已有執行中 Job。


        阻擋：

            WAITING
            RUNNING


        不阻擋：

            DONE
            FAILED


        自動巡檢模式：

            DONE 可以重新建立新的 Job。
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
    # Check Waiting
    # ==================================================

    def has_waiting_job(
        self,
        target_id,
    ):
        """
        保留相容 API。

        判斷是否存在 WAITING Job。
        """

        jobs = (
            self.job_repository
            .find_waiting_by_target(
                target_id
            )
        )


        return len(jobs) > 0



    # ==================================================
    # Refresh
    # ==================================================

    def refresh_jobs(self):
        """
        Alias:

            create_pending_jobs()
        """

        return (
            self.create_pending_jobs()
        )



__all__ = [
    "TargetJobService",
]