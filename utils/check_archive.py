"""
utils/check_archive.py

AutoSearch V4

Knowledge Archive Verification Tool

功能：

1. 檢查 articles
2. 檢查 raw_documents
3. 檢查 archive_versions
4. 檢查 ai_tasks
5. 驗證 Raw HTML 實體檔案
6. 驗證 SHA256 Hash
7. 驗證 Archive Version
8. 驗證 Article -> Raw Document -> Archive Version
9. 驗證 AI Task Coverage

注意：

Database Schema 不會被修改。
"""

import hashlib
from pathlib import Path

from database.connection import get_connection


# ============================================================
# Project Root
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# Archive Root
# ============================================================

ARCHIVE_ROOT = PROJECT_ROOT / "archive" / "html"


# ============================================================
# Database
# ============================================================

TABLES = [
    "articles",
    "raw_documents",
    "archive_versions",
    "ai_tasks",
]


# ============================================================
# Utility
# ============================================================

def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def calculate_sha256(path):
    """
    計算檔案 SHA256。
    """

    sha256 = hashlib.sha256()

    try:

        with open(path, "rb") as f:

            while True:

                data = f.read(1024 * 1024)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    except Exception:
        return None


def resolve_archive_path(storage_path):
    """
    將 Database 中的 storage_path
    轉換成實際 Windows Path。

    Database 範例：

    archive/html\\2026\\08\\08\\xxxxx.html

    實際：

    C:\\...\\AutoSearchV2\\archive\\html\\2026\\08\\08\\xxxxx.html
    """

    if not storage_path:
        return None

    # 統一 Windows / Unix separator
    normalized = str(storage_path).replace("\\", "/")

    # Database path 通常從 archive/html 開始
    prefix = "archive/html/"

    if normalized.startswith(prefix):

        relative_path = normalized[len(prefix):]

        return ARCHIVE_ROOT.joinpath(
            *relative_path.split("/")
        )

    # 如果 DB 已經只存相對 archive 路徑
    if normalized.startswith("html/"):

        relative_path = normalized[len("html/"):]

        return ARCHIVE_ROOT.joinpath(
            *relative_path.split("/")
        )

    # 最後嘗試直接從 Project Root 解決
    return PROJECT_ROOT.joinpath(
        *normalized.split("/")
    )


# ============================================================
# Table Count
# ============================================================

def check_table(cursor, table):

    cursor.execute(
        f"SELECT COUNT(*) AS count FROM {table}"
    )

    row = cursor.fetchone()

    if row is None:
        return 0

    # Dict cursor
    if isinstance(row, dict):

        return row.get("count", 0)

    # Tuple cursor
    return row[0]


# ============================================================
# Article Check
# ============================================================

def check_articles(cursor):

    section("ARTICLE CHECK")

    cursor.execute(
        """
        SELECT
            id,
            title,
            status
        FROM articles
        ORDER BY id
        """
    )

    rows = cursor.fetchall()

    for row in rows:

        if isinstance(row, dict):

            article_id = row["id"]
            title = row["title"]
            status = row["status"]

        else:

            article_id = row[0]
            title = row[1]
            status = row[2]

        print(
            f"[ARTICLE] "
            f"id={article_id} | "
            f"title={title} | "
            f"status={status}"
        )

    return len(rows)


# ============================================================
# Raw Document Check
# ============================================================

