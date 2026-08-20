"""
utils/check_archive_storage_consistency.py

AutoSearch V4

Archive Storage Consistency Check

驗證：

    ArchiveVersion
        |
        | raw_document_id
        v
    MySQL raw_documents
        |
        | file_hash
        v
    Archive Content Identity

    ArchiveVersion
        |
        | storage_path
        v
    MongoDB raw_html


V4 Archive Storage 設計：

    RawDocument
        ↓
    Content Identity

    主要 Identity：

        file_hash
        file_size

    ArchiveVersion
        ↓
    Version Identity

    主要資訊：

        raw_document_id
        file_hash
        file_size
        storage_path

    MongoDB raw_html
        ↓
    實際 Archive Storage


重要：

    RawDocument 可以因為相同 file_hash
    被不同 Archive Version 共用。

    因此：

        RawDocument.original_url
            不一定等於
        MongoDB.url

    也因此：

        RawDocument.storage_path
            不一定等於
        ArchiveVersion.storage_path

    本測試不再要求上述兩者一致。

真正必須成立：

    ArchiveVersion
        ↓
        raw_document_id
        ↓
    RawDocument.id

    ArchiveVersion.file_hash
        ==
    RawDocument.file_hash

    ArchiveVersion.file_hash
        ==
    MongoDB.content_hash

    ArchiveVersion.storage_path
        ↓
    MongoDB raw_html document

    MongoDB HTML
        ↓
    file_size 正確


IMPORTANT:

    本測試不使用 article_id
    查找 RawDocument。

    RawDocument 必須由：

        ArchiveVersion.raw_document_id

    精確取得。
"""

from services.archive_service import (
    ArchiveService
)

from database.raw_document_repository import (
    RawDocumentRepository
)

from database.archive_version_repository import (
    ArchiveVersionRepository
)

from database.raw_html_repository import (
    RawHTMLRepository
)


def get_value(
    obj,
    name,
    default=None
):
    """
    安全取得 Model / Object 欄位。
    """

    return getattr(
        obj,
        name,
        default
    )


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

    storage_path = str(
        storage_path
    ).strip()

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


def find_raw_document_by_exact_id(
    raw_repo,
    raw_document_id
):
    """
    嚴格依 RawDocument Primary Key 查詢。

    不允許：

        article_id
        URL
        file_hash

    作為 fallback。

    原因：

        ArchiveVersion.raw_document_id
        必須直接對應：

        raw_documents.id
    """

    if raw_document_id is None:

        return None

    # ==========================================
    # Preferred API
    # ==========================================

    if hasattr(
        raw_repo,
        "get_by_id"
    ):

        try:

            return raw_repo.get_by_id(
                raw_document_id
            )

        except Exception as e:

            print(
                "[WARN] RawDocumentRepository."
                f"get_by_id() failed: {e}"
            )

    # ==========================================
    # Compatibility API
    # ==========================================

    if hasattr(
        raw_repo,
        "find_by_id"
    ):

        try:

            return raw_repo.find_by_id(
                raw_document_id
            )

        except Exception as e:

            print(
                "[WARN] RawDocumentRepository."
                f"find_by_id() failed: {e}"
            )

    return None


