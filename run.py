"""
run.py

AutoSearch V5

V5.6.3

Batch Runner Entry Point


用途：

    使用者只需要執行：

        python run.py


啟動流程：


    Target
        |
        ▼
    TargetJobService
        |
        ▼
    jobs(WAITING)
        |
        ▼
    BatchExecutionService
        |
        ▼
    JobExecutorBridge
        |
        ▼
    TargetSourceService
        |
        ▼
    Source Definition
        |
        ▼
    SourceResolutionBridge
        |
        ▼
    Search / Crawl Pipeline


Auto巡檢模式：

    每次 run:

        1.
        檢查 active targets


        2.
        自動建立 WAITING jobs


        3.
        執行 WAITING jobs



本檔案負責：

    ✔ Application Entry
    ✔ Target Job Refresh
    ✔ Batch Execution Start


本檔案不負責：

    - Target Validation
    - Target CRUD
    - Source Resolution
    - Search Provider
    - SearchAdapter
    - SearchExecution
    - Crawler
    - Parser
    - Article
    - Archive
    - AI

"""


# ==================================================
#
# Repository
#
# ==================================================

from database.target_repository import (
    TargetRepository,
)


from database.job_repository import (
    JobRepository,
)



# ==================================================
#
# Target Job Service
#
# ==================================================

from services.target_job_service import (
    TargetJobService,
)



# ==================================================
#
# Batch Execution Service
#
# ==================================================

from services.batch_execution_service import (
    BatchExecutionService,
)



# ==================================================
#
# Job Executor Bridge
#
# ==================================================

from services.job_executor_bridge import (
    JobExecutorBridge,
)



def main():
    """
    AutoSearch V5 Runner。


    Flow:


        targets

            ↓

        TargetJobService

            ↓

        jobs WAITING

            ↓

        BatchExecutionService

            ↓

        JobExecutorBridge

            ↓

        Search / Crawl Pipeline


    Returns:

        Batch Execution Result

    """


    # ==================================================
    #
    # Repository
    #
    # ==================================================

    target_repository = (
        TargetRepository()
    )


    job_repository = (
        JobRepository()
    )



    # ==================================================
    #
    # Auto Target Inspection
    #
    # ==================================================

    target_job_service = (
        TargetJobService(
            target_repository,
            job_repository,
        )
    )


    created_jobs = (
        target_job_service
        .create_pending_jobs()
    )


    print(
        "Auto Target Inspection:"
    )


    print(
        f"Created WAITING Jobs: {len(created_jobs)}"
    )



    # ==================================================
    #
    # Job Executor
    #
    # ==================================================

    executor = (
        JobExecutorBridge()
    )



    # ==================================================
    #
    # Batch Execution
    #
    # ==================================================

    batch_service = (
        BatchExecutionService(
            executor=executor,
        )
    )



    # ==================================================
    #
    # Execute Jobs
    #
    # ==================================================

    return (
        batch_service.run()
    )



# ==================================================
#
# Application Entry Point
#
# ==================================================

if __name__ == "__main__":


    result = main()


    print(
        ""
    )


    print(
        "AutoSearch V5 Batch Result:"
    )


    print(
        result
    )