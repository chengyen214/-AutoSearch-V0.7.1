"""
services/archive_service.py

AutoSearch V4

P2.2.2 Step 4

Archive Service

功能:

1. 保存 Raw HTML Snapshot
2. 建立 Archive Path
3. 計算實際檔案 File Hash
4. 儲存 Raw Document Metadata
5. 建立 Archive Version
6. 自動計算 Version Number
7. 偵測相同 URL + 相同 HTML
8. 相同內容不建立新的 Version

Flow:

Crawler
↓
ArchiveService
├── RawDocumentRepository
│       ↓
│   raw_documents
│
└── ArchiveVersionRepository
        ↓
    archive_versions

Version History:

Article
↓
Version 1
Version 2
Version 3
...
"""

import os
import hashlib

from datetime import datetime

from database.raw_document_repository import (
    RawDocumentRepository
)

from database.archive_version_repository import (
    ArchiveVersionRepository
)

from models.raw_document import (
    RawDocument
)

from models.archive_version import (
    ArchiveVersion
)

from utils.logger import logger


class ArchiveService:

    # ======================================
    # Initialize
    # ======================================

    def __init__(self):

        # ==================================
        # Repository
        # ==================================

        self.raw_repo = (
            RawDocumentRepository()
        )

        self.version_repo = (
            ArchiveVersionRepository()
        )

        # ==================================
        # Archive Root
        # ==================================

        self.archive_root = os.path.join(
            "archive",
            "html"
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
        html
    ):
        """
        儲存 HTML Archive。

        Change Detection:

            相同 Article
            +
            相同 URL
            +
            相同 HTML

        → 不建立新的 Version。

        不同 HTML:

            Version 1
            Version 2
            Version 3
            ...

        """

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

            # ==================================
            # Validate HTML
            # ==================================

            if not html:

                logger.warning(
                    "Archive HTML is empty"
                )

                return None

            # ==================================
            # Normalize URL
            #
            # 目前採 exact URL 比對。
            #
            # 只移除前後空白，
            # 不改變 URL 本身。
            # ==================================

            url = str(
                url
            ).strip()

            # ==================================
            # Calculate Content Hash
            #
            # HTML UTF-8 bytes 的 SHA256。
            #
            # 用來判斷內容是否變化。
            # ==================================

            content_hash = (
                self.generate_hash(
                    html
                )
            )

            # ==================================
            # Change Detection
            #
            # 相同：
            #
            # article_id
            # +
            # URL
            # +
            # file_hash
            #
            # → 不建立新的 Version
            # ==================================

            existing_version = (
                self._find_existing_version(
                    article_id=article_id,
                    url=url,
                    file_hash=content_hash
                )
            )

            if existing_version is not None:

                logger.info(

                    "Archive content unchanged: "

                    f"article={article_id}, "

                    f"url={url}, "

                    f"hash={content_hash}, "

                    f"version="
                    f"{existing_version.version_number}"

                )

                return existing_version

            # ==================================
            # Current Time
            # ==================================

            now = datetime.now()

            # ==================================
            # Archive Folder
            # ==================================

            folder = os.path.join(

                self.archive_root,

                str(now.year),

                f"{now.month:02d}",

                f"{now.day:02d}"

            )

            os.makedirs(

                folder,

                exist_ok=True

            )

            # ==================================
            # Temporary File
            #
            # 先寫入實際 HTML。
            # ==================================

            temp_filename = (
                "temp_archive.html"
            )

            temp_path = os.path.join(

                folder,

                temp_filename

            )

            with open(

                temp_path,

                "w",

                encoding="utf-8",

                newline=""

            ) as f:

                f.write(html)

            # ==================================
            # Calculate Hash From Actual File
            #
            # 最終 Archive File 使用
            # 實際落盤 bytes 的 SHA256。
            # ==================================

            file_hash = (
                self.generate_file_hash(
                    temp_path
                )
            )

            # ==================================
            # File Name
            # ==================================

            filename = (
                f"{file_hash}.html"
            )

            storage_path = os.path.join(

                folder,

                filename

            )

            # ==================================
            # Avoid Duplicate File Conflict
            # ==================================

            if os.path.exists(
                storage_path
            ):

                os.remove(
                    temp_path
                )

            else:

                os.replace(

                    temp_path,

                    storage_path

                )

            # ==================================
            # File Size
            # ==================================

            file_size = os.path.getsize(
                storage_path
            )

            # ==================================
            # Normalize DB Path
            #
            # Database 統一使用 /
            # ==================================

            db_storage_path = os.path.join(

                self.archive_root,

                str(now.year),

                f"{now.month:02d}",

                f"{now.day:02d}",

                filename

            ).replace(
                os.sep,
                "/"
            )

            # ==================================
            # Verify Actual File Hash
            # ==================================

            actual_hash = (
                self.generate_file_hash(
                    storage_path
                )
            )

            if actual_hash != file_hash:

                logger.error(

                    "Archive hash verification failed: "

                    f"expected={file_hash}, "

                    f"actual={actual_hash}"

                )

                # 避免留下錯誤 Archive File

                try:

                    if os.path.exists(
                        storage_path
                    ):

                        os.remove(
                            storage_path
                        )

                except Exception:

                    pass

                return None

            # ==================================
            # Important:
            #
            # file_hash 應與 content_hash 相同。
            #
            # 如果不同，代表實際落盤內容
            # 與原始 HTML 不一致。
            # ==================================

            if file_hash != content_hash:

                logger.error(

                    "Archive content hash mismatch: "

                    f"content_hash={content_hash}, "

                    f"file_hash={file_hash}"

                )

                try:

                    if os.path.exists(
                        storage_path
                    ):

                        os.remove(
                            storage_path
                        )

                except Exception:

                    pass

                return None

            # ==================================
            # Raw Document
            # ==================================

            raw_document = RawDocument(

                article_id=article_id,

                original_url=url,

                storage_path=db_storage_path,

                file_hash=file_hash,

                file_size=file_size,

                mime_type="text/html",

                created_time=now

            )

            # ==================================
            # Save Raw Document
            # ==================================

            saved_raw = None

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
                # 如果 Database 已存在相同 Hash，
                # 嘗試取得既有 RawDocument。
                # ----------------------------------

                try:

                    existing_raw = (
                        self.raw_repo
                        .get_by_file_hash(
                            file_hash
                        )
                    )

                except Exception:

                    existing_raw = None

                if existing_raw is None:

                    return None

                saved_raw = existing_raw

                logger.info(

                    "Reuse existing RawDocument: "

                    f"hash={file_hash}, "

                    f"raw_document="
                    f"{existing_raw.id}"

                )

            if saved_raw is None:

                logger.error(
                    "Failed to save RawDocument"
                )

                return None

            # ==================================
            # Important:
            #
            # RawDocument 可能因為相同 Hash
            # 被 Repository 重用。
            #
            # 此時再次確認：
            #
            # Article + URL + Hash
            #
            # 是否已經存在 Version。
            # ==================================

            existing_version = (
                self._find_existing_version(
                    article_id=article_id,
                    url=url,
                    file_hash=file_hash
                )
            )

            if existing_version is not None:

                logger.info(

                    "Archive version already exists "
                    "after RawDocument lookup: "

                    f"article={article_id}, "

                    f"url={url}, "

                    f"hash={file_hash}, "

                    f"version="
                    f"{existing_version.version_number}"

                )

                return existing_version

            # ==================================
            # Get Next Version Number
            # ==================================

            version_number = (

                self.version_repo
                .get_next_version_number(
                    article_id
                )

            )

            # ==================================
            # Create Archive Version
            # ==================================

            archive_version = ArchiveVersion(

                article_id=article_id,

                raw_document_id=saved_raw.id,

                version_number=version_number,

                file_hash=file_hash,

                storage_path=db_storage_path,

                file_size=file_size,

                mime_type="text/html",

                created_time=now

            )

            # ==================================
            # Save Archive Version
            # ==================================

            saved_version = (

                self.version_repo.save(
                    archive_version
                )

            )

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

                f"hash={file_hash}, "

                f"path={db_storage_path}"

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
        article_id,
        url,
        file_hash
    ):
        """
        查詢是否已存在：

            Article
            +
            URL
            +
            File Hash

        相同代表：

            相同文章
            +
            相同網址
            +
            相同內容

        因此不需要建立新的 Version。
        """

        try:

            # ==================================
            # Preferred Repository API
            # ==================================

            if hasattr(
                self.version_repo,
                "get_by_article_url_hash"
            ):

                return (
                    self.version_repo
                    .get_by_article_url_hash(
                        article_id=article_id,
                        url=url,
                        file_hash=file_hash
                    )
                )

            # ==================================
            # Compatibility Fallback
            #
            # 如果 Repository 尚未提供
            # get_by_article_url_hash，
            # 使用 Version History + RawDocument
            # 做 fallback。
            # ==================================

            versions = (
                self.version_repo
                .get_by_article_id(
                    article_id
                )
            )

            if not versions:

                return None

            for version in versions:

                version_hash = getattr(
                    version,
                    "file_hash",
                    None
                )

                if version_hash != file_hash:

                    continue

                # ----------------------------------
                # 確認 RawDocument URL
                # ----------------------------------

                raw_document = None

                raw_document_id = getattr(
                    version,
                    "raw_document_id",
                    None
                )

                if raw_document_id is not None:

                    if hasattr(
                        self.raw_repo,
                        "get_by_id"
                    ):

                        raw_document = (
                            self.raw_repo
                            .get_by_id(
                                raw_document_id
                            )
                        )

                # ----------------------------------
                # 如果 Repository 沒有 get_by_id，
                # 使用 file_hash 查詢。
                # ----------------------------------

                if raw_document is None:

                    if hasattr(
                        self.raw_repo,
                        "get_by_file_hash"
                    ):

                        raw_document = (
                            self.raw_repo
                            .get_by_file_hash(
                                file_hash
                            )
                        )

                if raw_document is None:

                    continue

                raw_url = getattr(
                    raw_document,
                    "original_url",
                    None
                )

                if raw_url == url:

                    return version

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
    # Generate Hash From File
    #
    # ======================================

    def generate_file_hash(
        self,
        file_path
    ):

        sha256 = hashlib.sha256()

        with open(
            file_path,
            "rb"
        ) as f:

            for chunk in iter(
                lambda: f.read(
                    1024 * 1024
                ),
                b""
            ):

                sha256.update(
                    chunk
                )

        return sha256.hexdigest()

    # ======================================
    #
    # Generate Hash From Content
    #
    # ======================================

    def generate_hash(
        self,
        content
    ):
        """
        計算 HTML UTF-8 Content SHA256。
        """

        if content is None:

            return None

        if not isinstance(
            content,
            str
        ):

            content = str(
                content
            )

        return hashlib.sha256(

            content.encode(
                "utf-8"
            )

        ).hexdigest()
