"""
tests/V5/test_batch_target_retrieval.py

AutoSearch V5

V5.6.2

Batch Target Retrieval Test

用途：

    驗證：

        SQL Job
            ↓
        Job.target_id
            ↓
        BatchTargetService
            ↓
        TargetRepository
            ↓
        Target

本測試不執行：

    Search
    Crawl
    Parser
    Article
    Archive
    AI
    JobExecutorBridge
    BatchExecutionService

執行方式：

    python -m tests.V5.test_batch_target_retrieval
"""

# ==================================================
#
# Imports
#
# ==================================================

from services.batch_job_service import (
    BatchJobService,
)

from services.batch_target_service import (
    BatchTargetService,
)


# ==================================================
#
# Main Test
#
# ==================================================

def main():
    """
    測試從 SQL 取得 WAITING Job，
    再透過 Job.target_id 取得 Target。
    """

    print("=" * 70)
    print("AutoSearch V5")
    print("V5.6.2 Batch Target Retrieval Test")
    print("=" * 70)

    # ==================================================
    #
    # 建立 Service
    #
    # ==================================================

    job_service = (
        BatchJobService()
    )

    target_service = (
        BatchTargetService()
    )

    # ==================================================
    #
    # 取得 WAITING Jobs
    #
    # ==================================================

    print()
    print("[1] 取得 WAITING Jobs")
    print("-" * 70)

    jobs = (
        job_service.get_waiting_jobs()
    )

    if not jobs:

        print("❌ 找不到 WAITING Job")
        print()
        print("請確認 SQL jobs table 是否存在 WAITING Job。")
        return

    print(
        f"找到 {len(jobs)} 個 WAITING Job"
    )

    # ==================================================
    #
    # 逐一取得 Target
    #
    # ==================================================

    print()
    print("[2] Job → Target")
    print("-" * 70)

    for index, job in enumerate(
        jobs,
        start=1,
    ):

        print()
        print(
            f"Job #{index}"
        )

        print(
            f"  job.id        = {getattr(job, 'id', None)}"
        )

        print(
            f"  job.target_id = "
            f"{getattr(job, 'target_id', None)}"
        )

        # ----------------------------------------------
        # 取得 Target
        # ----------------------------------------------

        target = (
            target_service
            .get_target_for_job(
                job
            )
        )

        if target is None:

            print(
                "  ❌ Target = None"
            )

            continue

        # ----------------------------------------------
        # Target 基本資訊
        # ----------------------------------------------

        print(
            "  ✅ Target retrieved"
        )

        print(
            f"  target.id = "
            f"{getattr(target, 'id', None)}"
        )

        print(
            f"  target.target_type = "
            f"{getattr(target, 'target_type', None)}"
        )

        print(
            f"  target.url = "
            f"{getattr(target, 'url', None)}"
        )

        print(
            f"  target.keyword = "
            f"{getattr(target, 'keyword', None)}"
        )

        print(
            f"  target.search_provider = "
            f"{getattr(target, 'search_provider', None)}"
        )

        # ----------------------------------------------
        # 額外輸出 Target Object
        # ----------------------------------------------

        print()
        print(
            "  Target object:"
        )

        print(
            f"  {target!r}"
        )

    # ==================================================
    #
    # Finished
    #
    # ==================================================

    print()
    print("=" * 70)
    print("Test Finished")
    print("=" * 70)


# ==================================================
#
# Entry Point
#
# ==================================================

if __name__ == "__main__":

    main()