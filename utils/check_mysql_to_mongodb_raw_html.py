"""
utils/check_mysql_to_mongodb_raw_html.py

AutoSearch V4

MySQL RawDocument -> MongoDB Raw HTML Check

目的：

    從 MySQL raw_documents 取得一筆實際資料，
    再透過 storage_path 找到 MongoDB raw_html，
    驗證 MySQL 與 MongoDB 的資料是否一致。

Flow:

    MySQL
        raw_documents
            |
            | storage_path
            v
    MongoDB
        raw_html

驗證：

    1. MySQL RawDocument 存在
    2. article_id 存在
    3. original_url 存在
    4. storage_path 存在
    5. storage_path 指向 MongoDB
    6. MongoDB document 存在
    7. article_id 一致
    8. URL 一致
    9. file_hash == content_hash
    10. MongoDB HTML 存在
    11. MongoDB HTML 不為空
    12. file_size 一致

IMPORTANT:

    不依賴 RawDocumentRepository 未確認存在的 API。

    MySQL 查詢直接使用：

        database.connection.get_connection()

    MongoDB 查詢使用目前確定存在的：

        RawHTMLRepository.find_by_id()
"""


from database.connection import (
    get_connection
)

from database.raw_html_repository import (
    RawHTMLRepository
)


# ============================================================
# Configuration
# ============================================================

TEST_ARTICLE_ID = 1


# ============================================================
# Utility
# ============================================================

def extract_mongo_id(
    storage_path
):
    """
    從：

        mongodb://raw_html/<mongo_id>

    取得 MongoDB Document ID。
    """

    prefix = "mongodb://raw_html/"

    if not storage_path:
        return None

    if not isinstance(
        storage_path,
        str
    ):
        return None

    if not storage_path.startswith(
        prefix
    ):
        return None

    mongo_id = storage_path[
        len(prefix):
    ].strip()

    if not mongo_id:
        return None

    return mongo_id


# ============================================================
# MySQL Query
# ============================================================

