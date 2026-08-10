"""
check_search_index.py

AutoSearch V4

P2.3 - Search Ranking Enhancement
Step 1 - Search Index 確認

用途：
    檢查 Knowledge Archive、Search Index、
    Knowledge Scores 三者目前的資料狀態與關聯。

實際 V4 Schema：

    articles
        ↓
    knowledge_archive
        ↓
        ├── search_index
        └── knowledge_scores

檢查項目：
    1. 資料表數量
    2. Knowledge Archive → Search Index
    3. Orphan Search Index
    4. Search Index 詳細資料
    5. Knowledge Archive → Knowledge Scores
    6. Orphan Knowledge Scores
    7. Check Summary

注意：
    本程式只讀取資料庫，不修改任何資料。
"""


from database.connection import get_connection


def print_section(title):
    """輸出區塊標題"""

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def check_counts(cursor):
    """
    檢查主要資料表數量
    """

    print_section("1. 資料表數量")

    tables = [
        "articles",
        "knowledge_archive",
        "search_index",
        "knowledge_scores",
    ]

    counts = {}

    for table in tables:

        sql = f"""
            SELECT COUNT(*) AS count
            FROM {table}
        """

        cursor.execute(sql)

        row = cursor.fetchone()

        count = row["count"]

        counts[table] = count

        print(f"{table:<22} : {count}")

    return counts


def check_knowledge_indexes(cursor):
    """
    檢查 Knowledge Archive 是否都有 Search Index
    """

    print_section(
        "2. Knowledge Archive → Search Index"
    )

    sql = """
        SELECT
            ka.id AS knowledge_id,
            ka.article_id,
            a.title,
            si.id AS search_index_id
        FROM knowledge_archive ka

        LEFT JOIN articles a
            ON ka.article_id = a.id

        LEFT JOIN search_index si
            ON ka.id = si.knowledge_id

        ORDER BY ka.id
    """

    cursor.execute(sql)

    rows = cursor.fetchall()

    if not rows:

        print(
            "目前沒有 Knowledge Archive 資料。"
        )

        return

    for row in rows:

        knowledge_id = row["knowledge_id"]
        article_id = row["article_id"]
        title = row["title"]
        search_index_id = row["search_index_id"]

        print()
        print(f"Knowledge ID : {knowledge_id}")
        print(f"Article ID   : {article_id}")
        print(f"Title        : {title}")

        if search_index_id is None:

            print(
                "Search Index : ❌ NOT FOUND"
            )

        else:

            print(
                f"Search Index : ✅ {search_index_id}"
            )


def check_orphan_indexes(cursor):
    """
    檢查是否存在沒有對應 Knowledge Archive 的
    Search Index。
    """

    print_section(
        "3. Orphan Search Index"
    )

    sql = """
        SELECT
            si.id,
            si.knowledge_id
        FROM search_index si

        LEFT JOIN knowledge_archive ka
            ON si.knowledge_id = ka.id

        WHERE ka.id IS NULL

        ORDER BY si.id
    """

    cursor.execute(sql)

    rows = cursor.fetchall()

    if not rows:

        print(
            "✅ 沒有發現 Orphan Search Index"
        )

        return

    print(
        f"⚠️ 發現 {len(rows)} 筆 "
        f"Orphan Search Index"
    )

    for row in rows:

        print(
            f"Search Index ID: {row['id']} "
            f"| knowledge_id: {row['knowledge_id']}"
        )


def check_search_index_details(cursor):
    """
    顯示 Search Index 詳細資料。
    """

    print_section(
        "4. Search Index 詳細資料"
    )

    sql = """
        SELECT
            si.id,
            si.knowledge_id,
            ka.article_id,
            a.title,
            si.search_text,
            si.keywords,
            si.entities,
            si.topic,
            si.embedding_reference,
            si.index_version,
            si.created_time

        FROM search_index si

        INNER JOIN knowledge_archive ka
            ON si.knowledge_id = ka.id

        LEFT JOIN articles a
            ON ka.article_id = a.id

        ORDER BY si.id
    """

    cursor.execute(sql)

    rows = cursor.fetchall()

    if not rows:

        print(
            "⚠️ search_index 目前沒有資料。"
        )

        return

    for row in rows:

        print()
        print("-" * 70)

        print(
            f"Search Index ID     : "
            f"{row['id']}"
        )

        print(
            f"Knowledge ID        : "
            f"{row['knowledge_id']}"
        )

        print(
            f"Article ID          : "
            f"{row['article_id']}"
        )

        print(
            f"Title               : "
            f"{row['title']}"
        )

        print(
            f"search_text         : "
            f"{row['search_text']}"
        )

        print(
            f"keywords            : "
            f"{row['keywords']}"
        )

        print(
            f"entities            : "
            f"{row['entities']}"
        )

        print(
            f"topic               : "
            f"{row['topic']}"
        )

        print(
            f"embedding_reference : "
            f"{row['embedding_reference']}"
        )

        print(
            f"index_version       : "
            f"{row['index_version']}"
        )

        print(
            f"created_time        : "
            f"{row['created_time']}"
        )


