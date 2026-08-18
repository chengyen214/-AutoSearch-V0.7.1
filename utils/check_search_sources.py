"""
utils/check_search_sources.py

AutoSearch V4

用途：
    確認 Multi-Source Search 是否正常整合。

檢查：
    1. articles 總數
    2. Google News 文章
    3. TSMC 文章
    4. keyword
    5. source
    6. URL
    7. TSMC Press Center URL
    8. 最近一次搜尋結果

執行：

    python -m utils.check_search_sources
"""

from database.database import get_connection


# ==================================================
# Print Section
# ==================================================

def print_section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ==================================================
# Main
# ==================================================

def main():

    print("=" * 70)
    print("AutoSearch V4 Search Source Check")
    print("=" * 70)

    connection = None
    cursor = None

    try:

        connection = get_connection()

        cursor = connection.cursor(dictionary=True)

        # ==================================================
        # 1. Article Total
        # ==================================================

        print_section("1. ARTICLES TOTAL")

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM articles
            """
        )

        row = cursor.fetchone()

        print(
            f"Total Articles: {row['total']}"
        )

        # ==================================================
        # 2. Keyword Summary
        # ==================================================

        print_section("2. KEYWORD SUMMARY")

        cursor.execute(
            """
            SELECT
                keyword,
                COUNT(*) AS total
            FROM articles
            GROUP BY keyword
            ORDER BY total DESC
            """
        )

        rows = cursor.fetchall()

        for row in rows:

            print(
                f"keyword={row['keyword']} "
                f"| articles={row['total']}"
            )

        # ==================================================
        # 3. Source Summary
        # ==================================================

        print_section("3. SOURCE SUMMARY")

        cursor.execute(
            """
            SELECT
                source,
                COUNT(*) AS total
            FROM articles
            GROUP BY source
            ORDER BY total DESC
            """
        )

        rows = cursor.fetchall()

        for row in rows:

            print(
                f"source={row['source']} "
                f"| articles={row['total']}"
            )

        # ==================================================
        # 4. Google News Articles
        # ==================================================

        print_section("4. GOOGLE NEWS ARTICLES")

        cursor.execute(
            """
            SELECT
                id,
                keyword,
                title,
                source,
                url,
                published,
                crawl_time
            FROM articles
            WHERE
                url NOT LIKE '%pr.tsmc.com%'
                AND source NOT LIKE '%TSMC%'
            ORDER BY id DESC
            LIMIT 20
            """
        )

        rows = cursor.fetchall()

        print(
            f"Google/General Articles Found: {len(rows)}"
        )

        for row in rows:

            print(
                f"[{row['id']}] "
                f"keyword={row['keyword']} "
                f"| source={row['source']}"
            )

            print(
                f"    title={row['title']}"
            )

            print(
                f"    url={row['url']}"
            )

        # ==================================================
        # 5. TSMC Articles
        # ==================================================

        print_section("5. TSMC ARTICLES")

        cursor.execute(
            """
            SELECT
                id,
                keyword,
                title,
                source,
                url,
                published,
                crawl_time
            FROM articles
            WHERE
                url LIKE '%pr.tsmc.com%'
                OR source LIKE '%TSMC%'
            ORDER BY id DESC
            LIMIT 20
            """
        )

        rows = cursor.fetchall()

        print(
            f"TSMC Articles Found: {len(rows)}"
        )

        for row in rows:

            print(
                f"[{row['id']}] "
                f"keyword={row['keyword']} "
                f"| source={row['source']}"
            )

            print(
                f"    title={row['title']}"
            )

            print(
                f"    url={row['url']}"
            )

        # ==================================================
        # 6. TSMC Latest News URL Check
        # ==================================================

        print_section("6. TSMC PRESS CENTER CHECK")

        cursor.execute(
            """
            SELECT
                id,
                keyword,
                title,
                url,
                source
            FROM articles
            WHERE url LIKE '%pr.tsmc.com%'
            ORDER BY id DESC
            LIMIT 20
            """
        )

        rows = cursor.fetchall()

        if not rows:

            print(
                "No TSMC Press Center articles found."
            )

        else:

            for row in rows:

                print(
                    f"[{row['id']}] "
                    f"keyword={row['keyword']} "
                    f"| source={row['source']}"
                )

                print(
                    f"    title={row['title']}"
                )

                print(
                    f"    url={row['url']}"
                )

        # ==================================================
        # 7. Latest Articles
        # ==================================================

        print_section("7. LATEST ARTICLES")

        cursor.execute(
            """
            SELECT
                id,
                keyword,
                title,
                source,
                url,
                crawl_time
            FROM articles
            ORDER BY id DESC
            LIMIT 30
            """
        )

        rows = cursor.fetchall()

        for row in rows:

            print(
                f"[{row['id']}] "
                f"{row['keyword']} "
                f"| {row['source']}"
            )

            print(
                f"    {row['title']}"
            )

            print(
                f"    {row['url']}"
            )

        # ==================================================
        # 8. Final Summary
        # ==================================================

        print_section("8. FINAL CHECK")

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM articles
            WHERE url LIKE '%pr.tsmc.com%'
            """
        )

        tsmc_count = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM articles
            WHERE url NOT LIKE '%pr.tsmc.com%'
            """
        )

        other_count = cursor.fetchone()["total"]

        print(
            f"TSMC Press Center Articles : {tsmc_count}"
        )

        print(
            f"Other Articles             : {other_count}"
        )

        print()

        if tsmc_count > 0:

            print(
                "RESULT: TSMC source data exists."
            )

        else:

            print(
                "RESULT: TSMC source data NOT found."
            )

    except Exception as e:

        print()
        print(
            "ERROR:",
            e
        )

    finally:

        if cursor is not None:

            cursor.close()

        if connection is not None:

            connection.close()

    print()
    print("=" * 70)
    print("Check Finished")
    print("=" * 70)


if __name__ == "__main__":

    main()