def check_raw_documents(cursor):

    section("RAW DOCUMENT CHECK")

    cursor.execute(
        """
        SELECT
            id,
            article_id,
            storage_path,
            file_hash,
            file_size
        FROM raw_documents
        ORDER BY id
        """
    )

    rows = cursor.fetchall()

    success = True

    for row in rows:

        if isinstance(row, dict):

            raw_id = row["id"]
            article_id = row["article_id"]
            storage_path = row["storage_path"]
            db_hash = row["file_hash"]
            db_size = row["file_size"]

        else:

            raw_id = row[0]
            article_id = row[1]
            storage_path = row[2]
            db_hash = row[3]
            db_size = row[4]

        actual_path = resolve_archive_path(
            storage_path
        )

        if actual_path is None:

            print(
                f"[RAW] id={raw_id} | "
                f"article={article_id} | "
                f"INVALID PATH"
            )

            success = False
            continue

        if not actual_path.exists():

            print(
                f"[RAW] id={raw_id} | "
                f"article={article_id} | "
                f"file=MISSING / HASH ERROR"
            )

            print(
                f"      hash={db_hash}"
            )

            print(
                f"      db_path={storage_path}"
            )

            print(
                f"      actual_path={actual_path}"
            )

            success = False
            continue

        actual_size = actual_path.stat().st_size

        actual_hash = calculate_sha256(
            actual_path
        )

        if (
            actual_size != db_size
            or actual_hash != db_hash
        ):

            print(
                f"[RAW] id={raw_id} | "
                f"article={article_id} | "
                f"file=MISSING / HASH ERROR"
            )

            print(
                f"      db_size={db_size}"
            )

            print(
                f"      actual_size={actual_size}"
            )

            print(
                f"      db_hash={db_hash}"
            )

            print(
                f"      actual_hash={actual_hash}"
            )

            print(
                f"      db_path={storage_path}"
            )

            print(
                f"      actual_path={actual_path}"
            )

            success = False

        else:

            print(
                f"[OK] raw={raw_id} | "
                f"article={article_id} | "
                f"size={actual_size} | "
                f"hash={actual_hash}"
            )

    return success


# ============================================================
# Archive Version Check
# ============================================================

def check_archive_versions(cursor):

    section("ARCHIVE VERSION CHECK")

    cursor.execute(
        """
        SELECT
            id,
            article_id,
            raw_document_id,
            version_number,
            file_hash,
            storage_path
        FROM archive_versions
        ORDER BY article_id, version_number
        """
    )

    rows = cursor.fetchall()

    success = True

    for row in rows:

        if isinstance(row, dict):

            version_id = row["id"]
            article_id = row["article_id"]
            raw_id = row["raw_document_id"]
            version = row["version_number"]
            db_hash = row["file_hash"]
            storage_path = row["storage_path"]

        else:

            version_id = row[0]
            article_id = row[1]
            raw_id = row[2]
            version = row[3]
            db_hash = row[4]
            storage_path = row[5]

        actual_path = resolve_archive_path(
            storage_path
        )

        if (
            actual_path is None
            or not actual_path.exists()
        ):

            print(
                f"[VERSION] "
                f"id={version_id} | "
                f"article={article_id} | "
                f"raw={raw_id} | "
                f"version={version} | "
                f"file=MISSING / HASH ERROR"
            )

            print(
                f"          hash={db_hash}"
            )

            print(
                f"          db_path={storage_path}"
            )

            print(
                f"          actual_path={actual_path}"
            )

            success = False

            continue

        actual_hash = calculate_sha256(
            actual_path
        )

        if actual_hash != db_hash:

            print(
                f"[VERSION] "
                f"id={version_id} | "
                f"article={article_id} | "
                f"raw={raw_id} | "
                f"version={version} | "
                f"HASH ERROR"
            )

            print(
                f"          db_hash={db_hash}"
            )

            print(
                f"          actual_hash={actual_hash}"
            )

            success = False

        else:

            print(
                f"[OK] version={version_id} | "
                f"article={article_id} | "
                f"raw={raw_id} | "
                f"version={version}"
            )

    return success


# ============================================================
# AI Task Check
# ============================================================

def check_ai_tasks(cursor):

    section("AI TASK CHECK")

    cursor.execute(
        """
        SELECT
            id,
            article_id,
            task_type,
            status,
            retry_count
        FROM ai_tasks
        ORDER BY id
        """
    )

    rows = cursor.fetchall()

    for row in rows:

        if isinstance(row, dict):

            task_id = row["id"]
            article_id = row["article_id"]
            task_type = row["task_type"]
            status = row["status"]
            retry_count = row["retry_count"]

        else:

            task_id = row[0]
            article_id = row[1]
            task_type = row[2]
            status = row[3]
            retry_count = row[4]

        print(
            f"[AI TASK] "
            f"id={task_id} | "
            f"article={article_id} | "
            f"type={task_type} | "
            f"status={status} | "
            f"retry={retry_count}"
        )

    return len(rows)


