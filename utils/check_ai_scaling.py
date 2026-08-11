"""
utils/check_ai_scaling.py

AutoSearch V4

P2.4 Async AI Scaling Check

用途：

1. 檢查 articles 數量
2. 檢查 ai_tasks 數量
3. 檢查 WAITING AI Tasks
4. 檢查 AI Task Status
5. 判斷是否達到 Async AI Scaling Threshold

執行：

python -m utils.check_ai_scaling
"""

from database.connection import (
    get_connection
)


from config.settings import (
    AI_THRESHOLD
)

def main():
    """
    檢查目前 Async AI Scaling 狀態。
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()

        if connection is None:

            print(
                "Database connection failed"
            )

            return

        cursor = connection.cursor()

        print("=" * 60)
        print(
            "AutoSearch V4 - "
            "P2.4 Async AI Scaling Check"
        )
        print("=" * 60)

        # ==========================================
        # Articles
        # ==========================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM articles
            """
        )

        article_count = (
            cursor.fetchone()[0]
        )

        print(
            f"Articles              : "
            f"{article_count}"
        )

        # ==========================================
        # AI Tasks
        # ==========================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM ai_tasks
            """
        )

        task_count = (
            cursor.fetchone()[0]
        )

        print(
            f"AI Tasks              : "
            f"{task_count}"
        )

        # ==========================================
        # WAITING
        # ==========================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM ai_tasks
            WHERE status = 'WAITING'
            """
        )

        waiting_count = (
            cursor.fetchone()[0]
        )

        print(
            f"WAITING AI Tasks      : "
            f"{waiting_count}"
        )

        # ==========================================
        # Threshold
        # ==========================================

        print(
            f"AI Threshold          : "
            f"{AI_THRESHOLD}"
        )

        print()

        if waiting_count >= AI_THRESHOLD:

            print(
                "Async AI Scaling      : "
                "READY / SHOULD TRIGGER"
            )

        else:

            remaining = (
                AI_THRESHOLD
                - waiting_count
            )

            print(
                "Async AI Scaling      : "
                "NOT READY"
            )

            print(
                f"Remaining Tasks       : "
                f"{remaining}"
            )

        # ==========================================
        # Status Distribution
        # ==========================================

        print()
        print("AI Task Status")
        print("-" * 60)

        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS count
            FROM ai_tasks
            GROUP BY status
            ORDER BY status
            """
        )

        rows = cursor.fetchall()

        if not rows:

            print(
                "No AI Tasks"
            )

        else:

            for status, count in rows:

                print(
                    f"{status:<20} : "
                    f"{count}"
                )

        # ==========================================
        # Latest Tasks
        # ==========================================

        print()
        print("Latest AI Tasks")
        print("-" * 60)

        cursor.execute(
            """
            SELECT
                article_id,
                task_type,
                status,
                priority,
                retry_count
            FROM ai_tasks
            ORDER BY article_id DESC
            LIMIT 10
            """
        )

        rows = cursor.fetchall()

        if not rows:

            print(
                "No AI Tasks"
            )

        else:

            for row in rows:

                print(
                    f"article={row[0]}, "
                    f"type={row[1]}, "
                    f"status={row[2]}, "
                    f"priority={row[3]}, "
                    f"retry={row[4]}"
                )

        print("=" * 60)

    except Exception as e:

        print(
            f"ERROR: {e}"
        )

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()


if __name__ == "__main__":

    main()