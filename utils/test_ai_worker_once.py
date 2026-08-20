"""
utils/test_ai_worker_once.py

AutoSearch V4

P2.4 One-Shot AI Worker Test

用途：
    一次性測試 AI Worker Queue Drain。

測試架構：

    AIWorkerPool
        |
        +--> Worker = 1
        |
        v
    AIWorker.run_once()
        |
        +--> Claim WAITING Tasks
        |
        +--> Process AI Analysis
        |
        +--> Groq
        |
        +--> Knowledge
        |
        +--> Search Index
        |
        +--> DONE
        |
        v
    WAITING Queue Empty

注意：
    不啟動 AIScheduler
    不啟動 run.py
    不建立 Background Scheduler

執行：

    python -m utils.test_ai_worker_once
"""

from services.ai_worker_pool import AIWorkerPool
from ai.worker import AIWorker

from utils.logger import logger


def main():
    """
    一次性執行 AI Worker Pool。
    """

    print()
    print("=" * 60)
    print("AutoSearch V4 - One Shot AI Worker Test")
    print("=" * 60)

    # ==================================================
    # Worker Configuration
    # ==================================================

    worker_count = 1

    print()
    print(f"Worker Count : {worker_count}")
    print("Batch Limit  : 10")
    print()

    # ==================================================
    # Create Worker Pool
    # ==================================================

    pool = AIWorkerPool(
        worker_count=worker_count,
        worker_class=AIWorker
    )

    print("Worker Pool created.")
    print()

    # ==================================================
    # Before Status
    # ==================================================

    print("-" * 60)
    print("BEFORE")
    print("-" * 60)

    print(
        f"Worker Count      : "
        f"{pool.get_worker_count()}"
    )

    print(
        f"Active Workers    : "
        f"{pool.get_active_worker_count()}"
    )

    print(
        f"Completed Workers : "
        f"{pool.get_completed_worker_count()}"
    )

    print(
        f"Failed Workers    : "
        f"{pool.get_failed_worker_count()}"
    )

    print()

    # ==================================================
    # Start Pool
    # ==================================================

    print("-" * 60)
    print("STARTING WORKER")
    print("-" * 60)

    started = pool.start()

    if not started:

        print()
        print("ERROR: Worker Pool failed to start.")
        print()

        return 1

    print()
    print("Worker Pool started.")
    print()

    # ==================================================
    # Wait Until Worker Finished
    # ==================================================

    print("-" * 60)
    print("WAITING FOR QUEUE DRAIN")
    print("-" * 60)

    pool.join()

    # ==================================================
    # Final Status
    # ==================================================

    status = pool.get_status()

    print()
    print("-" * 60)
    print("AFTER")
    print("-" * 60)

    print(
        f"Running           : "
        f"{status.get('running')}"
    )

    print(
        f"Lifecycle Complete: "
        f"{status.get('lifecycle_completed')}"
    )

    print(
        f"Worker Count      : "
        f"{status.get('worker_count')}"
    )

    print(
        f"Active Workers    : "
        f"{status.get('active_workers')}"
    )

    print(
        f"Completed Workers : "
        f"{status.get('completed_workers')}"
    )

    print(
        f"Failed Workers    : "
        f"{status.get('failed_workers')}"
    )

    print()

    # ==================================================
    # Final Result
    # ==================================================

    if (
        status.get("lifecycle_completed")
        and status.get("failed_workers", 0) == 0
    ):

        print("=" * 60)
        print("AI WORKER TEST COMPLETED")
        print("=" * 60)
        print()
        print("Worker Count : 1")
        print("Queue Drain  : Completed")
        print()
        print("請再檢查資料庫：")
        print()
        print("WAITING = 0")
        print("RUNNING = 0")
        print("DONE    = 原 WAITING 數量")
        print()

        return 0

    # ==================================================
    # Failure
    # ==================================================

    print("=" * 60)
    print("AI WORKER TEST FINISHED WITH FAILURE")
    print("=" * 60)
    print()

    return 1


if __name__ == "__main__":

    try:

        exit_code = main()

    except KeyboardInterrupt:

        print()
        print("KeyboardInterrupt received.")

        exit_code = 130

    except Exception as e:

        logger.exception(
            "One-shot AI Worker test failed."
        )

        print()
        print(
            f"ERROR: {e}"
        )

        exit_code = 1

    raise SystemExit(
        exit_code
    )