# ============================================================
# Archive Relationship
# ============================================================

def check_relationship(cursor):

    section("ARCHIVE RELATIONSHIP CHECK")

    cursor.execute(
        """
        SELECT
            av.article_id,
            av.version_number,
            av.raw_document_id,
            rd.article_id AS raw_article_id
        FROM archive_versions av
        JOIN raw_documents rd
            ON av.raw_document_id = rd.id
        ORDER BY av.article_id
        """
    )

    rows = cursor.fetchall()

    success = True

    for row in rows:

        if isinstance(row, dict):

            article_id = row["article_id"]
            version = row["version_number"]
            raw_id = row["raw_document_id"]
            raw_article_id = row["raw_article_id"]

        else:

            article_id = row[0]
            version = row[1]
            raw_id = row[2]
            raw_article_id = row[3]

        if article_id == raw_article_id:

            print(
                f"[OK] "
                f"Article={article_id} "
                f"Version={version} "
                f"RawDocument={raw_id}"
            )

        else:

            print(
                f"[ERROR] "
                f"Article={article_id} "
                f"RawDocument={raw_id} "
                f"belongs_to={raw_article_id}"
            )

            success = False

    return success


# ============================================================
# Version Number Check
# ============================================================

def check_version_numbers(cursor):

    section("VERSION NUMBER CHECK")

    cursor.execute(
        """
        SELECT
            article_id,
            MIN(version_number) AS min_version,
            MAX(version_number) AS max_version,
            COUNT(*) AS version_count
        FROM archive_versions
        GROUP BY article_id
        ORDER BY article_id
        """
    )

    rows = cursor.fetchall()

    success = True

    for row in rows:

        if isinstance(row, dict):

            article_id = row["article_id"]
            min_version = row["min_version"]
            max_version = row["max_version"]
            count = row["version_count"]

        else:

            article_id = row[0]
            min_version = row[1]
            max_version = row[2]
            count = row[3]

        expected = list(
            range(
                1,
                max_version + 1
            )
        )

        cursor.execute(
            """
            SELECT version_number
            FROM archive_versions
            WHERE article_id = %s
            ORDER BY version_number
            """,
            (article_id,)
        )

        version_rows = cursor.fetchall()

        actual = []

        for version_row in version_rows:

            if isinstance(version_row, dict):
                actual.append(
                    version_row["version_number"]
                )
            else:
                actual.append(
                    version_row[0]
                )

        if actual == expected:

            print(
                f"[OK] article={article_id} | "
                f"versions={min_version}-{max_version}"
            )

        else:

            print(
                f"[ERROR] article={article_id} | "
                f"versions={actual}"
            )

            success = False

    return success


# ============================================================
# Article Archive Coverage
# ============================================================

def check_archive_coverage(cursor):

    section("ARTICLE ARCHIVE COVERAGE")

    cursor.execute(
        """
        SELECT
            a.id AS article_id,

            (
                SELECT COUNT(*)
                FROM raw_documents rd
                WHERE rd.article_id = a.id
            ) AS raw_count,

            (
                SELECT COUNT(*)
                FROM archive_versions av
                WHERE av.article_id = a.id
            ) AS version_count

        FROM articles a

        ORDER BY a.id
        """
    )

    rows = cursor.fetchall()

    success = True

    for row in rows:

        if isinstance(row, dict):

            article_id = row["article_id"]
            raw_count = row["raw_count"]
            version_count = row["version_count"]

        else:

            article_id = row[0]
            raw_count = row[1]
            version_count = row[2]

        if raw_count >= 1 and version_count >= 1:

            print(
                f"[OK] article={article_id} | "
                f"raw={raw_count} | "
                f"versions={version_count}"
            )

        else:

            print(
                f"[ERROR] article={article_id} | "
                f"raw={raw_count} | "
                f"versions={version_count}"
            )

            success = False

    return success


# ============================================================
# AI Task Coverage
# ============================================================

