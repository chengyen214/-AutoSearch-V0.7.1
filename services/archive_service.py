"""
services/archive_service.py

AutoSearch V4

P2.2.2 Step 4

Archive Service

功能：

1. 保存 Raw HTML Snapshot 到 MongoDB
2. 建立 Raw HTML MongoDB Document
3. 計算 HTML Content Hash
4. 儲存 Raw Document Metadata 到 MySQL
5. 建立 Archive Version
6. 自動計算 Version Number
7. 偵測相同 URL + 相同 HTML
8. 相同內容不建立新的 Version

Storage Architecture:

    Crawler
        ↓
    ArchiveService
        │
        ├── RawHTMLRepository
        │       ↓
        │   MongoDB
        │       ↓
        │   autosearch.raw_html
        │
        ├── RawDocumentRepository
        │       ↓
        │   MySQL raw_documents
        │
        └── ArchiveVersionRepository
                ↓
            MySQL archive_versions


Duplicate Detection Policy:

    URL
    +
    HTML Content Hash
        ↓
    相同
        ↓
    Duplicate Archive

重要：

    article_id
    不參與 Duplicate Detection。

article_id 只負責：

    1. Archive Version 歸屬
    2. Version Number
    3. Article Version History


Hash Responsibility:

Article document_id
    ↓
utils.hash.generate_hash()

Archive content hash
    ↓
utils.hash.generate_content_hash()

ArchiveService 不自行實作 SHA256。


Flow:

Crawler
    ↓
ArchiveService
    │
    ├── RawHTMLRepository
    │       ↓
    │   MongoDB raw_html
    │
    ├── RawDocumentRepository
    │       ↓
    │   MySQL raw_documents
    │
    └── ArchiveVersionRepository
            ↓
        MySQL archive_versions


Duplicate Detection:

    original_url + file_hash

不考慮：

    article_id


Version History:

Article
    ↓
Version 1
Version 2
Version 3
...
"""

from datetime import datetime


from database.raw_document_repository import (
    RawDocumentRepository
)

from database.archive_version_repository import (
    ArchiveVersionRepository
)

from database.raw_html_repository import (
    RawHTMLRepository
)

from models.raw_document import (
    RawDocument
)

from models.archive_version import (
    ArchiveVersion
)

from utils.hash import (
    generate_content_hash,
    generate_hash,
)

from utils.logger import logger


