"""
utils/check_database_schema.py

AutoSearch V5

Database Schema Inspector

用途:

查看目前 MySQL:

- Tables
- Columns
- Create SQL
- Index / Structure

支援:

V4
    - Articles
    - AI Tasks
    - Knowledge Archive
    - Knowledge Scores
    - Search Index
    - Raw Documents

V5
    - Targets
    - Jobs
"""


from database.connection import get_connection


# ======================================
# Show Tables
# ======================================

def show_tables():

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            "SHOW TABLES"
        )

        tables = cursor.fetchall()

        print(
            "\n========== TABLES ==========\n"
        )

        for table in tables:

            print(
                table[0]
            )

    finally:

        cursor.close()
        conn.close()


# ======================================
# Show Columns
# ======================================

def show_columns(table):

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        print(
            f"\n========== {table} COLUMNS ==========\n"
        )

        cursor.execute(
            f"""
            SHOW COLUMNS FROM `{table}`
            """
        )

        rows = cursor.fetchall()

        for row in rows:

            print(row)

    finally:

        cursor.close()
        conn.close()


# ======================================
# Show Create SQL
# ======================================

def show_create(table):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            f"""
            SHOW CREATE TABLE `{table}`
            """
        )

        result = cursor.fetchone()

        print(
            "\n========== CREATE TABLE ==========\n"
        )

        if result:

            print(
                result[1]
            )

    finally:

        cursor.close()
        conn.close()


# ======================================
# Main
# ======================================

def main():

    print(
        "========== AutoSearch V5 Schema Check =========="
    )

    # ==================================
    # Show All Tables
    # ==================================

    show_tables()

    # ==================================
    # Tables To Inspect
    # ==================================

    check_tables = [

        # ==============================
        # V4
        # ==============================

        "articles",

        "ai_tasks",

        "knowledge_archive",

        "knowledge_scores",

        "search_index",

        "raw_documents",

        # ==============================
        # V5
        # ==============================

        "targets",

        "jobs",

    ]

    # ==================================
    # Inspect Tables
    # ==================================

    for table in check_tables:

        try:

            show_columns(
                table
            )

            show_create(
                table
            )

        except Exception as e:

            print(
                f"\nSkip {table}: {e}"
            )

    # ==================================
    # Finished
    # ==================================

    print(
        "\n========== Check Finished =========="
    )


# ======================================
# Entry Point
# ======================================

if __name__ == "__main__":

    main()