def check_ai_task_coverage(cursor):

    section("AI TASK COVERAGE")

    cursor.execute(
        """
        SELECT
            a.id AS article_id,
            COUNT(t.id) AS task_count
        FROM articles a
        LEFT JOIN ai_tasks t
            ON a.id = t.article_id
        GROUP BY a.id
        ORDER BY a.id
        """
    )

    rows = cursor.fetchall()

    success = True

    for row in rows:

        if isinstance(row, dict):

            article_id = row["article_id"]
            task_count = row["task_count"]

        else:

            article_id = row[0]
            task_count = row[1]

        if task_count >= 1:

            print(
                f"[OK] article={article_id} "
                f"AI tasks={task_count}"
            )

        else:

            print(
                f"[ERROR] article={article_id} "
                f"AI tasks=0"
            )

            success = False

    return success


# ============================================================
# Main
# ============================================================

def check_archive():

    print()
    print("=" * 70)
    print(" AutoSearch V4 Knowledge Archive Check")
    print("=" * 70)

    print()
    print(
        f"Archive Root: {ARCHIVE_ROOT}"
    )

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    conn = get_connection()

    if conn is None:

        raise RuntimeError(
            "Database connection failed"
        )

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        # ----------------------------------------------------
        # Table Count
        # ----------------------------------------------------

        counts = {}

        for table in TABLES:

            section(
                f"TABLE: {table}"
            )

            count = check_table(
                cursor,
                table
            )

            counts[table] = count

            print(
                f"COUNT = {count}"
            )

        # ----------------------------------------------------
        # Article
        # ----------------------------------------------------

        check_articles(
            cursor
        )

        # ----------------------------------------------------
        # Raw Documents
        # ----------------------------------------------------

        raw_files_ok = check_raw_documents(
            cursor
        )

        # ----------------------------------------------------
        # Archive Versions
        # ----------------------------------------------------

        archive_files_ok = check_archive_versions(
            cursor
        )

        # ----------------------------------------------------
        # AI Tasks
        # ----------------------------------------------------

        check_ai_tasks(
            cursor
        )

        # ----------------------------------------------------
        # Relationship
        # ----------------------------------------------------

        relationship_ok = check_relationship(
            cursor
        )

        # ----------------------------------------------------
        # Version
        # ----------------------------------------------------

        version_ok = check_version_numbers(
            cursor
        )

        # ----------------------------------------------------
        # Coverage
        # ----------------------------------------------------

        archive_coverage_ok = check_archive_coverage(
            cursor
        )

        # ----------------------------------------------------
        # AI Coverage
        # ----------------------------------------------------

        ai_coverage_ok = check_ai_task_coverage(
            cursor
        )

        # ----------------------------------------------------
        # Final
        # ----------------------------------------------------

        section("FINAL RESULT")

        print(
            f"Articles         : "
            f"{counts['articles']}"
        )

        print(
            f"Raw Documents    : "
            f"{counts['raw_documents']}"
        )

        print(
            f"Archive Versions : "
            f"{counts['archive_versions']}"
        )

        print(
            f"AI Tasks         : "
            f"{counts['ai_tasks']}"
        )

        print()

        print(
            "Archive Relation : "
            + (
                "OK"
                if relationship_ok
                else "FAILED"
            )
        )

        print(
            "Version History  : "
            + (
                "OK"
                if version_ok
                else "FAILED"
            )
        )

        print(
            "Raw Files        : "
            + (
                "OK"
                if raw_files_ok
                else "FAILED"
            )
        )

        print(
            "Archive Files    : "
            + (
                "OK"
                if archive_files_ok
                else "FAILED"
            )
        )

        print(
            "Archive Coverage : "
            + (
                "OK"
                if archive_coverage_ok
                else "FAILED"
            )
        )

        print(
            "AI Task Coverage : "
            + (
                "OK"
                if ai_coverage_ok
                else "FAILED"
            )
        )

        all_ok = (
            relationship_ok
            and version_ok
            and raw_files_ok
            and archive_files_ok
            and archive_coverage_ok
            and ai_coverage_ok
        )

        print()

        if all_ok:

            print(
                "✅ Knowledge Archive Check PASSED"
            )

        else:

            print(
                "❌ Knowledge Archive Check FAILED"
            )

    finally:

        cursor.close()
        conn.close()

    print()
    print("=" * 70)
    print(" Check Finished")
    print("=" * 70)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    check_archive()