def get_latest_raw_document(
    article_id
):
    """
    直接從 MySQL raw_documents 取得指定 article
    的最新 RawDocument。

    不依賴 RawDocumentRepository API。
    """

    conn = None
    cursor = None

    try:

        conn = get_connection()

        if conn is None:

            print(
                "[FAIL] MySQL connection failed."
            )

            return None

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT
                id,
                article_id,
                original_url,
                storage_path,
                file_hash,
                file_size
            FROM raw_documents
            WHERE article_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                article_id,
            )
        )

        row = cursor.fetchone()

        return row

    except Exception as e:

        print()
        print(
            "[FAIL] Failed to query MySQL "
            "raw_documents."
        )

        print(
            f"       Error : {e}"
        )

        return None

    finally:

        if cursor is not None:

            cursor.close()

        if conn is not None:

            conn.close()


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print(
        "AutoSearch V4"
    )
    print(
        "MySQL RawDocument -> MongoDB Raw HTML Check"
    )
    print("=" * 60)

    # ========================================================
    # Initialize MongoDB
    # ========================================================

    print()
    print(
        "Initializing Repositories"
    )
    print("-" * 60)

    try:

        raw_html_repo = (
            RawHTMLRepository()
        )

        print(
            "[OK] RawHTMLRepository initialized."
        )

    except Exception as e:

        print(
            "[FAIL] RawHTMLRepository "
            "initialization failed."
        )

        print(
            f"       Error : {e}"
        )

        return

    # ========================================================
    # MySQL
    # ========================================================

    print()
    print(
        "Checking MySQL raw_documents"
    )
    print("-" * 60)

    print(
        f"Mode : latest RawDocument "
        f"for article_id={TEST_ARTICLE_ID}"
    )

    raw_document = get_latest_raw_document(
        TEST_ARTICLE_ID
    )

    if raw_document is None:

        print()
        print(
            "[FAIL] No RawDocument found."
        )

        print(
            f"       article_id = "
            f"{TEST_ARTICLE_ID}"
        )

        return

    print(
        "[OK] MySQL RawDocument found."
    )

    # ========================================================
    # MySQL Fields
    # ========================================================

    raw_id = raw_document.get(
        "id"
    )

    raw_article_id = raw_document.get(
        "article_id"
    )

    raw_url = raw_document.get(
        "original_url"
    )

    raw_storage_path = raw_document.get(
        "storage_path"
    )

    raw_hash = raw_document.get(
        "file_hash"
    )

    raw_file_size = raw_document.get(
        "file_size"
    )

    print()
    print(
        "MySQL RawDocument"
    )
    print("-" * 60)

    print(
        f"id            : {raw_id}"
    )

    print(
        f"article_id    : {raw_article_id}"
    )

    print(
        f"original_url  : {raw_url}"
    )

    print(
        f"storage_path  : {raw_storage_path}"
    )

    print(
        f"file_hash     : {raw_hash}"
    )

    print(
        f"file_size     : {raw_file_size}"
    )

    # ========================================================
    # MySQL Validation
    # ========================================================

    print()
    print(
        "MySQL Validation"
    )
    print("-" * 60)

    passed = True

    if raw_id is None:

        print(
            "[FAIL] RawDocument.id missing."
        )

        passed = False

    else:

        print(
            "[OK] RawDocument.id"
        )

    if raw_article_id != TEST_ARTICLE_ID:

        print(
            "[FAIL] RawDocument article_id mismatch."
        )

        print(
            f"       Expected : "
            f"{TEST_ARTICLE_ID}"
        )

        print(
            f"       MySQL    : "
            f"{raw_article_id}"
        )

        passed = False

    else:

        print(
            "[OK] RawDocument article_id"
        )

    if not raw_url:

        print(
            "[FAIL] RawDocument original_url missing."
        )

        passed = False

    else:

        print(
            "[OK] RawDocument original_url"
        )

    if not raw_hash:

        print(
            "[FAIL] RawDocument file_hash missing."
        )

        passed = False

    else:

        print(
            "[OK] RawDocument file_hash"
        )

    if raw_file_size is None:

        print(
            "[FAIL] RawDocument file_size missing."
        )

        passed = False

    else:

        print(
            "[OK] RawDocument file_size"
        )

    # ========================================================
    # MongoDB Reference
    # ========================================================

    print()
    print(
        "Checking MongoDB Storage Reference"
    )
    print("-" * 60)

    mongo_id = extract_mongo_id(
        raw_storage_path
    )

    if not mongo_id:

        print(
            "[FAIL] Invalid MongoDB storage_path."
        )

        print(
            f"       storage_path = "
            f"{raw_storage_path}"
        )

        print()
        print("=" * 60)
        print(
            "[FAIL] MySQL -> MongoDB "
            "check failed."
        )
        print("=" * 60)

        return

    print(
        "[OK] storage_path points to MongoDB"
    )

    print(
        f"MongoDB document ID : {mongo_id}"
    )

    # ========================================================
    # MongoDB
    # ========================================================

    print()
    print(
        "Checking MongoDB raw_html"
    )
    print("-" * 60)

    try:

        raw_html = (
            raw_html_repo.find_by_id(
                mongo_id
            )
        )

    except Exception as e:

        print(
            "[FAIL] MongoDB query failed."
        )

        print(
            f"       Error : {e}"
        )

        return

    if raw_html is None:

        print(
            "[FAIL] MongoDB raw_html "
            "document not found."
        )

        print(
            f"       MongoDB ID : "
            f"{mongo_id}"
        )

        return

    print(
        "[OK] MongoDB raw_html document found."
    )

    # ========================================================
    # MongoDB Fields
    # ========================================================

    mongo_article_id = raw_html.get(
        "article_id"
    )

    mongo_document_id = raw_html.get(
        "document_id"
    )

    mongo_url = raw_html.get(
        "url"
    )

    mongo_hash = raw_html.get(
        "content_hash"
    )

    mongo_html = raw_html.get(
        "html"
    )

    print()
    print(
        "MongoDB Raw HTML"
    )
    print("-" * 60)

    print(
        f"article_id   : {mongo_article_id}"
    )

    print(
        f"document_id  : {mongo_document_id}"
    )

    print(
        f"url          : {mongo_url}"
    )

    print(
        f"content_hash : {mongo_hash}"
    )

    print(
        f"html_exists  : "
        f"{mongo_html is not None}"
    )

    # ========================================================
    # Consistency Validation
    # ========================================================

    print()
    print(
        "Consistency Validation"
    )
    print("-" * 60)

    # --------------------------------------------------------
    # 1. Article ID
    # --------------------------------------------------------

    if mongo_article_id != raw_article_id:

        print(
            "[FAIL] MySQL ↔ MongoDB article_id"
        )

        print(
            f"       MySQL    : "
            f"{raw_article_id}"
        )

        print(
            f"       MongoDB  : "
            f"{mongo_article_id}"
        )

        passed = False

    else:

        print(
            "[OK] MySQL ↔ MongoDB article_id"
        )

    # --------------------------------------------------------
    # 2. URL
    # --------------------------------------------------------

    if mongo_url != raw_url:

        print(
            "[FAIL] MySQL ↔ MongoDB URL mismatch"
        )

        print(
            f"       MySQL    : "
            f"{raw_url}"
        )

        print(
            f"       MongoDB  : "
            f"{mongo_url}"
        )

        passed = False

    else:

        print(
            "[OK] MySQL ↔ MongoDB URL"
        )

    # --------------------------------------------------------
    # 3. Hash
    # --------------------------------------------------------

    if mongo_hash != raw_hash:

        print(
            "[FAIL] MySQL file_hash ↔ "
            "MongoDB content_hash mismatch"
        )

        print(
            f"       MySQL    : "
            f"{raw_hash}"
        )

        print(
            f"       MongoDB  : "
            f"{mongo_hash}"
        )

        passed = False

    else:

        print(
            "[OK] MySQL ↔ MongoDB hash"
        )

    # --------------------------------------------------------
    # 4. HTML
    # --------------------------------------------------------

    if mongo_html is None:

        print(
            "[FAIL] MongoDB HTML missing."
        )

        passed = False

    elif not str(mongo_html):

        print(
            "[FAIL] MongoDB HTML empty."
        )

        passed = False

    else:

        print(
            "[OK] MongoDB HTML exists"
        )

    # --------------------------------------------------------
    # 5. File Size
    # --------------------------------------------------------

    if mongo_html is not None:

        mongo_file_size = len(
            str(
                mongo_html
            ).encode(
                "utf-8"
            )
        )

        if raw_file_size != mongo_file_size:

            print(
                "[FAIL] file_size mismatch"
            )

            print(
                f"       MySQL file_size : "
                f"{raw_file_size}"
            )

            print(
                f"       MongoDB HTML    : "
                f"{mongo_file_size}"
            )

            passed = False

        else:

            print(
                "[OK] MySQL ↔ MongoDB file_size"
            )

    # ========================================================
    # Final
    # ========================================================

    print()
    print("=" * 60)

    if passed:

        print(
            "[PASS] MySQL RawDocument -> "
            "MongoDB Raw HTML check passed."
        )

        print()
        print(
            "Confirmed:"
        )

        print(
            "  MySQL raw_documents"
        )

        print(
            "        ↓"
        )

        print(
            "  storage_path"
        )

        print(
            "        ↓"
        )

        print(
            "  MongoDB raw_html"
        )

        print()
        print(
            "HTML is successfully stored "
            "and retrievable from MongoDB."
        )

    else:

        print(
            "[FAIL] MySQL RawDocument -> "
            "MongoDB Raw HTML check failed."
        )

    print("=" * 60)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    main()