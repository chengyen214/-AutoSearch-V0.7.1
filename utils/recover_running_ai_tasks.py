"""
utils/recover_running_ai_tasks.py

AutoSearch V4

用途：
    將因為程序中斷而殘留的 RUNNING AI Tasks
    安全恢復為 WAITING。

執行：

    python -m utils.recover_running_ai_tasks
"""

from database.connection import get_connection


def main():

    print("=" * 70)
    print("AutoSearch V4 - Recover RUNNING AI Tasks")
    print("=" * 70)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # ==========================================
        # 查詢目前 RUNNING
        # ==========================================

        cursor.execute(
            """
            SELECT
                id,
                article_id,
                task_type,
                status,
                retry_count
            FROM ai_tasks
            WHERE status = 'RUNNING'
            ORDER BY id ASC
            """
        )

        tasks = cursor.fetchall()

        print()
        print(
            f"RUNNING Tasks Found : {len(tasks)}"
        )

        if not tasks:

            print(
                "No RUNNING tasks need recovery."
            )

            return

        print()

        for task in tasks:

            print(
                f"task={task['id']}, "
                f"article={task['article_id']}, "
                f"type={task['task_type']}, "
                f"retry={task['retry_count']}"
            )

        print()

        # ==========================================
        # RUNNING -> WAITING
        # ==========================================

        cursor.execute(
            """
            UPDATE ai_tasks
            SET status = 'WAITING'
            WHERE status = 'RUNNING'
            """
        )

        affected = cursor.rowcount

        conn.commit()

        print(
            f"Recovered Tasks : {affected}"
        )

        print(
            "RUNNING -> WAITING"
        )

        print()

    except Exception:

        conn.rollback()

        raise

    finally:

        cursor.close()
        conn.close()

    print("=" * 70)
    print("Recovery completed")
    print("=" * 70)


if __name__ == "__main__":

    main()