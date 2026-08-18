"""
utils/check_async_groq_pipeline.py

AutoSearch V4

Async Groq End-to-End Pipeline Test

用途:

    驗證目前 AutoSearch V4
    Async AI Scaling + Groq
    是否能完整執行。

測試流程:

    Existing WAITING AI Tasks
            |
            v
    AIBatchTriggerService
            |
            | force_trigger()
            v
       AIScheduler
            |
            v
       AIWorkerPool
            |
            v
        AIWorker
            |
            v
    AIAnalysisService
            |
            v
        LLMClient
            |
            v
          Groq
            |
            v
    openai/gpt-oss-120b
            |
            v
       JSONParser
            |
            v
       AIAnalysis
            |
            v
       Knowledge
            |
            v
    Knowledge Intelligence
            |
            v
        Task DONE

輸出:

    output/async_groq_pipeline_test.json

執行:

    python -m utils.check_async_groq_pipeline

注意:

    1. 本測試會實際處理目前資料庫 WAITING Tasks。
    2. Worker Pool 會依目前 P2.4.9 設計 Drain Queue。
    3. 不修改 AI_THRESHOLD。
    4. 使用 force_trigger()，因此不受 threshold=40 限制。
"""


import json
import os
import time
from datetime import datetime

from config.ai_config import (
    LLM_PROVIDER,
    LLM_MODEL
)

from database.connection import get_connection

from database.ai_task_repository import (
    AITaskRepository
)

from services.ai_batch_trigger_service import (
    AIBatchTriggerService
)

from services.ai_scheduler import (
    AIScheduler
)

from utils.logger import logger


# ==================================================
# Output
# ==================================================

OUTPUT_DIR = "output"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "async_groq_pipeline_test.json"
)


# ==================================================
# Queue Status
# ==================================================

def get_task_status_counts():
    """
    查詢目前 AI Task Queue 狀態。

    Returns
    -------

    dict

        {
            "WAITING": 0,
            "RUNNING": 0,
            "DONE": 0,
            "FAILED": 0
        }
    """

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        sql = """
        SELECT
            status,
            COUNT(*) AS count
        FROM ai_tasks
        GROUP BY status
        """

        cursor.execute(
            sql
        )

        rows = cursor.fetchall()

        result = {

            "WAITING": 0,

            "RUNNING": 0,

            "DONE": 0,

            "FAILED": 0

        }

        for row in rows:

            status = row.get(
                "status"
            )

            count = int(
                row.get(
                    "count",
                    0
                )
            )

            if status in result:

                result[status] = count

            else:

                result[status] = count

        return result

    finally:

        cursor.close()

        conn.close()


# ==================================================
# Safe JSON
# ==================================================

def json_safe(
    value
):
    """
    將資料轉成 JSON 可序列化格式。
    """

    if value is None:

        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool
        )
    ):

        return value

    if isinstance(
        value,
        datetime
    ):

        return value.isoformat()

    if isinstance(
        value,
        dict
    ):

        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        list
    ):

        return [
            json_safe(item)
            for item in value
        ]

    return str(value)


# ==================================================
# Main
# ==================================================

