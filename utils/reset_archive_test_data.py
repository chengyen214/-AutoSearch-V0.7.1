"""
utils/reset_archive_test_data.py

AutoSearch V4

Archive Test Data Reset

用途：

    清除 Archive Storage / Archive Version
    測試所產生的測試資料。

本工具只處理：

    document_id LIKE "test-archive-%"

不依照 article_id 全部刪除。

因此：

    Article 89 Version 1 ~ 7
        ↓
    保留

測試產生的：

    Version 8
    test-archive-different-url-*
    test-archive-same-url-same-html-*
        ↓
    清除

清除範圍：

    1. MySQL archive_versions
    2. MySQL raw_documents
    3. MongoDB raw_html

注意：

    本工具是測試資料清理工具。
    不應用於正式 Archive 清理。
"""

from database.connection import get_connection

from database.raw_html_repository import (
    RawHTMLRepository
)


TEST_DOCUMENT_PREFIX = "test-archive-"


def print_section(title):

    print()
    print(title)
    print("-" * 60)


def get_test_raw_documents():

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

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
            WHERE original_url LIKE %s
            ORDER BY id ASC
            """,
            (
                TEST_DOCUMENT_PREFIX + "%",
            )
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conn.close()


def get_test_archive_versions(
    raw_document_ids
):

    if not raw_document_ids:

        return []

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        placeholders = ",".join(
            ["%s"] * len(raw_document_ids)
        )

        sql = f"""
        SELECT
            id,
            article_id,
            version_number,
            raw_document_id,
            file_hash,
            file_size,
            storage_path
        FROM archive_versions
        WHERE raw_document_id IN ({placeholders})
        ORDER BY article_id, version_number
        """

        cursor.execute(
            sql,
            tuple(raw_document_ids)
        )

        return cursor.fetchall()

    finally:

        cursor.close()
        conn.close()


def extract_mongo_id(
    storage_path
):

    prefix = "mongodb://raw_html/"

    if not storage_path:

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


def delete_archive_versions(
    raw_document_ids
):

    if not raw_document_ids:

        return 0

    conn = get_connection()

    cursor = conn.cursor()

    try:

        placeholders = ",".join(
            ["%s"] * len(raw_document_ids)
        )

        sql = f"""
        DELETE FROM archive_versions
        WHERE raw_document_id IN ({placeholders})
        """

        cursor.execute(
            sql,
            tuple(raw_document_ids)
        )

        deleted = cursor.rowcount

        conn.commit()

        return deleted

    except Exception:

        conn.rollback()

        raise

    finally:

        cursor.close()
        conn.close()


def delete_raw_documents(
    raw_document_ids
):

    if not raw_document_ids:

        return 0

    conn = get_connection()

    cursor = conn.cursor()

    try:

        placeholders = ",".join(
            ["%s"] * len(raw_document_ids)
        )

        sql = f"""
        DELETE FROM raw_documents
        WHERE id IN ({placeholders})
        """

        cursor.execute(
            sql,
            tuple(raw_document_ids)
        )

        deleted = cursor.rowcount

        conn.commit()

        return deleted

    except Exception:

        conn.rollback()

        raise

    finally:

        cursor.close()
        conn.close()


def delete_mongodb_documents(
    mongo_ids
):

    if not mongo_ids:

        return 0

    raw_html_repo = RawHTMLRepository()

    deleted = 0

    for mongo_id in mongo_ids:

        try:

            result = raw_html_repo.delete_by_id(
                mongo_id
            )

            if result:

                deleted += 1

        except Exception as e:

            print(
                f"[WARN] Failed to delete "
                f"MongoDB document {mongo_id}: {e}"
            )

    return deleted


def main():

    print("=" * 60)
    print("AutoSearch V4")
    print("Archive Test Data Reset")
    print("=" * 60)

    # ==========================================
    # Find Test Raw Documents
    # ==========================================

    print_section(
        "Checking Test RawDocuments"
    )

    raw_documents = (
        get_test_raw_documents()
    )

    if not raw_documents:

        print(
            "[OK] No test RawDocuments found."
        )

        print()
        print("=" * 60)
        print(
            "[PASS] Nothing to reset."
        )
        print("=" * 60)

        return

    print(
        f"Found {len(raw_documents)} "
        f"test RawDocument(s)."
    )

    raw_document_ids = []

    mongo_ids = []

    for row in raw_documents:

        raw_id = row["id"]

        raw_document_ids.append(
            raw_id
        )

        mongo_id = extract_mongo_id(
            row["storage_path"]
        )

        if mongo_id:

            mongo_ids.append(
                mongo_id
            )

        print()
        print(
            f"RawDocument ID : {raw_id}"
        )

        print(
            f"Article ID     : {row['article_id']}"
        )

        print(
            f"URL            : {row['original_url']}"
        )

        print(
            f"Storage Path   : {row['storage_path']}"
        )

        print(
            f"File Hash      : {row['file_hash']}"
        )

    # ==========================================
    # Find Test Archive Versions
    # ==========================================

    print_section(
        "Checking Test Archive Versions"
    )

    versions = (
        get_test_archive_versions(
            raw_document_ids
        )
    )

    if not versions:

        print(
            "[OK] No test ArchiveVersion found."
        )

    else:

        print(
            f"Found {len(versions)} "
            f"test ArchiveVersion(s)."
        )

        for version in versions:

            print()

            print(
                f"ArchiveVersion ID : "
                f"{version['id']}"
            )

            print(
                f"Article ID       : "
                f"{version['article_id']}"
            )

            print(
                f"Version          : "
                f"{version['version_number']}"
            )

            print(
                f"RawDocument ID   : "
                f"{version['raw_document_id']}"
            )

            print(
                f"Storage Path     : "
                f"{version['storage_path']}"
            )

    # ==========================================
    # MongoDB References
    # ==========================================

    print_section(
        "MongoDB Test References"
    )

    if mongo_ids:

        for mongo_id in mongo_ids:

            print(
                f"MongoDB ID : {mongo_id}"
            )

    else:

        print(
            "[OK] No MongoDB references found."
        )

    # ==========================================
    # Safety Confirmation
    # ==========================================

    print_section(
        "Reset Confirmation"
    )

    print(
        "The following test data will be deleted:"
    )

    print(
        f"  RawDocuments    : "
        f"{len(raw_document_ids)}"
    )

    print(
        f"  ArchiveVersions : "
        f"{len(versions)}"
    )

    print(
        f"  MongoDB HTML    : "
        f"{len(mongo_ids)}"
    )

    print()
    print(
        "Only records identified by:"
    )

    print(
        f'    original_url LIKE "{TEST_DOCUMENT_PREFIX}%"'
    )

    print(
        "will be removed."
    )

    print()
    print(
        "Existing Article 89 versions "
        "that are not test data will remain."
    )

    print()

    confirmation = input(
        "Type RESET to continue: "
    ).strip()

    if confirmation != "RESET":

        print()
        print(
            "[CANCELLED] Reset cancelled."
        )

        return

    # ==========================================
    # Delete Archive Versions
    # ==========================================

    print_section(
        "Deleting Archive Versions"
    )

    deleted_versions = (
        delete_archive_versions(
            raw_document_ids
        )
    )

    print(
        f"[OK] Deleted ArchiveVersions: "
        f"{deleted_versions}"
    )

    # ==========================================
    # Delete MongoDB Raw HTML
    # ==========================================

    print_section(
        "Deleting MongoDB raw_html"
    )

    deleted_mongo = (
        delete_mongodb_documents(
            mongo_ids
        )
    )

    print(
        f"[OK] Deleted MongoDB documents: "
        f"{deleted_mongo}"
    )

    # ==========================================
    # Delete Raw Documents
    # ==========================================

    print_section(
        "Deleting MySQL raw_documents"
    )

    deleted_raw = (
        delete_raw_documents(
            raw_document_ids
        )
    )

    print(
        f"[OK] Deleted RawDocuments: "
        f"{deleted_raw}"
    )

    # ==========================================
    # Final
    # ==========================================

    print()
    print("=" * 60)

    print(
        "[PASS] Archive test data reset completed."
    )

    print("=" * 60)


if __name__ == "__main__":

    main()