def main():

    print("=" * 60)
    print("AutoSearch V4")
    print("Archive Storage Consistency Check")
    print("=" * 60)

    # ==========================================
    # Test Article
    # ==========================================

    article_id = 89

    # ==========================================
    # Initialize Repositories
    # ==========================================

    print()
    print("Initializing Repositories")
    print("-" * 60)

    archive_service = ArchiveService()

    raw_repo = RawDocumentRepository()

    version_repo = ArchiveVersionRepository()

    raw_html_repo = RawHTMLRepository()

    print(
        "[OK] ArchiveService initialized."
    )

    print(
        "[OK] RawDocumentRepository initialized."
    )

    print(
        "[OK] ArchiveVersionRepository initialized."
    )

    print(
        "[OK] RawHTMLRepository initialized."
    )

    # ==========================================
    # Get Versions
    # ==========================================

    print()
    print("Checking Article Versions")
    print("-" * 60)

    versions = (
        archive_service.get_versions(
            article_id
        )
    )

    if not versions:

        print(
            "[FAIL] No archive versions found."
        )

        return

    print(
        f"Total versions: {len(versions)}"
    )

    for version in versions:

        print(
            f"  Version "
            f"{get_value(version, 'version_number')}"
        )

    # ==========================================
    # Get Latest Version
    # ==========================================

    latest_version = (
        archive_service.get_latest_version(
            article_id
        )
    )

    if latest_version is None:

        print(
            "[FAIL] Latest archive version "
            "not found."
        )

        return

    version_number = get_value(
        latest_version,
        "version_number"
    )

    version_article_id = get_value(
        latest_version,
        "article_id"
    )

    raw_document_id = get_value(
        latest_version,
        "raw_document_id"
    )

    version_hash = get_value(
        latest_version,
        "file_hash"
    )

    storage_path = get_value(
        latest_version,
        "storage_path"
    )

    version_file_size = get_value(
        latest_version,
        "file_size"
    )

    print()
    print("Latest Archive Version")
    print("-" * 60)

    print(
        f"article_id       : {version_article_id}"
    )

    print(
        f"version_number   : {version_number}"
    )

    print(
        f"raw_document_id  : {raw_document_id}"
    )

    print(
        f"file_hash        : {version_hash}"
    )

    print(
        f"file_size        : {version_file_size}"
    )

    print(
        f"storage_path     : {storage_path}"
    )

    # ==========================================
    # Validate ArchiveVersion
    # ==========================================

    print()
    print("Archive Version Validation")
    print("-" * 60)

    version_ok = True

    # ------------------------------------------
    # Article ID
    # ------------------------------------------

    if version_article_id != article_id:

        print(
            "[FAIL] ArchiveVersion article_id mismatch."
        )

        print(
            f"       Expected : {article_id}"
        )

        print(
            f"       Actual   : {version_article_id}"
        )

        version_ok = False

    else:

        print(
            "[OK] ArchiveVersion article_id"
        )

    # ------------------------------------------
    # Version Number
    # ------------------------------------------

    if version_number is None:

        print(
            "[FAIL] version_number is missing."
        )

        version_ok = False

    else:

        print(
            "[OK] version_number exists"
        )

    # ------------------------------------------
    # RawDocument ID
    # ------------------------------------------

    if raw_document_id is None:

        print(
            "[FAIL] raw_document_id is missing."
        )

        version_ok = False

    else:

        print(
            "[OK] raw_document_id exists"
        )

    # ------------------------------------------
    # File Hash
    # ------------------------------------------

    if not version_hash:

        print(
            "[FAIL] file_hash is missing."
        )

        version_ok = False

    else:

        print(
            "[OK] file_hash exists"
        )

    # ------------------------------------------
    # File Size
    # ------------------------------------------

    if version_file_size is None:

        print(
            "[FAIL] file_size is missing."
        )

        version_ok = False

    else:

        print(
            "[OK] file_size exists"
        )

    # ------------------------------------------
    # Storage Path
    # ------------------------------------------

    if not storage_path:

        print(
            "[FAIL] storage_path is missing."
        )

        version_ok = False

    elif not str(
        storage_path
    ).startswith(
        "mongodb://raw_html/"
    ):

        print(
            "[FAIL] storage_path does not "
            "point to MongoDB raw_html."
        )

        version_ok = False

    else:

        print(
            "[OK] storage_path points to MongoDB"
        )

    if not version_ok:

        print()
        print(
            "[FAIL] Archive Version validation failed."
        )

        return

    # ==========================================
    # Extract MongoDB ID
    #
    # IMPORTANT:
    #
    # MongoDB ID comes from:
    #
    #     ArchiveVersion.storage_path
    #
    # NOT:
    #
    #     RawDocument.storage_path
    #
    # NOT:
    #
    #     article_id
    #
    # NOT:
    #
    #     URL
    # ==========================================

    mongo_id = extract_mongo_id(
        storage_path
    )

    if not mongo_id:

        print()
        print(
            "[FAIL] Cannot extract MongoDB "
            "document ID from ArchiveVersion."
        )

        return

    print()
    print("Archive Storage Reference")
    print("-" * 60)

    print(
        f"MongoDB document ID : {mongo_id}"
    )

    # ==========================================
    # Find RawDocument
    #
    # ONLY:
    #
    #     ArchiveVersion.raw_document_id
    #
    # →
    #
    #     raw_documents.id
    # ==========================================

    print()
    print("Checking MySQL raw_documents")
    print("-" * 60)

    raw_document = (
        find_raw_document_by_exact_id(
            raw_repo,
            raw_document_id
        )
    )

    if raw_document is None:

        print(
            "[FAIL] MySQL raw_documents record "
            "not found by exact ID."
        )

        print(
            f"       raw_document_id = "
            f"{raw_document_id}"
        )

        return

    print(
        "[OK] MySQL raw_documents record found."
    )

    actual_raw_id = get_value(
        raw_document,
        "id"
    )

    raw_article_id = get_value(
        raw_document,
        "article_id"
    )

    raw_url = get_value(
        raw_document,
        "original_url"
    )

    raw_storage_path = get_value(
        raw_document,
        "storage_path"
    )

    raw_hash = get_value(
        raw_document,
        "file_hash"
    )

    raw_file_size = get_value(
        raw_document,
        "file_size"
    )

    print()
    print("RawDocument")
    print("-" * 60)

    print(
        f"id            : {actual_raw_id}"
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

    # ==========================================
    # Find MongoDB Raw HTML
    #
    # MongoDB ID MUST come from:
    #
    #     ArchiveVersion.storage_path
    # ==========================================

    print()
    print("Checking MongoDB raw_html")
    print("-" * 60)

    raw_html = (
        raw_html_repo.find_by_id(
            mongo_id
        )
    )

    if raw_html is None:

        print(
            "[FAIL] MongoDB raw_html document "
            "not found."
        )

        print(
            f"       MongoDB ID = {mongo_id}"
        )

        return

    print(
        "[OK] MongoDB raw_html document found."
    )

    mongo_article_id = raw_html.get(
        "article_id"
    )

    mongo_document_id = raw_html.get(
        "document_id"
    )

    mongo_url = raw_html.get(
        "url"
    )

    mongo_html = raw_html.get(
        "html"
    )

    mongo_hash = raw_html.get(
        "content_hash"
    )

    print()
    print("MongoDB Raw HTML")
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
        f"html_exists  : {mongo_html is not None}"
    )

    # ==========================================
    # Consistency Validation
    # ==========================================

    print()
    print("Consistency Validation")
    print("-" * 60)

    passed = True

    # ==========================================
    # 1. ArchiveVersion → RawDocument
    # ==========================================

    if actual_raw_id != raw_document_id:

        print(
            "[FAIL] ArchiveVersion → RawDocument "
            "relation mismatch."
        )

        print(
            f"       ArchiveVersion.raw_document_id : "
            f"{raw_document_id}"
        )

        print(
            f"       RawDocument.id                 : "
            f"{actual_raw_id}"
        )

        passed = False

    else:

        print(
            "[OK] ArchiveVersion → RawDocument relation"
        )

    # ==========================================
    # 2. Article ID
    # ==========================================

    if raw_article_id != article_id:

        print(
            "[FAIL] RawDocument article_id mismatch."
        )

        print(
            f"       Expected : {article_id}"
        )

        print(
            f"       MySQL    : {raw_article_id}"
        )

        passed = False

    else:

        print(
            "[OK] RawDocument article_id"
        )

    if mongo_article_id != article_id:

        print(
            "[FAIL] MongoDB article_id mismatch."
        )

        print(
            f"       Expected : {article_id}"
        )

        print(
            f"       MongoDB  : {mongo_article_id}"
        )

        passed = False

    else:

        print(
            "[OK] MongoDB article_id"
        )

    # ==========================================
    # 3. URL
    #
    # IMPORTANT:
    #
    # RawDocument 是 Content Identity。
    #
    # 相同 HTML 可以被不同 URL 的
    # Archive Version 共用。
    #
    # 因此：
    #
    #     RawDocument.original_url
    #
    # 不要求等於：
    #
    #     MongoDB.url
    #
    # 本測試只顯示兩者，
    # 不把 URL mismatch 判定為 FAIL。
    # ==========================================

    print(
        "[OK] URL consistency not enforced "
        "(RawDocument may be shared by hash)"
    )

    print(
        f"       RawDocument URL : {raw_url}"
    )

    print(
        f"       MongoDB URL     : {mongo_url}"
    )

    # ==========================================
    # 4. ArchiveVersion ↔ RawDocument Hash
    # ==========================================

    if raw_hash != version_hash:

        print(
            "[FAIL] RawDocument file_hash does not "
            "match ArchiveVersion file_hash."
        )

        print(
            f"       ArchiveVersion : {version_hash}"
        )

        print(
            f"       RawDocument    : {raw_hash}"
        )

        passed = False

    else:

        print(
            "[OK] ArchiveVersion ↔ RawDocument hash"
        )

    # ==========================================
    # 5. ArchiveVersion ↔ MongoDB Hash
    # ==========================================

    if mongo_hash != version_hash:

        print(
            "[FAIL] MongoDB content_hash does not "
            "match ArchiveVersion file_hash."
        )

        print(
            f"       ArchiveVersion : {version_hash}"
        )

        print(
            f"       MongoDB        : {mongo_hash}"
        )

        passed = False

    else:

        print(
            "[OK] ArchiveVersion ↔ MongoDB hash"
        )

    # ==========================================
    # 6. RawDocument ↔ MongoDB Hash
    # ==========================================

    if raw_hash != mongo_hash:

        print(
            "[FAIL] RawDocument file_hash does not "
            "match MongoDB content_hash."
        )

        print(
            f"       RawDocument : {raw_hash}"
        )

        print(
            f"       MongoDB     : {mongo_hash}"
        )

        passed = False

    else:

        print(
            "[OK] RawDocument ↔ MongoDB hash"
        )

    # ==========================================
    # 7. MongoDB HTML
    # ==========================================

    if mongo_html is None:

        print(
            "[FAIL] MongoDB HTML content missing."
        )

        passed = False

    elif not str(
        mongo_html
    ):

        print(
            "[FAIL] MongoDB HTML content is empty."
        )

        passed = False

    else:

        print(
            "[OK] MongoDB HTML content exists"
        )

    # ==========================================
    # 8. File Size
    #
    # ArchiveVersion / RawDocument / MongoDB
    # 都應該代表相同 HTML Content。
    # ==========================================

    if mongo_html is not None:

        mongo_html_size = len(
            str(
                mongo_html
            ).encode(
                "utf-8"
            )
        )

        # --------------------------------------
        # ArchiveVersion
        # --------------------------------------

        if version_file_size != mongo_html_size:

            print(
                "[FAIL] ArchiveVersion file_size "
                "does not match MongoDB HTML size."
            )

            print(
                f"       ArchiveVersion : "
                f"{version_file_size}"
            )

            print(
                f"       MongoDB HTML   : "
                f"{mongo_html_size}"
            )

            passed = False

        else:

            print(
                "[OK] ArchiveVersion file_size"
            )

        # --------------------------------------
        # RawDocument
        # --------------------------------------

        if raw_file_size != mongo_html_size:

            print(
                "[FAIL] RawDocument file_size "
                "does not match MongoDB HTML size."
            )

            print(
                f"       RawDocument  : "
                f"{raw_file_size}"
            )

            print(
                f"       MongoDB HTML : "
                f"{mongo_html_size}"
            )

            passed = False

        else:

            print(
                "[OK] RawDocument file_size"
            )

        # --------------------------------------
        # ArchiveVersion ↔ RawDocument
        # --------------------------------------

        if version_file_size != raw_file_size:

            print(
                "[FAIL] ArchiveVersion / RawDocument "
                "file_size mismatch."
            )

            print(
                f"       ArchiveVersion : "
                f"{version_file_size}"
            )

            print(
                f"       RawDocument    : "
                f"{raw_file_size}"
            )

            passed = False

        else:

            print(
                "[OK] ArchiveVersion ↔ RawDocument "
                "file_size"
            )

    # ==========================================
    # 9. ArchiveVersion Storage Path
    #
    # IMPORTANT:
    #
    # ArchiveVersion.storage_path
    # 才是本次 Version 的實際 MongoDB
    # Storage Reference。
    #
    # 不要求：
    #
    #     RawDocument.storage_path
    #
    # 與其一致。
    #
    # 因為 RawDocument 可以被不同
    # Archive Version 共用。
    # ==========================================

    archive_mongo_id = extract_mongo_id(
        storage_path
    )

    if not archive_mongo_id:

        print(
            "[FAIL] ArchiveVersion storage_path "
            "does not point to MongoDB raw_html."
        )

        passed = False

    elif archive_mongo_id != mongo_id:

        print(
            "[FAIL] ArchiveVersion MongoDB "
            "reference mismatch."
        )

        print(
            f"       ArchiveVersion : "
            f"{archive_mongo_id}"
        )

        print(
            f"       Loaded MongoDB : "
            f"{mongo_id}"
        )

        passed = False

    else:

        print(
            "[OK] ArchiveVersion → MongoDB relation"
        )

    # ==========================================
    # 10. RawDocument Storage Path
    #
    # IMPORTANT:
    #
    # 不要求：
    #
    #     RawDocument.storage_path
    #         ==
    #     ArchiveVersion.storage_path
    #
    # RawDocument 可能是 shared content record。
    #
    # 因此只檢查：
    #
    #     RawDocument.storage_path
    #
    # 是否為合法 MongoDB reference。
    # ==========================================

    raw_mongo_id = extract_mongo_id(
        raw_storage_path
    )

    if not raw_mongo_id:

        print(
            "[WARN] RawDocument storage_path "
            "does not point to MongoDB raw_html."
        )

    else:

        print(
            "[OK] RawDocument storage_path is "
            "a valid MongoDB reference"
        )

        print(
            f"       RawDocument MongoDB ID : "
            f"{raw_mongo_id}"
        )

    # ==========================================
    # 11. ArchiveVersion → MongoDB Content
    #
    # 這才是本次 Version 的真正
    # Storage Consistency。
    # ==========================================

    if mongo_id:

        print(
            "[OK] ArchiveVersion storage_path "
            "resolves to existing MongoDB document"
        )

    # ==========================================
    # Final Result
    # ==========================================

    print()
    print("=" * 60)

    if not passed:

        print(
            "[FAIL] Archive Storage Consistency "
            "test failed."
        )

        print("=" * 60)

        return

    print(
        "[PASS] Archive Storage Consistency "
        "test passed."
    )

    print("=" * 60)


if __name__ == "__main__":

    main()