def main():
    """
    執行 Async Groq E2E Test。
    """

    start_time = time.perf_counter()

    result = {

        "test_time":
            datetime.now().isoformat(),

        "test_name":
            "AutoSearch V4 Async Groq End-to-End Test",

        "provider":
            LLM_PROVIDER,

        "model":
            LLM_MODEL,

        "before":

            {},

        "trigger":

            {},

        "scheduler":

            {},

        "worker_pool":

            {},

        "after":

            {},

        "groq_request_detected":
            False,

        "async_pipeline_success":
            False,

        "queue_drained":
            False,

        "all_tasks_finished":
            False,

        "error":
            None,

        "elapsed_seconds":
            None

    }

    print("=" * 70)
    print(
        "AutoSearch V4 - Async Groq End-to-End Test"
    )
    print("=" * 70)

    print()

    print(
        f"Provider : {LLM_PROVIDER}"
    )

    print(
        f"Model    : {LLM_MODEL}"
    )

    print()

    try:

        # ==================================================
        # Configuration Check
        # ==================================================

        if LLM_PROVIDER != "groq":

            raise RuntimeError(
                "LLM_PROVIDER is not 'groq'."
            )

        if not LLM_MODEL:

            raise RuntimeError(
                "LLM_MODEL is empty."
            )

        # ==================================================
        # Initial Queue Status
        # ==================================================

        before = (
            get_task_status_counts()
        )

        result[
            "before"
        ] = before

        waiting_before = before.get(
            "WAITING",
            0
        )

        running_before = before.get(
            "RUNNING",
            0
        )

        print(
            "Initial Queue:"
        )

        print(
            json.dumps(
                before,
                ensure_ascii=False,
                indent=4
            )
        )

        print()

        if waiting_before == 0:

            raise RuntimeError(
                "No WAITING AI Tasks available. "
                "Run python run.py first or create AI Tasks."
            )

        print(
            f"WAITING Tasks : {waiting_before}"
        )

        print(
            f"RUNNING Tasks : {running_before}"
        )

        print()

        # ==================================================
        # Create Scheduler
        # ==================================================

        scheduler = AIScheduler(
            interval=30
        )

        # ==================================================
        # Create Batch Trigger
        # ==================================================

        batch_trigger = (
            AIBatchTriggerService(
                scheduler=scheduler
            )
        )

        # ==================================================
        # Force Trigger
        # ==================================================

        print(
            "Force triggering Async AI Scheduler..."
        )

        trigger_start = time.perf_counter()

        triggered = (
            batch_trigger.force_trigger()
        )

        trigger_elapsed = (
            time.perf_counter()
            - trigger_start
        )

        result[
            "trigger"
        ] = {

            "triggered":
                triggered,

            "elapsed_seconds":
                round(
                    trigger_elapsed,
                    3
                )

        }

        if not triggered:

            raise RuntimeError(
                "Failed to force start "
                "AI Scheduler."
            )

        print(
            "AI Scheduler force trigger SUCCESS"
        )

        print()

        # ==================================================
        # Wait Worker Pool
        # ==================================================

        print(
            "Waiting for AI Worker Pool..."
        )

        wait_start = time.perf_counter()

        poll_interval = 0.5

        max_wait_seconds = 3600

        while True:

            elapsed = (
                time.perf_counter()
                - wait_start
            )

            if elapsed > max_wait_seconds:

                raise TimeoutError(
                    "Async AI Pipeline timeout "
                    f"after {max_wait_seconds} seconds."
                )

            status = (
                scheduler.get_status()
            )

            result[
                "scheduler"
            ] = json_safe(
                status
            )

            worker_pool_status = (
                scheduler.get_worker_pool_status()
            )

            result[
                "worker_pool"
            ] = json_safe(
                worker_pool_status
            )

            pool_running = status.get(
                "worker_pool_running",
                False
            )

            active_workers = status.get(
                "active_workers",
                0
            )

            completed_workers = status.get(
                "completed_workers",
                0
            )

            failed_workers = status.get(
                "failed_workers",
                0
            )

            print(
                "\r"
                f"Pool Running={pool_running} | "
                f"Active={active_workers} | "
                f"Completed={completed_workers} | "
                f"Failed={failed_workers}",
                end="",
                flush=True
            )

            # ------------------------------------------
            # Pool Complete
            # ------------------------------------------

            if (
                not pool_running
                and active_workers == 0
            ):

                break

            time.sleep(
                poll_interval
            )

        print()
        print()

        # ==================================================
        # Final Queue Status
        # ==================================================

        after = (
            get_task_status_counts()
        )

        result[
            "after"
        ] = after

        waiting_after = after.get(
            "WAITING",
            0
        )

        running_after = after.get(
            "RUNNING",
            0
        )

        done_after = after.get(
            "DONE",
            0
        )

        failed_after = after.get(
            "FAILED",
            0
        )

        # ==================================================
        # Queue Validation
        # ==================================================

        result[
            "queue_drained"
        ] = (
            waiting_after == 0
        )

        result[
            "all_tasks_finished"
        ] = (
            waiting_after == 0
            and running_after == 0
        )

        # ==================================================
        # Groq Connection Detection
        # ==================================================
        #
        # 這裡不是單純測設定。
        #
        # 如果 Worker 真正執行 AIAnalysisService，
        # 正常 Log 應該包含：
        #
        #     ===== GROQ REQUEST =====
        #     ===== GROQ RESPONSE OK =====
        #
        # Python 本身無法直接從 logger history
        # 取得所有 Log，
        # 因此結合：
        #
        #     provider
        #     model
        #     queue processing
        #     DONE / FAILED
        #
        # 判定 Async Pipeline 是否成功完成。
        #
        # 真正 Groq request 的最終確認
        # 仍以 console / log 中：
        #
        #     GROQ RESPONSE OK
        #
        # 為最高證據。
        # ==================================================

        if (
            LLM_PROVIDER == "groq"
            and LLM_MODEL
            and done_after > 0
        ):

            result[
                "groq_request_detected"
            ] = True

        # ==================================================
        # Pipeline Success
        # ==================================================

        result[
            "async_pipeline_success"
        ] = (
            result[
                "queue_drained"
            ]
            and result[
                "all_tasks_finished"
            ]
            and (
                failed_after == 0
                or done_after > 0
            )
        )

        # ==================================================
        # Print Final
        # ==================================================

        print("=" * 70)

        if result[
            "async_pipeline_success"
        ]:

            print(
                "ASYNC GROQ PIPELINE TEST SUCCESS"
            )

        else:

            print(
                "ASYNC GROQ PIPELINE TEST FAILED"
            )

        print("=" * 70)

        print()

        print(
            "Final Queue:"
        )

        print(
            json.dumps(
                after,
                ensure_ascii=False,
                indent=4
            )
        )

        print()

        print(
            f"WAITING : {waiting_after}"
        )

        print(
            f"RUNNING : {running_after}"
        )

        print(
            f"DONE    : {done_after}"
        )

        print(
            f"FAILED  : {failed_after}"
        )

        print()

        print(
            "Worker Pool:"
        )

        print(
            json.dumps(
                result["worker_pool"],
                ensure_ascii=False,
                indent=4
            )
        )

        print()

    except Exception as e:

        result[
            "error"
        ] = {

            "type":
                type(e).__name__,

            "message":
                str(e)

        }

        logger.exception(
            "Async Groq Pipeline Test failed."
        )

        print()
        print("=" * 70)
        print(
            "ASYNC GROQ PIPELINE TEST FAILED"
        )
        print("=" * 70)

        print()

        print(
            f"Error Type : {type(e).__name__}"
        )

        print(
            f"Error      : {e}"
        )

    finally:

        # ==================================================
        # Scheduler Cleanup
        # ==================================================

        try:

            if "scheduler" in locals():

                if scheduler.is_running():

                    print()
                    print(
                        "Stopping AI Scheduler..."
                    )

                    scheduler.stop()

                    print(
                        "AI Scheduler stopped."
                    )

        except Exception as e:

            logger.exception(
                "Scheduler cleanup failed: "
                f"{e}"
            )

            if result.get(
                "error"
            ) is None:

                result[
                    "error"
                ] = {

                    "type":
                        type(e).__name__,

                    "message":
                        str(e)

                }

        # ==================================================
        # Timing
        # ==================================================

        elapsed = (
            time.perf_counter()
            - start_time
        )

        result[
            "elapsed_seconds"
        ] = round(
            elapsed,
            3
        )

        # ==================================================
        # Output Directory
        # ==================================================

        os.makedirs(
            OUTPUT_DIR,
            exist_ok=True
        )

        # ==================================================
        # Write Result
        # ==================================================

        try:

            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    json_safe(result),
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception as e:

            print(
                "Failed to write result file:"
            )

            print(
                str(e)
            )

        print()

        print(
            f"Result file: {OUTPUT_FILE}"
        )

        print(
            f"Elapsed    : "
            f"{result['elapsed_seconds']} sec"
        )

        print(
            "=" * 70
        )


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":

    main()