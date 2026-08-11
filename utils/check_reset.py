"""
utils/check_reset.py

AutoSearch V4

Database Reset Verification

用途：

    驗證 utils.reset_test.py 執行後，
    AutoSearch V4 核心資料表是否全部清空。

檢查：

    1. articles
    2. ai_tasks
    3. raw_documents
    4. archive_versions
    5. article_metadata
    6. knowledge_archive
    7. knowledge_scores
    8. search_index

注意：

    本工具只負責「檢查」。

    不會：

        DELETE
        TRUNCATE
        UPDATE
        INSERT

執行：

    python -m utils.check_reset

成功：

    DATABASE RESET : PASS

失敗：

    DATABASE RESET : FAILED
"""


from database.connection import (
    get_connection
)


# ==================================================
# Tables
# ==================================================

RESET_TABLES = [

    "articles",

    "ai_tasks",

    "raw_documents",

    "archive_versions",

    "article_metadata",

    "knowledge_archive",

    "knowledge_scores",

    "search_index"

]


# ==================================================
# Main
# ==================================================

def main():
    """
    檢查 Database Reset 狀態。
    """

    connection = None
    cursor = None

    try:

        # ==========================================
        # Database Connection
        # ==========================================

        connection = get_connection()

        if connection is None:

            print(
                "DATABASE RESET : FAILED"
            )

            print(
                "Reason: Database connection failed"
            )

            return False


        cursor = connection.cursor()


        # ==========================================
        # Header
        # ==========================================

        print("=" * 60)

        print(
            "AutoSearch V4 - "
            "Database Reset Check"
        )

        print("=" * 60)

        print()


        # ==========================================
        # Check Tables
        # ==========================================

        results = []

        has_data = False

        missing_tables = []


        for table in RESET_TABLES:

            try:

                sql = f"""
                SELECT COUNT(*)
                FROM `{table}`
                """

                cursor.execute(
                    sql
                )

                row = cursor.fetchone()

                count = int(
                    row[0]
                )


                results.append(
                    (
                        table,
                        count
                    )
                )


                if count > 0:

                    has_data = True


            except Exception as e:

                missing_tables.append(
                    (
                        table,
                        str(e)
                    )
                )


        # ==========================================
        # Result
        # ==========================================

        print(
            "Database Table Status"
        )

        print("-" * 60)


        for table, count in results:

            if count == 0:

                status = "EMPTY"

            else:

                status = "NOT EMPTY"


            print(
                f"{table:<25} : "
                f"{count:<8} "
                f"{status}"
            )


        # ==========================================
        # Missing / Error Tables
        # ==========================================

        if missing_tables:

            print()

            print(
                "Table Check Errors"
            )

            print("-" * 60)


            for table, error in missing_tables:

                print(
                    f"{table:<25} : "
                    f"{error}"
                )


        # ==========================================
        # Final Status
        # ==========================================

        print()

        print("=" * 60)


        if (
            not has_data
            and not missing_tables
        ):

            print(
                "DATABASE RESET : PASS"
            )

            print(
                "All checked tables are empty."
            )

            print("=" * 60)

            return True


        print(
            "DATABASE RESET : FAILED"
        )


        if has_data:

            print(
                "Some tables still contain data."
            )


        if missing_tables:

            print(
                "Some tables could not be checked."
            )


        print("=" * 60)

        return False


    except Exception as e:

        print(
            "DATABASE RESET : FAILED"
        )

        print(
            f"ERROR: {e}"
        )

        return False


    finally:

        # ==========================================
        # Close Cursor
        # ==========================================

        if cursor is not None:

            try:

                cursor.close()

            except Exception:

                pass


        # ==========================================
        # Close Connection
        # ==========================================

        if connection is not None:

            try:

                connection.close()

            except Exception:

                pass


# ==================================================
# Entry Point
# ==================================================

if __name__ == "__main__":

    success = main()

    if not success:

        raise SystemExit(1)
