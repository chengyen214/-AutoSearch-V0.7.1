"""
tests/check_archive_database.py

AutoSearch V4

Database Diagnostic Tool

用途：
    直接檢查目前資料庫中的：

    1. Articles
    2. Archive Versions
    3. TSMC 搜尋結果
    4. AI 欄位
    5. Archive 數量
    6. Article / Archive 關聯

注意：
    本程式只讀取資料庫。
    不會新增、修改或刪除任何資料。
"""

from database.connection import get_connection


# ============================================================
# Helpers
# ============================================================

def print_section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_rows(rows):
    if not rows:
        print("No data.")
        return

    for index, row in enumerate(rows, start=1):

        print()
        print(f"[{index}]")

        for key, value in row.items():
            print(f"  {key}: {value}")


# ============================================================
# Database Check
# ============================================================

def check_database():

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        # ====================================================
        # 1. Articles Count
        # ====================================================

        print_section(
            "1. ARTICLES COUNT"
        )

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM articles
            """
        )

        result = cursor.fetchone()

        print(
            "Total articles:",
            result["total"]
        )

        # ====================================================
        # 2. Archive Versions Count
        # ====================================================

        print_section(
            "2. ARCHIVE VERSIONS COUNT"
        )

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM archive_versions
            """
        )

        result = cursor.fetchone()

        print(
            "Total archive versions:",
            result["total"]
        )

        # ====================================================
        # 3. Archived Article Count
        # ====================================================

        print_section(
            "3. ARCHIVED ARTICLE COUNT"
        )

        cursor.execute(
            """
            SELECT COUNT(
                DISTINCT article_id
            ) AS total

            FROM archive_versions
            """
        )

        result = cursor.fetchone()

        print(
            "Archived articles:",
            result["total"]
        )

        # ====================================================
        # 4. Latest Articles
        # ====================================================

        print_section(
            "4. LATEST ARTICLES"
        )

        cursor.execute(
            """
            SELECT
                id,
                document_id,
                keyword,
                title,
                source,
                published,
                crawl_time,
                ai_category,
                ai_importance,
                ai_confidence,
                ai_status

            FROM articles

            ORDER BY id DESC

            LIMIT 20
            """
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 5. Search TSMC in Articles
        # ====================================================

        print_section(
            "5. ARTICLES MATCHING TSMC"
        )

        keyword = "%TSMC%"

        cursor.execute(
            """
            SELECT
                id,
                document_id,
                keyword,
                title,
                url,
                source,
                published,
                crawl_time,

                ai_summary,
                ai_category,
                ai_keywords,
                ai_importance,
                ai_model,
                ai_version,
                ai_analyze_time,
                ai_confidence,
                ai_status

            FROM articles

            WHERE
                keyword LIKE %s
                OR title LIKE %s
                OR source LIKE %s
                OR url LIKE %s
                OR ai_summary LIKE %s
                OR ai_keywords LIKE %s

            ORDER BY id DESC
            """,
            (
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword
            )
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 6. TSMC Articles + Archive Versions
        # ====================================================

        print_section(
            "6. TSMC ARTICLES + ARCHIVE VERSIONS"
        )

        cursor.execute(
            """
            SELECT

                a.id AS article_id,
                a.document_id,
                a.keyword,
                a.title,
                a.source,

                av.id AS archive_version_id,
                av.raw_document_id,
                av.version_number,
                av.file_hash,
                av.storage_path,
                av.file_size,
                av.mime_type,
                av.created_time

            FROM articles a

            LEFT JOIN archive_versions av
                ON a.id = av.article_id

            WHERE
                a.keyword LIKE %s
                OR a.title LIKE %s
                OR a.source LIKE %s
                OR a.url LIKE %s

            ORDER BY
                av.created_time DESC
            """,
            (
                keyword,
                keyword,
                keyword,
                keyword
            )
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 7. Direct Archive Search
        # ====================================================

        print_section(
            "7. DIRECT ARCHIVE SEARCH: TSMC"
        )

        cursor.execute(
            """
            SELECT

                av.id,
                av.article_id,
                av.raw_document_id,
                av.version_number,
                av.file_hash,
                av.storage_path,
                av.file_size,
                av.mime_type,
                av.created_time,

                a.document_id,
                a.keyword,
                a.title,
                a.url,
                a.source,

                a.ai_category,
                a.ai_importance,
                a.ai_confidence,
                a.ai_status

            FROM archive_versions av

            INNER JOIN articles a
                ON a.id = av.article_id

            WHERE

                a.title LIKE %s
                OR a.keyword LIKE %s
                OR a.source LIKE %s
                OR a.url LIKE %s
                OR a.ai_summary LIKE %s
                OR a.ai_keywords LIKE %s

            ORDER BY
                av.created_time DESC
            """,
            (
                keyword,
                keyword,
                keyword,
                keyword,
                keyword,
                keyword
            )
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 8. AI Analysis Status
        # ====================================================

        print_section(
            "8. AI ANALYSIS STATUS"
        )

        cursor.execute(
            """
            SELECT
                ai_status,
                COUNT(*) AS total

            FROM articles

            GROUP BY
                ai_status

            ORDER BY
                total DESC
            """
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 9. AI Categories
        # ====================================================

        print_section(
            "9. AI CATEGORIES"
        )

        cursor.execute(
            """
            SELECT
                ai_category,
                COUNT(*) AS total

            FROM articles

            GROUP BY
                ai_category

            ORDER BY
                total DESC
            """
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 10. AI Importance
        # ====================================================

        print_section(
            "10. AI IMPORTANCE"
        )

        cursor.execute(
            """
            SELECT
                ai_importance,
                COUNT(*) AS total

            FROM articles

            GROUP BY
                ai_importance

            ORDER BY
                ai_importance DESC
            """
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 11. Archive Statistics
        # ====================================================

        print_section(
            "11. ARCHIVE STATISTICS"
        )

        cursor.execute(
            """
            SELECT

                COUNT(
                    DISTINCT av.article_id
                ) AS article_count,

                COUNT(*) AS version_count,

                COUNT(
                    DISTINCT a.source
                ) AS source_count,

                COALESCE(
                    SUM(av.file_size),
                    0
                ) AS total_size

            FROM archive_versions av

            INNER JOIN articles a
                ON a.id = av.article_id
            """
        )

        result = cursor.fetchone()

        print_rows([result])

        # ====================================================
        # 12. Archive Latest 20
        # ====================================================

        print_section(
            "12. LATEST ARCHIVE VERSIONS"
        )

        cursor.execute(
            """
            SELECT

                av.id,
                av.article_id,
                av.version_number,
                av.created_time,

                a.keyword,
                a.title,
                a.source

            FROM archive_versions av

            INNER JOIN articles a
                ON a.id = av.article_id

            ORDER BY
                av.created_time DESC

            LIMIT 20
            """
        )

        rows = cursor.fetchall()

        print_rows(rows)

        # ====================================================
        # 13. Knowledge Archive
        # ====================================================

        print_section(
            "13. KNOWLEDGE ARCHIVE COUNT"
        )

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM knowledge_archive
            """
        )

        result = cursor.fetchone()

        print(
            "Knowledge archive:",
            result["total"]
        )

        # ====================================================
        # 14. Knowledge Scores
        # ====================================================

        print_section(
            "14. KNOWLEDGE SCORES COUNT"
        )

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM knowledge_scores
            """
        )

        result = cursor.fetchone()

        print(
            "Knowledge scores:",
            result["total"]
        )

        # ====================================================
        # 15. Search Index
        # ====================================================

        print_section(
            "15. SEARCH INDEX COUNT"
        )

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM search_index
            """
        )

        result = cursor.fetchone()

        print(
            "Search index:",
            result["total"]
        )

        # ====================================================
        # 16. Final Diagnosis
        # ====================================================

        print_section(
            "16. DIAGNOSIS"
        )

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM articles
            WHERE
                keyword LIKE %s
                OR title LIKE %s
                OR source LIKE %s
                OR url LIKE %s
            """,
            (
                keyword,
                keyword,
                keyword,
                keyword
            )
        )

        article_count = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total

            FROM archive_versions av

            INNER JOIN articles a
                ON a.id = av.article_id

            WHERE
                a.keyword LIKE %s
                OR a.title LIKE %s
                OR a.source LIKE %s
                OR a.url LIKE %s
            """,
            (
                keyword,
                keyword,
                keyword,
                keyword
            )
        )

        archive_count = cursor.fetchone()["total"]

        print()
        print("TSMC Articles :", article_count)
        print("TSMC Archives :", archive_count)

        if article_count == 0:

            print()
            print(
                "RESULT:"
            )
            print(
                "Database contains no Article matching TSMC."
            )

        elif archive_count == 0:

            print()
            print(
                "RESULT:"
            )
            print(
                "TSMC Article exists, "
                "but no archive_versions record is linked."
            )

        else:

            print()
            print(
                "RESULT:"
            )
            print(
                "TSMC Archive data exists."
            )

    finally:

        cursor.close()
        conn.close()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AutoSearch V4 Database Diagnostic")
    print("=" * 70)

    check_database()

    print()
    print("=" * 70)
    print("Check Finished")
    print("=" * 70)