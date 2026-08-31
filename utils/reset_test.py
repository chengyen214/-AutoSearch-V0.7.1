"""
utils/reset_test.py

AutoSearch V5

Test Environment Reset Tool

功能：

1. 清除 Duplicate Cache
2. 清除 History
3. 清除 Excel Output
4. 清除 Legacy Local HTML Archive
5. 清除 MongoDB Raw HTML Archive
6. 清除 MySQL Test Data

Database Flow：

search_index
|
knowledge_scores
|
archive_versions
|
knowledge_archive
|
+-------------+
|             |
v             v
ai_tasks   raw_documents
|             |
+------articles


MySQL：

保留：

    jobs
    targets

以及：

    jobs 內所有資料
    targets 內所有資料


其他 MySQL Table：

    只刪除資料

    不：

        DROP TABLE
        TRUNCATE TABLE
        ALTER TABLE
        修改 Schema
        修改 Index
        修改 Foreign Key


migration_history：

    完全不動


MongoDB：

autosearch
    |
    +── raw_html


IMPORTANT：

本工具：

    不刪除 Database Schema
    不刪除 migration_history
    不刪除 MongoDB collection
    不刪除 MongoDB indexes

MySQL：

    jobs
        ↓
    保留 Table + Data

    targets
        ↓
    保留 Table + Data

其他資料表：

    只 DELETE Data


AutoSearch V5 Raw HTML Archive
正式使用 MongoDB。

因此：

    archive/html
        ↓
    Legacy Local Storage

不再是主要 Raw HTML Storage。

真正的 Raw HTML：

    MongoDB
        ↓
    autosearch.raw_html
"""


# ==================================================
#
# Standard Library
#
# ==================================================

import os
import json
import shutil


# ==================================================
#
# MySQL
#
# ==================================================

from database.connection import (
    get_connection
)


# ==================================================
#
# MongoDB
#
# ==================================================

from database.raw_html_repository import (
    RawHTMLRepository
)


# ==================================================
#
# Local Paths
#
# ==================================================

DOCUMENT_FILE = (
    "storage/documents.json"
)


HISTORY_FILE = (
    "storage/history.json"
)


EXCEL_FILE = (
    "output/result.xlsx"
)


# ==================================================
#
# Legacy Local Archive
#
# ==================================================
#
# AutoSearch V5 目前正式 Raw HTML
# 已改存 MongoDB。
#
# 這個目錄只保留作為：
#
# Legacy / Migration / 舊測試資料
#
# ==================================================

ARCHIVE_DIR = (
    "archive/html"
)


LOG_DIR = (
    "logs"
)


# ==================================================
#
# MySQL Tables
#
# ==================================================
#
# IMPORTANT：
#
# 以下 Table 只清除資料。
#
# 不 DROP
# 不 TRUNCATE
# 不 ALTER TABLE
# 不修改 Schema
# 不修改 Index
# 不修改 FK
#
# jobs / targets 不在這裡。
#
# 因為：
#
# jobs
# targets
#
# 必須保留 Table + Data。
#
# ==================================================

MYSQL_DATA_RESET_TABLES = [

    # ----------------------------------------------
    # Child Tables
    # ----------------------------------------------

    "search_index",

    "knowledge_scores",

    "archive_versions",

    "knowledge_archive",

    "ai_tasks",

    "raw_documents",

    "article_metadata",

    # ----------------------------------------------
    # Parent Table
    # ----------------------------------------------

    "articles",

]


# ==================================================
#
# Reset JSON
#
# ==================================================

def reset_json(
    path
):

    if os.path.exists(
        path
    ):

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                [],
                f,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"[RESET JSON] {path}"
        )

    else:

        print(
            f"[SKIP] {path}"
        )


# ==================================================
#
# Remove File
#
# ==================================================

def remove_file(
    path
):

    if os.path.exists(
        path
    ):

        os.remove(
            path
        )

        print(
            f"[REMOVE] {path}"
        )

    else:

        print(
            f"[SKIP] {path}"
        )


# ==================================================
#
# Clear Directory
#
# ==================================================

def clear_directory(
    path
):

    if not os.path.exists(
        path
    ):

        print(
            f"[SKIP] {path}"
        )

        return

    for item in os.listdir(
        path
    ):

        item_path = os.path.join(
            path,
            item
        )

        if os.path.isfile(
            item_path
        ):

            os.remove(
                item_path
            )

        elif os.path.isdir(
            item_path
        ):

            shutil.rmtree(
                item_path
            )

    print(
        f"[CLEAR DIR] {path}"
    )