def check_knowledge_scores(cursor):
    """
    檢查 Knowledge Archive 是否都有
    Knowledge Score。
    """

    print_section(
        "5. Knowledge Archive → Knowledge Scores"
    )

    sql = """
        SELECT
            ka.id AS knowledge_id,
            ka.article_id,
            a.title,

            ks.id AS score_id,
            ks.importance,
            ks.confidence,
            ks.quality_score,
            ks.freshness_score,
            ks.ranking_score

        FROM knowledge_archive ka

        LEFT JOIN articles a
            ON ka.article_id = a.id

        LEFT JOIN knowledge_scores ks
            ON ka.id = ks.knowledge_id

        ORDER BY ka.id
    """

    cursor.execute(sql)

    rows = cursor.fetchall()

    if not rows:

        print(
            "目前沒有 Knowledge Archive 資料。"
        )

        return

    for row in rows:

        print()
        print("-" * 70)

        print(
            f"Knowledge ID : "
            f"{row['knowledge_id']}"
        )

        print(
            f"Article ID   : "
            f"{row['article_id']}"
        )

        print(
            f"Title        : "
            f"{row['title']}"
        )

        if row["score_id"] is None:

            print(
                "Knowledge Score : ❌ NOT FOUND"
            )

        else:

            print(
                f"Knowledge Score : ✅ "
                f"{row['score_id']}"
            )

            print(
                f"Importance      : "
                f"{row['importance']}"
            )

            print(
                f"Confidence      : "
                f"{row['confidence']}"
            )

            print(
                f"Quality Score   : "
                f"{row['quality_score']}"
            )

            print(
                f"Freshness Score : "
                f"{row['freshness_score']}"
            )

            print(
                f"Ranking Score   : "
                f"{row['ranking_score']}"
            )


def check_orphan_scores(cursor):
    """
    檢查是否存在沒有對應 Knowledge Archive
    的 Knowledge Score。
    """

    print_section(
        "6. Orphan Knowledge Scores"
    )

    sql = """
        SELECT
            ks.id,
            ks.knowledge_id

        FROM knowledge_scores ks

        LEFT JOIN knowledge_archive ka
            ON ks.knowledge_id = ka.id

        WHERE ka.id IS NULL

        ORDER BY ks.id
    """

    cursor.execute(sql)

    rows = cursor.fetchall()

    if not rows:

        print(
            "✅ 沒有發現 Orphan Knowledge Score"
        )

        return

    print(
        f"⚠️ 發現 {len(rows)} 筆 "
        f"Orphan Knowledge Score"
    )

    for row in rows:

        print(
            f"Score ID: {row['id']} "
            f"| knowledge_id: {row['knowledge_id']}"
        )


def print_summary(counts):
    """
    輸出最終檢查摘要。
    """

    print_section(
        "7. Check Summary"
    )

    print(
        f"Articles             : "
        f"{counts['articles']}"
    )

    print(
        f"Knowledge Archive    : "
        f"{counts['knowledge_archive']}"
    )

    print(
        f"Search Index         : "
        f"{counts['search_index']}"
    )

    print(
        f"Knowledge Scores     : "
        f"{counts['knowledge_scores']}"
    )

    print()

    # Knowledge Archive 與 Search Index
    if (
        counts["knowledge_archive"]
        == counts["search_index"]
    ):

        print(
            "✅ Knowledge Archive / "
            "Search Index 數量一致"
        )

    else:

        print(
            "⚠️ Knowledge Archive / "
            "Search Index 數量不一致"
        )

    # Knowledge Archive 與 Scores
    if (
        counts["knowledge_archive"]
        == counts["knowledge_scores"]
    ):

        print(
            "✅ Knowledge Archive / "
            "Knowledge Scores 數量一致"
        )

    else:

        print(
            "⚠️ Knowledge Archive / "
            "Knowledge Scores 數量不一致"
        )


def run_check():
    """
    執行完整 Search Index Check。
    """

    print()
    print("=" * 70)
    print("AutoSearch V4")
    print("P2.3 Search Ranking Enhancement")
    print("Step 1 - Search Index Check")
    print("=" * 70)

    connection = None
    cursor = None

    try:

        connection = get_connection()

        if connection is None:

            print()
            print(
                "❌ Database connection failed."
            )

            return

        cursor = connection.cursor(
            dictionary=True
        )

        # 1
        counts = check_counts(
            cursor
        )

        # 2
        check_knowledge_indexes(
            cursor
        )

        # 3
        check_orphan_indexes(
            cursor
        )

        # 4
        check_search_index_details(
            cursor
        )

        # 5
        check_knowledge_scores(
            cursor
        )

        # 6
        check_orphan_scores(
            cursor
        )

        # 7
        print_summary(
            counts
        )

        print()
        print("=" * 70)
        print(
            "Search Index Check Completed."
        )
        print("=" * 70)

    except Exception as e:

        print()
        print(
            "❌ Search Index Check Failed"
        )

        print(
            f"Error: {e}"
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


if __name__ == "__main__":

    run_check()