class ArchiveService:

    # ======================================
    # Initialize
    # ======================================

    def __init__(
        self
    ):

        # ----------------------------------
        # MySQL Raw Document
        # ----------------------------------

        self.raw_repo = (
            RawDocumentRepository()
        )

        # ----------------------------------
        # MySQL Archive Version
        # ----------------------------------

        self.version_repo = (
            ArchiveVersionRepository()
        )

        # ----------------------------------
        # MongoDB Raw HTML
        # ----------------------------------

        self.raw_html_repo = (
            RawHTMLRepository()
        )

    # ======================================
    #
    # Save HTML Snapshot
    #
    # ======================================

    def save_html(
        self,
        article_id,
        url,
        html,
        document_id=None
    ):
        """
        儲存 HTML Archive。

        Raw HTML：

            MongoDB

        Metadata：

            MySQL raw_documents

        Version：

            MySQL archive_versions


        Parameters
        ----------

        article_id :
            MySQL Article ID

        url :
            原始 URL

        html :
            原始 HTML

        document_id :
            Article Document ID

            如果呼叫端沒有提供，
            會使用 Article ID 建立
            相容性 Document ID。


        Duplicate Detection：

            URL
            +
            HTML Hash

        相同：

            → 不建立新的 Version

        不同：

            → 建立新的 Version


        注意：

            article_id 絕對不參與
            Duplicate Detection。

        article_id 僅用於：

            Version 歸屬
            Version Number
            Article Version History
        """

        mongo_document_id = None

        try:

            # ==================================
            # Validate Article
            # ==================================

            if article_id is None:

                logger.error(
                    "Archive requires article_id"
                )

                return None

            # ==================================
            # Validate URL
            # ==================================

            if not url:

                logger.warning(
                    "Archive URL is empty"
                )

                return None

            url = str(
                url
            ).strip()

            if not url:

                logger.warning(
                    "Archive URL is empty after normalization"
                )

                return None

            # ==================================
            # Validate HTML
            # ==================================

            if html is None:

                logger.warning(
                    "Archive HTML is empty"
                )

                return None

            # ==================================
            # Normalize HTML
            # ==================================

            if isinstance(
                html,
                bytes
            ):

                try:

                    html = html.decode(
                        "utf-8"
                    )

                except UnicodeDecodeError as e:

                    logger.error(
                        "Archive HTML UTF-8 decode failed: "
                        f"{e}"
                    )

                    return None

            elif not isinstance(
                html,
                str
            ):

                html = str(
                    html
                )

            if not html:

                logger.warning(
                    "Archive HTML is empty after normalization"
                )

                return None

            # ==================================
            # Resolve Document ID
            # ==================================
            #
            # 正式 Pipeline：
            #
            #     Article.document_id
            #
            # → 直接傳入。
            #
            # Compatibility：
            #
            #     舊版 save_html()
            #     沒有 document_id
            #
            # → 建立穩定 Document ID。
            #
            # 注意：
            #
            # document_id 只負責 MongoDB
            # Raw HTML Document Identity。
            #
            # 不參與：
            #
            #     URL + HTML Hash
            #     Duplicate Detection
            # ==================================

            if document_id:

                document_id = str(
                    document_id
                ).strip()

            if not document_id:

                document_id = (
                    "archive-"
                    +
                    generate_hash(
                        f"{article_id}:{url}"
                    )
                )

                logger.warning(

                    "Archive document_id was not "
                    "provided. Generated compatibility "
                    "document_id: "
                    f"{document_id}"

                )

            # ==================================
            # Generate Content Hash
            # ==================================

            content_hash = (
                generate_content_hash(
                    html
                )
            )

            if not content_hash:

                logger.error(
                    "Failed to generate archive content hash"
                )

                return None

            # ==================================
            # Duplicate Detection
            #
            # 唯一條件：
            #
            #     URL
            #     +
            #     HTML Content Hash
            #
            # NEVER：
            #
            #     article_id
            #
            # 這裡是本次 Archive Request
            # 的唯一正常流程 Duplicate Check。
            #
            # 如果沒有找到：
            #
            #     → 繼續建立 Archive Version
            #
            # 如果找到：
            #
            #     → 直接回傳既有 Version
            #
            # 不在 RawDocument 儲存後再次
            # 執行相同 Check，避免把本次
            # 新增的 Archive 誤判為 Duplicate。
            # ==================================

            existing_version = (
                self._find_existing_version(
                    url=url,
                    file_hash=content_hash
                )
            )

            if existing_version is not None:

                logger.info(

                    "Archive duplicate detected: "

                    f"url={url}, "

                    f"hash={content_hash}, "

                    f"existing_article="
                    f"{existing_version.article_id}, "

                    f"existing_version="
                    f"{existing_version.version_number}"

                )

                return existing_version

            # ==================================
            # Current Time
            # ==================================

            now = datetime.now()

            # ==================================
            # Save Raw HTML to MongoDB
            #
            # HTML 本體正式儲存在：
            #
            #     MongoDB
            #
            # 不再使用：
            #
            #     archive/html
            # ==================================

            try:

                mongo_document_id = (
                    self.raw_html_repo.save(
                        article_id=article_id,
                        document_id=document_id,
                        url=url,
                        html=html, 
                        content_hash=content_hash
                    )
                )

            except Exception as e:

                logger.exception(

                    "Failed to save Raw HTML "
                    "to MongoDB: "
                    f"{e}"

                )

                return None

            if mongo_document_id is None:

                logger.error(
                    "Failed to save Raw HTML to MongoDB"
                )

                return None

            logger.info(

                "Raw HTML MongoDB archive saved: "

                f"article={article_id}, "

                f"document_id={document_id}, "

                f"mongo_id={mongo_document_id}, "

                f"hash={content_hash}"

            )

            # ==================================
            # MongoDB Storage Reference
            #
            # MySQL 不保存 HTML 本體。
            #
            # storage_path：
            #
            #     mongodb://raw_html/<mongo_id>
            #
            # 這是 Storage Reference，
            # 不是本地檔案路徑。
            # ==================================

            storage_path = (
                f"mongodb://raw_html/"
                f"{mongo_document_id}"
            )

            # ==================================
            # File Size
            #
            # HTML 本體現在存在 MongoDB，
            # 沒有本地 archive/html 檔案。
            #
            # 因此使用 UTF-8 Byte Size。
            # ==================================

            file_size = len(
                html.encode(
                    "utf-8"
                )
            )

            # ==================================
            # Raw Document
            #
            # MySQL：
            #
            #     raw_documents
            #
            # 儲存：
            #
            #     Article ID
            #     URL
            #     MongoDB Reference
            #     Content Hash
            #     Size
            #     MIME Type
            #
            # HTML 本體：
            #
            #     MongoDB
            # ==================================

            raw_document = RawDocument(

                article_id=article_id,

                original_url=url,

                storage_path=storage_path,

                file_hash=content_hash,

                file_size=file_size,

                mime_type="text/html",

                created_time=now

            )

            # ==================================
            # Save Raw Document
            # ==================================

            try:

                saved_raw = (
                    self.raw_repo.save(
                        raw_document
                    )
                )

            except Exception as e:

                logger.exception(

                    "Failed to save RawDocument: "
                    f"{e}"

                )

                # ----------------------------------
                # Recovery Lookup
                #
                # ONLY：
                #
                #     URL + Hash
                #
                # 不使用 article_id。
                # ----------------------------------

                saved_raw = None

                try:

                    saved_raw = (
                        self.raw_repo
                        .get_by_url_and_file_hash(
                            url=url,
                            file_hash=content_hash
                        )
                    )

                except Exception as lookup_error:

                    logger.exception(

                        "Failed to lookup existing "
                        "RawDocument: "
                        f"{lookup_error}"

                    )

                if saved_raw is None:

                    return None

                logger.info(

                    "Reuse existing RawDocument: "

                    f"url={url}, "

                    f"hash={content_hash}, "

                    f"raw_document="
                    f"{saved_raw.id}"

                )

            if saved_raw is None:

                logger.error(
                    "Failed to save RawDocument"
                )

                return None

            # ==================================
            # IMPORTANT
            #
            # 不在這裡再次執行：
            #
            #     _find_existing_version()
            #
            # 原因：
            #
            # 本次第一次 Check 已經確認
            # URL + Hash 不存在。
            #
            # 如果這裡再次 Check，
            # Fake Repository / 實際 Repository
            # 都可能已經看到剛剛建立的資料，
            # 導致本次 Version 被誤判成 Duplicate。
            #
            # 正常流程：
            #
            #     Duplicate Check
            #         ↓
            #     MongoDB Raw HTML
            #         ↓
            #     MySQL RawDocument
            #         ↓
            #     Version Number
            #         ↓
            #     Archive Version
            #
            # 只在下一次 save_html()
            # 時進行 Duplicate Detection。
            # ==================================

            # ==================================
            # Get Next Version Number
            #
            # article_id 從這裡開始使用。
            #
            # 用途：
            #
            #     Article Version History
            # ==================================

            version_number = (
                self.version_repo
                .get_next_version_number(
                    article_id
                )
            )

            if version_number is None:

                logger.error(

                    "Failed to get next archive "
                    "version number: "
                    f"article={article_id}"

                )

                return None

            # ==================================
            # Create Archive Version
            # ==================================

            archive_version = ArchiveVersion(

                article_id=article_id,

                raw_document_id=saved_raw.id,

                version_number=version_number,

                file_hash=content_hash,

                storage_path=storage_path,

                file_size=file_size,

                mime_type="text/html",

                created_time=now

            )

            # ==================================
            # Save Archive Version
            # ==================================

            try:

                saved_version = (
                    self.version_repo.save(
                        archive_version
                    )
                )

            except Exception as e:

                logger.exception(

                    "Failed to save ArchiveVersion: "
                    f"{e}"

                )

                return None

            if saved_version is None:

                logger.error(
                    "Failed to save ArchiveVersion"
                )

                return None

            # ==================================
            # Log
            # ==================================

            logger.info(

                "Archive version saved: "

                f"article={article_id}, "

                f"version={version_number}, "

                f"url={url}, "

                f"hash={content_hash}, "

                f"storage=mongodb, "

                f"mongo_id={mongo_document_id}"

            )

            logger.info(

                "Archive completed: "

                f"article={article_id}, "

                f"version={version_number}"

            )

            return saved_version

        except Exception as e:

            logger.exception(
                f"Archive save error: {e}"
            )

            return None

    # ======================================
    #
    # Find Existing Version
    #
    # ======================================

    def _find_existing_version(
        self,
        url,
        file_hash
    ):
        """
        全域 Duplicate Detection。

        唯一判斷條件：

            original_url
            +
            file_hash

        不使用：

            article_id


        Repository 優先使用：

            ArchiveVersionRepository
                ↓
            get_by_url_and_file_hash()


        如果尚未提供，
        則 fallback：

            RawDocumentRepository
                ↓
            get_by_url_and_file_hash()
                ↓
            ArchiveVersionRepository
                ↓
            get_by_raw_document_id()
        """

        try:

            if not url:

                return None

            if not file_hash:

                return None

            url = str(
                url
            ).strip()

            if not url:

                return None

            # ==================================
            # Global URL + Hash Detection
            #
            # 不傳 article_id。
            # ==================================

            if hasattr(
                self.version_repo,
                "get_by_url_and_file_hash"
            ):

                return (
                    self.version_repo
                    .get_by_url_and_file_hash(
                        url=url,
                        file_hash=file_hash
                    )
                )

            # ==================================
            # Compatibility Fallback
            #
            # ArchiveVersionRepository 如果尚未
            # 提供 Global API，
            # 使用 RawDocument Repository。
            # ==================================

            if not hasattr(
                self.raw_repo,
                "get_by_url_and_file_hash"
            ):

                logger.error(

                    "RawDocumentRepository does not "
                    "provide get_by_url_and_file_hash()."

                )

                return None

            raw_document = (
                self.raw_repo
                .get_by_url_and_file_hash(
                    url=url,
                    file_hash=file_hash
                )
            )

            if raw_document is None:

                return None

            raw_document_id = getattr(
                raw_document,
                "id",
                None
            )

            if raw_document_id is None:

                return None

            # ==================================
            # Find Version By RawDocument
            # ==================================

            if hasattr(
                self.version_repo,
                "get_by_raw_document_id"
            ):

                return (
                    self.version_repo
                    .get_by_raw_document_id(
                        raw_document_id
                    )
                )

            if hasattr(
                self.version_repo,
                "find_by_raw_document_id"
            ):

                return (
                    self.version_repo
                    .find_by_raw_document_id(
                        raw_document_id
                    )
                )

            logger.error(

                "ArchiveVersionRepository does not "
                "provide raw document lookup API."

            )

            return None

        except Exception as e:

            logger.exception(

                "Find existing archive version "
                "error: "
                f"{e}"

            )

            return None

    # ======================================
    #
    # Get Article Versions
    #
    # ======================================

    def get_versions(
        self,
        article_id
    ):
        """
        取得 Article 所有 Archive Versions。

        這裡使用 article_id 是正確的。

        因為這是 Version History，
        不是 Duplicate Detection。
        """

        try:

            return (
                self.version_repo
                .get_by_article_id(
                    article_id
                )
            )

        except Exception as e:

            logger.exception(

                "Get archive versions error: "
                f"{e}"

            )

            return []

    # ======================================
    #
    # Get Latest Version
    #
    # ======================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得 Article 最新 Archive Version。

        article_id 在這裡是必要的，
        因為這是 Article Version History。
        """

        try:

            return (
                self.version_repo
                .get_latest_version(
                    article_id
                )
            )

        except Exception as e:

            logger.exception(

                "Get latest archive version error: "
                f"{e}"

            )

            return None


# ======================================
#
# Public API
#
# ======================================

__all__ = [
    "ArchiveService",
]