# ==================================================
#
# Clear Logs
#
# ==================================================

def clear_logs(
    path
):
    """
    清除 Logs。

    Windows 注意：

        如果 log 檔目前正被 Python logging
        或其他程序使用，os.remove()
        會產生 WinError 32。

    因此：

        無法刪除的檔案
            ↓
        顯示 [SKIP]
            ↓
        不阻止整個 Reset 流程

    這樣 MongoDB / MySQL reset
    仍然可以繼續執行。
    """

    if not os.path.exists(
        path
    ):

        print(
            f"[SKIP] {path}"
        )

        return

    for filename in os.listdir(
        path
    ):

        file_path = os.path.join(
            path,
            filename
        )

        # ----------------------------------
        # File
        # ----------------------------------

        if os.path.isfile(
            file_path
        ):

            try:

                os.remove(
                    file_path
                )

                print(
                    f"[REMOVE LOG] {file_path}"
                )

            except PermissionError:

                print(
                    f"[SKIP LOG - IN USE] "
                    f"{file_path}"
                )

            except OSError as e:

                print(
                    f"[SKIP LOG] "
                    f"{file_path}: {e}"
                )

        # ----------------------------------
        # Directory
        # ----------------------------------

        elif os.path.isdir(
            file_path
        ):

            try:

                shutil.rmtree(
                    file_path
                )

                print(
                    f"[REMOVE LOG DIR] "
                    f"{file_path}"
                )

            except PermissionError:

                print(
                    f"[SKIP LOG DIR - IN USE] "
                    f"{file_path}"
                )

            except OSError as e:

                print(
                    f"[SKIP LOG DIR] "
                    f"{file_path}: {e}"
                )

    print(
        f"[CLEAR LOG] {path}"
    )


# ==================================================
#
# Reset MongoDB Raw HTML
#
# ==================================================

def reset_mongodb_raw_html():

    print()

    print(
        "========== MONGODB RAW HTML RESET =========="
    )

    repository = RawHTMLRepository()

    collection = repository.collection

    # ----------------------------------
    # Count Before
    # ----------------------------------

    count_before = (
        collection.count_documents({})
    )

    print(
        f"[MONGODB] raw_html before : "
        f"{count_before}"
    )

    # ----------------------------------
    # Nothing to delete
    # ----------------------------------

    if count_before == 0:

        print(
            "[MONGODB] No raw_html documents found."
        )

        return

    # ----------------------------------
    # Delete Documents Only
    #
    # IMPORTANT：
    #
    # delete_many({})
    #
    # 只刪除 documents。
    #
    # 不會：
    #
    # drop collection
    # drop database
    # drop indexes
    #
    # ----------------------------------

    result = collection.delete_many(
        {}
    )

    print(
        f"[CLEAR MONGODB] "
        f"raw_html deleted : "
        f"{result.deleted_count}"
    )

    # ----------------------------------
    # Verify
    # ----------------------------------

    count_after = (
        collection.count_documents({})
    )

    print(
        f"[MONGODB] raw_html after  : "
        f"{count_after}"
    )

    if count_after != 0:

        raise RuntimeError(
            "MongoDB raw_html reset failed."
        )

    print(
        "[OK] MongoDB raw_html cleared."
    )


# ==================================================
#
# Reset MySQL Database Data
#
# ==================================================

