"""
utils/reset_test.py

AutoSearch V4

Test Environment Reset Tool

功能:

1. 清除 Duplicate Cache
2. 清除 History
3. 清除 Excel Output
4. 清除 Raw HTML Archive
5. 清除 Database Test Data
6. Reset Auto Increment ID

Database Flow:

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

注意:

不刪除 Database Schema
不刪除 migration_history
"""

import os
import json
import shutil

from database.connection import get_connection


# ======================================
# Path
# ======================================

DOCUMENT_FILE = (
    "storage/documents.json"
)

HISTORY_FILE = (
    "storage/history.json"
)

EXCEL_FILE = (
    "output/result.xlsx"
)

# ======================================
# P2.2.2 Archive
#
# ArchiveService 實際使用:
# archive/html
# ======================================

ARCHIVE_DIR = (
    "archive/html"
)

LOG_DIR = (
    "logs"
)


# ======================================
# Reset JSON
# ======================================

def reset_json(path):

    if os.path.exists(path):

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


# ======================================
# Remove File
# ======================================

def remove_file(path):

    if os.path.exists(path):

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


# ======================================
# Clear Directory
# ======================================

def clear_directory(path):

    if not os.path.exists(path):

        print(
            f"[SKIP] {path}"
        )

        return

    for item in os.listdir(path):

        item_path = os.path.join(
            path,
            item
        )

        if os.path.isfile(item_path):

            os.remove(
                item_path
            )

        elif os.path.isdir(item_path):

            shutil.rmtree(
                item_path
            )

    print(
        f"[CLEAR DIR] {path}"
    )


# ======================================
# Clear Logs
# ======================================

def clear_logs(path):

    if not os.path.exists(path):

        print(
            f"[SKIP] {path}"
        )

        return

    for filename in os.listdir(path):

        file_path = os.path.join(
            path,
            filename
        )

        if os.path.isfile(file_path):

            os.remove(
                file_path
            )

        elif os.path.isdir(file_path):

            shutil.rmtree(
                file_path
            )

    print(
        f"[CLEAR LOG] {path}"
    )


# ======================================
# Reset Database
# ======================================

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
            "========== DATABASE RESET =========="
        )

        # ==================================
        # FK Child -> Parent
        # ==================================
        #
        # search_index
        # knowledge_scores
        # archive_versions
        # knowledge_archive
        # ai_tasks
        # raw_documents
        # articles
        #
        # ==================================

        tables = [

            "search_index",

            "knowledge_scores",

            "archive_versions",

            "knowledge_archive",

            "ai_tasks",

            "raw_documents",

            "articles"

        ]

        # ==================================
        # Clear Tables
        # ==================================

        for table in tables:

            try:

                cursor.execute(
                    f"""
                    DELETE FROM {table}
                    """
                )

                print(
                    f"[CLEAR TABLE] {table}"
                )

            except Exception as e:

                print(
                    f"[SKIP TABLE] {table}: {e}"
                )

        # ==================================
        # Reset Auto Increment
        # ==================================

        for table in tables:

            try:

                cursor.execute(
                    f"""
                    ALTER TABLE {table}
                    AUTO_INCREMENT = 1
                    """
                )

                print(
                    f"[RESET ID] {table}"
                )

            except Exception as e:

                print(
                    f"[SKIP ID] {table}: {e}"
                )

        # ==================================
        # Commit
        # ==================================

        conn.commit()

    except Exception:

        conn.rollback()

        raise

    finally:

        cursor.close()

        conn.close()


# ======================================
# Main
# ======================================

def main():

    print()

    print(
        "================================="
    )

    print(
        " AutoSearch V4 Test Reset"
    )

    print(
        "================================="
    )

    print()

    # --------------------------
    # Local Storage
    # --------------------------

    reset_json(
        DOCUMENT_FILE
    )

    reset_json(
        HISTORY_FILE
    )

    remove_file(
        EXCEL_FILE
    )

    clear_logs(
        LOG_DIR
    )

    # --------------------------
    # P2.2.2 Archive
    # --------------------------

    clear_directory(
        ARCHIVE_DIR
    )

    # --------------------------
    # Database
    # --------------------------

    reset_database()

    print()

    print(
        "================================="
    )

    print(
        " Reset Complete"
    )

    print(
        "================================="
    )


# ======================================
# Entry Point
# ======================================

if __name__ == "__main__":

    main()