def reset_database():

    conn = get_connection()

    if conn is None:

        raise Exception(
            "Database connection failed"
        )

    cursor = conn.cursor()

    try:

        print()

        print(
            "========== MYSQL DATA RESET =========="
        )

        print(
            "IMPORTANT:"
        )

        print(
            "  jobs    : KEEP TABLE + DATA"
        )

        print(
            "  targets : KEEP TABLE + DATA"
        )

        print(
            "  migration_history : KEEP TABLE + DATA"
        )

        print(
            "  other tables      : DELETE DATA ONLY"
        )

        print(
            "======================================"
        )

        # ==================================
        # Count jobs / targets Before
        #
        # 只讀取。
        #
        # 不修改。
        # ==================================

        for table in (
            "jobs",
            "targets",
        ):

            try:

                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {table}
                    """
                )

                count = cursor.fetchone()[0]

                print(
                    f"[KEEP DATA] "
                    f"{table}: {count} rows"
                )

            except Exception as e:

                print(
                    f"[VERIFY FAILED] "
                    f"{table}: {e}"
                )

        # ==================================
        # Clear Data Only
        #
        # IMPORTANT：
        #
        # 只使用 DELETE。
        #
        # 不：
        #
        # TRUNCATE
        # DROP
        # ALTER
        #
        # ==================================

        for table in MYSQL_DATA_RESET_TABLES:

            try:

                cursor.execute(
                    f"""
                    DELETE FROM {table}
                    """
                )

                print(
                    f"[CLEAR DATA] {table}: "
                    f"{cursor.rowcount} rows"
                )

            except Exception as e:

                print(
                    f"[SKIP TABLE] "
                    f"{table}: {e}"
                )

                raise

        # ==================================
        # Verify Cleared Tables
        #
        # ==================================

        for table in MYSQL_DATA_RESET_TABLES:

            try:

                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {table}
                    """
                )

                count = cursor.fetchone()[0]

                if count != 0:

                    raise RuntimeError(
                        f"MySQL table reset failed: "
                        f"{table} still has "
                        f"{count} rows."
                    )

                print(
                    f"[VERIFY CLEAR] "
                    f"{table}: 0 rows"
                )

            except Exception:

                raise

        # ==================================
        # Verify jobs / targets Still Exist
        #
        # 只確認資料數量。
        #
        # 不修改。
        # ==================================

        for table in (
            "jobs",
            "targets",
        ):

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM {table}
                """
            )

            count_after = (
                cursor.fetchone()[0]
            )

            print(
                f"[VERIFY KEEP] "
                f"{table}: "
                f"{count_after} rows"
            )

        # ==================================
        # Commit
        # ==================================

        conn.commit()

        print()

        print(
            "[OK] MySQL data reset committed."
        )

        print(
            "[KEEP] jobs table + data"
        )

        print(
            "[KEEP] targets table + data"
        )

        print(
            "[KEEP] migration_history table + data"
        )

        print(
            "[CLEAR] Other MySQL test data only"
        )

        print(
            "[KEEP] MySQL Schema"
        )

        print(
            "[KEEP] MySQL Indexes"
        )

        print(
            "[KEEP] MySQL Foreign Keys"
        )

    except Exception:

        conn.rollback()

        print(
            "[ROLLBACK] MySQL data reset rolled back."
        )

        raise

    finally:

        cursor.close()

        conn.close()


# ==================================================
#
# Main
#
# ==================================================

def main():

    print()

    print(
        "============================================================"
    )

    print(
        "AutoSearch V5"
    )

    print(
        "Test Environment Reset"
    )

    print(
        "============================================================"
    )

    # ==================================
    # 1. Local JSON
    # ==================================

    print()
    print(
        "Resetting Local Storage"
    )
    print(
        "-" * 60
    )

    reset_json(
        DOCUMENT_FILE
    )

    reset_json(
        HISTORY_FILE
    )

    remove_file(
        EXCEL_FILE
    )

    # ==================================
    # 2. Logs
    # ==================================

    print()
    print(
        "Resetting Logs"
    )
    print(
        "-" * 60
    )

    clear_logs(
        LOG_DIR
    )

    # ==================================
    # 3. Legacy Local Archive
    # ==================================

    print()
    print(
        "Resetting Legacy Local Archive"
    )
    print(
        "-" * 60
    )

    clear_directory(
        ARCHIVE_DIR
    )

    # ==================================
    # 4. MongoDB Raw HTML
    # ==================================

    print()
    print(
        "Resetting MongoDB Raw HTML"
    )
    print(
        "-" * 60
    )

    reset_mongodb_raw_html()

    # ==================================
    # 5. MySQL
    # ==================================

    print()
    print(
        "Resetting MySQL Test Data"
    )
    print(
        "-" * 60
    )

    reset_database()

    # ==================================
    # Final
    # ==================================

    print()

    print(
        "============================================================"
    )

    print(
        "[PASS] AutoSearch V5 Test Environment Reset Complete."
    )

    print(
        "============================================================"
    )


# ==================================================
#
# Entry Point
#
# ==================================================

if __name__ == "__main__":

    main()
