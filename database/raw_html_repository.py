"""
database/raw_html_repository.py

AutoSearch V5

Raw HTML Repository

用途：

    使用 MongoDB 儲存 CrawlService
    取得的原始 HTML Snapshot。


V5 Pipeline：

    SearchResult
        |
        v
    CrawlService
        |
        v
    CrawlResult
        |
        v
    RawHTMLRepository
        |
        v
    MongoDB
        |
        v
    ParserService
        |
        v
    Article
        |
        v
    ArchiveService


Crawl 階段：

    尚未建立 Article。

    因此：

        document_id = None

    但已經具有：

        url
        resolved_url
        html
        content_hash
        created_at


Archive Version：

    不使用 Article ID。

    Version Identity：

        URL
        +
        created_at


Archive Web Page：

    URL
        |
        v
    find_versions_by_url()
        |
        v
    歷史版本保存日期列表
        |
        v
    使用者選擇保存日期
        |
        v
    find_html_by_url_and_time()
        |
        v
    MongoDB Raw HTML
        |
        v
    自己的 Archive Web Page


版本列表只需要顯示：

    2026-08-29 14:20
    2026-08-28 14:15
    2026-08-25 09:32


V5 datetime policy：

    所有 created_at / updated_at
    一律使用 timezone-aware UTC datetime。


    Naive datetime：

        視為 UTC


    ISO 8601：

        2026-08-29T14:20:00Z
            ↓
        timezone-aware UTC datetime


    Timezone-aware datetime：

        自動轉換為 UTC。


本 Repository 不負責：

    - Crawler
    - HTTP Download
    - Hash Calculation
    - Parser
    - Article Model
    - MySQL ArticleRepository
    - Archive Duplicate Detection
    - Archive Version Decision
    - AI Analysis
    - Web UI
"""


# ==================================================
#
# Standard Library
#
# ==================================================

from datetime import (
    datetime,
    timezone,
)


# ==================================================
#
# MongoDB
#
# ==================================================

from bson import ObjectId

from pymongo.errors import (
    PyMongoError,
)


# ==================================================
#
# Project
#
# ==================================================

from config.mongo_config import (
    MONGO_RAW_HTML_COLLECTION,
)

from database.mongo_connection import (
    get_mongo_collection,
)

from utils.logger import (
    logger,
)


# ==================================================
#
# Raw HTML Repository
#
# ==================================================

class RawHTMLRepository:
    """
    MongoDB Raw HTML Repository。

    職責：

        CrawlResult
            ↓
        Raw HTML Snapshot
            ↓
        MongoDB


    Archive Viewer 所需的核心查詢：

        URL
            ↓
        歷史保存日期
            ↓
        URL + created_at
            ↓
        指定 Raw HTML


    Repository 不負責：

        - Hash Calculation
        - Duplicate Detection
        - Archive Version Decision
        - Parser
        - Article
        - AI
        - Web UI
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self
    ):

        self.collection = (
            get_mongo_collection(
                MONGO_RAW_HTML_COLLECTION
            )
        )

        self._ensure_indexes()

    # ==================================================
    # Normalize Datetime
    # ==================================================

    @staticmethod
    def _normalize_datetime(
        value
    ):
        """
        將 datetime / ISO 8601
        統一轉換為 timezone-aware UTC datetime。

        支援：

            datetime
            ISO 8601 string
            ISO 8601 + Z
            ISO 8601 + timezone offset


        規則：

            timezone-aware datetime
                ↓
            轉換為 UTC


            naive datetime
                ↓
            視為 UTC


        例如：

            2026-08-29T14:20:00Z
                ↓
            2026-08-29 14:20:00+00:00


            2026-08-29T22:20:00+08:00
                ↓
            2026-08-29 14:20:00+00:00
        """

        if value is None:

            return None

        # --------------------------------------------------
        # String
        # --------------------------------------------------

        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            if not value:

                return None

            try:

                value = datetime.fromisoformat(
                    value.replace(
                        "Z",
                        "+00:00",
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                logger.warning(
                    "Invalid datetime: "
                    f"{value}"
                )

                return None

        # --------------------------------------------------
        # Validate datetime
        # --------------------------------------------------

        if not isinstance(
            value,
            datetime,
        ):

            logger.warning(
                "Unsupported datetime type: "
                f"{type(value)}"
            )

            return None

        # --------------------------------------------------
        # Naive datetime
        #
        # V5：
        #
        # Naive datetime 一律視為 UTC。
        # --------------------------------------------------

        if value.tzinfo is None:

            return value.replace(
                tzinfo=timezone.utc,
            )

        # --------------------------------------------------
        # Timezone-aware datetime
        #
        # Normalize to UTC.
        # --------------------------------------------------

        return value.astimezone(
            timezone.utc,
        )

    # ==================================================
    # Ensure Indexes
    # ==================================================

    def _ensure_indexes(
        self
    ):
        """
        建立 Raw HTML Lookup Index。

        Index：

            document_id
            url
            resolved_url
            content_hash

            url + content_hash

            url + created_at

        注意：

            所有 Index 都不是 Unique。

            Duplicate Detection
            仍由 ArchiveService 負責。


        Archive Viewer：

            主要使用：

                url + created_at
        """

        try:

            # ------------------------------------------
            # Document ID
            # ------------------------------------------

            self.collection.create_index(
                "document_id"
            )

            # ------------------------------------------
            # URL
            # ------------------------------------------

            self.collection.create_index(
                "url"
            )

            # ------------------------------------------
            # Resolved URL
            # ------------------------------------------

            self.collection.create_index(
                "resolved_url"
            )

            # ------------------------------------------
            # Content Hash
            # ------------------------------------------

            self.collection.create_index(
                "content_hash"
            )

            # ------------------------------------------
            # URL + Content Hash
            #
            # Duplicate Lookup
            #
            # 由 ArchiveService 使用。
            # ------------------------------------------

            self.collection.create_index(
                [
                    ("url", 1),
                    ("content_hash", 1),
                ]
            )

            # ------------------------------------------
            # URL + Created At
            #
            # Archive Version Lookup
            #
            # 用於：
            #
            #     URL
            #       ↓
            #     歷史保存日期
            #
            #     URL + created_at
            #       ↓
            #     指定 HTML Snapshot
            # ------------------------------------------

            self.collection.create_index(
                [
                    ("url", 1),
                    ("created_at", -1),
                ]
            )

            logger.info(
                "Raw HTML MongoDB indexes initialized."
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML index initialization failed: "
                f"{e}"
            )

            raise

    # ==================================================
    # Save
    # ==================================================

    def save(
        self,
        url=None,
        html=None,
        content_hash=None,
        resolved_url=None,
        document_id=None,
    ):
        """
        儲存 Raw HTML Snapshot。

        Crawl 階段最小需求：

            url
            html
            content_hash


        可選 metadata：

            resolved_url
            document_id


        Archive Version：

            不依賴 Article ID。

            保存時間：

                created_at


        本方法不負責：

            Hash Calculation
            Duplicate Detection
            Archive Version Decision
        """

        # ==================================================
        # Validate URL
        # ==================================================

        if url is None:

            logger.error(
                "Raw HTML save failed: "
                "url is None"
            )

            return None

        url = str(
            url
        ).strip()

        if not url:

            logger.error(
                "Raw HTML save failed: "
                "url is empty"
            )

            return None

        # ==================================================
        # Validate HTML
        # ==================================================

        if html is None:

            logger.error(
                "Raw HTML save failed: "
                "html is None"
            )

            return None

        html = str(
            html
        )

        if not html:

            logger.error(
                "Raw HTML save failed: "
                "html is empty"
            )

            return None

        # ==================================================
        # Validate Content Hash
        # ==================================================

        if content_hash is None:

            logger.error(
                "Raw HTML save failed: "
                "content_hash is None"
            )

            return None

        content_hash = str(
            content_hash
        ).strip()

        if not content_hash:

            logger.error(
                "Raw HTML save failed: "
                "content_hash is empty"
            )

            return None

        # ==================================================
        # Normalize Resolved URL
        # ==================================================

        if resolved_url is not None:

            resolved_url = str(
                resolved_url
            ).strip()

            if not resolved_url:

                resolved_url = None

        # ==================================================
        # Normalize Document ID
        # ==================================================

        if document_id is not None:

            document_id = str(
                document_id
            ).strip()

            if not document_id:

                document_id = None

        # ==================================================
        # Current UTC Time
        # ==================================================

        now = datetime.now(
            timezone.utc,
        )

        # ==================================================
        # MongoDB Document
        # ==================================================

        document = {

            "document_id":
                document_id,

            "url":
                url,

            "resolved_url":
                resolved_url,

            "html":
                html,

            "content_hash":
                content_hash,

            "created_at":
                now,

            "updated_at":
                now,

        }

        # ==================================================
        # Insert
        # ==================================================

        try:

            result = (
                self.collection.insert_one(
                    document
                )
            )

            mongo_id = str(
                result.inserted_id
            )

            logger.info(
                "Raw HTML saved to MongoDB: "
                f"mongo_id={mongo_id}, "
                f"url={url}, "
                f"resolved_url={resolved_url}, "
                f"document_id={document_id}, "
                f"content_hash={content_hash}, "
                f"created_at={now}"
            )

            return mongo_id

        except PyMongoError as e:

            logger.exception(
                "Raw HTML save failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Save Crawl Result
    # ==================================================

    def save_crawl_result(
        self,
        crawl_result
    ):
        """
        將 CrawlService.CrawlResult
        直接保存到 MongoDB。

        CrawlResult：

            url
            resolved_url
            html
            content_hash


        Crawl 階段：

            不需要 Article ID。


        Returns：

            MongoDB ObjectId string
        """

        if crawl_result is None:

            logger.error(
                "save_crawl_result failed: "
                "crawl_result is None"
            )

            return None

        # ==================================================
        # Crawl Success Validation
        # ==================================================

        success = getattr(
            crawl_result,
            "success",
            False
        )

        if not success:

            logger.warning(
                "save_crawl_result skipped: "
                "crawl_result is not successful"
            )

            return None

        # ==================================================
        # Extract CrawlResult
        # ==================================================

        url = getattr(
            crawl_result,
            "url",
            None
        )

        resolved_url = getattr(
            crawl_result,
            "resolved_url",
            None
        )

        html = getattr(
            crawl_result,
            "html",
            None
        )

        content_hash = getattr(
            crawl_result,
            "content_hash",
            None
        )

        # ==================================================
        # Save
        # ==================================================

        return self.save(

            url=url,

            resolved_url=resolved_url,

            html=html,

            content_hash=content_hash,

        )

    # ==================================================
    # Find By MongoDB ID
    # ==================================================

    def find_by_id(
        self,
        mongo_id
    ):
        """
        依 MongoDB ObjectId
        查詢 Raw HTML Snapshot。
        """

        if not mongo_id:

            return None

        try:

            object_id = ObjectId(
                str(
                    mongo_id
                )
            )

        except Exception:

            logger.warning(
                "Invalid MongoDB ObjectId: "
                f"{mongo_id}"
            )

            return None

        try:

            return (
                self.collection.find_one(
                    {
                        "_id":
                            object_id
                    }
                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_by_id failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find By Document ID
    # ==================================================

    def find_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID
        查詢最新 Raw HTML Snapshot。
        """

        if not document_id:

            return None

        document_id = str(
            document_id
        ).strip()

        if not document_id:

            return None

        try:

            return (
                self.collection.find_one(

                    {
                        "document_id":
                            document_id
                    },

                    sort=[
                        (
                            "created_at",
                            -1
                        )
                    ]

                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_by_document_id failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find By URL
    # ==================================================

    def find_by_url(
        self,
        url
    ):
        """
        依原始 URL
        查詢最新 Raw HTML Snapshot。

        用途：

            Archive Viewer 預設顯示最新版本。
        """

        if not url:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        try:

            return (
                self.collection.find_one(

                    {
                        "url":
                            url
                    },

                    sort=[
                        (
                            "created_at",
                            -1
                        )
                    ]

                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_by_url failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find Versions By URL
    # ==================================================

    def find_versions_by_url(
        self,
        url
    ):
        """
        取得指定 URL 的所有 Raw HTML Snapshot
        歷史保存版本。

        Archive Version 對使用者而言：

            只顯示保存成功日期。


        回傳：

            mongo_id
            created_at


        content_hash：

            保留給內部使用。

            不需要顯示在 Archive UI。


        不回傳：

            html


        最新保存版本在前。
        """

        if not url:

            return []

        url = str(
            url
        ).strip()

        if not url:

            return []

        try:

            cursor = (
                self.collection.find(

                    {
                        "url":
                            url
                    },

                    {
                        "_id": 1,
                        "created_at": 1
                    }

                )
                .sort(
                    "created_at",
                    -1
                )
            )

            versions = []

            for document in cursor:

                created_at = (
                    document.get(
                        "created_at"
                    )
                )

                normalized_created_at = (
                    self._normalize_datetime(
                        created_at
                    )
                )

                if normalized_created_at is None:

                    continue

                versions.append({

                    "mongo_id":
                        str(
                            document["_id"]
                        ),

                    "created_at":
                        normalized_created_at,

                })

            logger.info(
                "Raw HTML versions found by URL: "
                f"url={url}, "
                f"count={len(versions)}"
            )

            return versions

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_versions_by_url failed: "
                f"{e}"
            )

            return []

    # ==================================================
    # Find By URL + Time
    # ==================================================

    def find_by_url_and_time(
        self,
        url,
        created_at
    ):
        """
        依：

            URL
            +
            created_at

        查詢指定 Raw HTML Snapshot。

        Archive Version Identity：

            URL
            +
            created_at


        V5 datetime policy：

            created_at 必須先統一成
            timezone-aware UTC datetime。


        用途：

            使用者在 Archive Web Page
            點擊某個歷史保存日期：

                URL + created_at
                    ↓
                MongoDB
                    ↓
                指定 Snapshot
        """

        if not url:

            return None

        if created_at is None:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        # ==================================================
        # Normalize Created At
        # ==================================================

        created_at = (
            self._normalize_datetime(
                created_at
            )
        )

        if created_at is None:

            return None

        # ==================================================
        # MongoDB Lookup
        # ==================================================

        try:

            return (
                self.collection.find_one(

                    {
                        "url":
                            url,

                        "created_at":
                            created_at
                    }

                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_by_url_and_time failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find HTML By URL + Time
    # ==================================================

    def find_html_by_url_and_time(
        self,
        url,
        created_at
    ):
        """
        依：

            URL
            +
            created_at

        取得指定歷史保存版本的 Raw HTML。

        只回傳 HTML。

        用途：

            Archive Article Page
                ↓
            使用者選擇歷史保存日期
                ↓
            URL + created_at
                ↓
            MongoDB
                ↓
            HTML
                ↓
            Web Page
        """

        document = (
            self.find_by_url_and_time(
                url,
                created_at
            )
        )

        if document is None:

            return None

        return document.get(
            "html"
        )

    # ==================================================
    # Find By Resolved URL
    # ==================================================

    def find_by_resolved_url(
        self,
        resolved_url
    ):
        """
        依 Redirect 後 URL
        查詢最新 Raw HTML Snapshot。
        """

        if not resolved_url:

            return None

        resolved_url = str(
            resolved_url
        ).strip()

        if not resolved_url:

            return None

        try:

            return (
                self.collection.find_one(

                    {
                        "resolved_url":
                            resolved_url
                    },

                    sort=[
                        (
                            "created_at",
                            -1
                        )
                    ]

                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_by_resolved_url failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find By Content Hash
    # ==================================================

    def find_by_content_hash(
        self,
        content_hash
    ):
        """
        依 Raw HTML Content Hash 查詢。

        僅提供 Lookup。

        不代表 Duplicate。
        """

        if not content_hash:

            return None

        content_hash = str(
            content_hash
        ).strip()

        if not content_hash:

            return None

        try:

            return (
                self.collection.find_one(

                    {
                        "content_hash":
                            content_hash
                    },

                    sort=[
                        (
                            "created_at",
                            -1
                        )
                    ]

                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_by_content_hash failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find By URL + Content Hash
    # ==================================================

    def find_by_url_and_content_hash(
        self,
        url,
        content_hash
    ):
        """
        查詢：

            URL
            +
            Content Hash

        僅提供 Lookup。

        Duplicate Decision：

            ArchiveService
        """

        if not url:

            return None

        if not content_hash:

            return None

        url = str(
            url
        ).strip()

        content_hash = str(
            content_hash
        ).strip()

        if not url or not content_hash:

            return None

        try:

            return (
                self.collection.find_one(
                    {
                        "url":
                            url,

                        "content_hash":
                            content_hash
                    }
                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML find_by_url_and_content_hash "
                "failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Exists By Document ID
    # ==================================================

    def exists(
        self,
        document_id
    ):
        """
        檢查 Document ID 是否存在。

        僅 Entity Lookup。
        """

        if not document_id:

            return False

        document_id = str(
            document_id
        ).strip()

        if not document_id:

            return False

        try:

            result = (
                self.collection.find_one(

                    {
                        "document_id":
                            document_id
                    },

                    {
                        "_id": 1
                    }

                )
            )

            return result is not None

        except PyMongoError as e:

            logger.exception(
                "Raw HTML exists check failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Exists By URL + Content Hash
    # ==================================================

    def exists_by_url_and_content_hash(
        self,
        url,
        content_hash
    ):
        """
        檢查 URL + Content Hash 是否存在。

        注意：

            只提供 Lookup。

            不代表 Duplicate。

            Duplicate Decision：

                ArchiveService
        """

        if not url:

            return False

        if not content_hash:

            return False

        url = str(
            url
        ).strip()

        content_hash = str(
            content_hash
        ).strip()

        if not url or not content_hash:

            return False

        try:

            result = (
                self.collection.find_one(

                    {
                        "url":
                            url,

                        "content_hash":
                            content_hash
                    },

                    {
                        "_id": 1
                    }

                )
            )

            return result is not None

        except PyMongoError as e:

            logger.exception(
                "Raw HTML URL + Content Hash "
                "existence check failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Update Metadata
    # ==================================================

    def update_metadata(
        self,
        mongo_id,
        document_id=None
    ):
        """
        Crawl / Parser 完成後：

            MongoDB Raw HTML
                    ↓
            Article 建立
                    ↓
            補回 Document Identity


        更新：

            document_id


        不更新：

            url
            resolved_url
            html
            content_hash
            created_at


        updated_at：

            使用 UTC datetime。


        注意：

            不再處理 article_id。

            Archive Version
            不依賴 Article ID。
        """

        if not mongo_id:

            return False

        # ==================================================
        # Normalize Document ID
        # ==================================================

        if document_id is None:

            return False

        document_id = str(
            document_id
        ).strip()

        if not document_id:

            return False

        update_data = {

            "document_id":
                document_id,

            "updated_at":
                datetime.now(
                    timezone.utc
                ),

        }

        # ==================================================
        # MongoDB Update
        # ==================================================

        try:

            object_id = ObjectId(
                str(
                    mongo_id
                )
            )

            result = (
                self.collection.update_one(

                    {
                        "_id":
                            object_id
                    },

                    {
                        "$set":
                            update_data
                    }

                )
            )

            if result.matched_count == 0:

                logger.warning(
                    "Raw HTML metadata update failed: "
                    f"mongo_id={mongo_id}"
                )

                return False

            logger.info(
                "Raw HTML metadata updated: "
                f"mongo_id={mongo_id}, "
                f"document_id={document_id}"
            )

            return True

        except Exception as e:

            logger.exception(
                "Raw HTML metadata update failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Update HTML By MongoDB ID
    # ==================================================

    def update_html_by_id(
        self,
        mongo_id,
        html,
        content_hash
    ):
        """
        依 MongoDB Snapshot ID
        更新 Raw HTML。

        注意：

            content_hash 必須由上游產生。

            Repository 不自行計算 Hash。

        Archive Version：

            由 ArchiveService 管理。


        updated_at：

            使用 UTC datetime。
        """

        if not mongo_id:

            return False

        if html is None:

            return False

        if content_hash is None:

            return False

        html = str(
            html
        )

        content_hash = str(
            content_hash
        ).strip()

        if not html or not content_hash:

            return False

        try:

            object_id = ObjectId(
                str(
                    mongo_id
                )
            )

            result = (
                self.collection.update_one(

                    {
                        "_id":
                            object_id
                    },

                    {
                        "$set": {

                            "html":
                                html,

                            "content_hash":
                                content_hash,

                            "updated_at":
                                datetime.now(
                                    timezone.utc
                                ),

                        }
                    }

                )
            )

            if result.matched_count == 0:

                logger.warning(
                    "Raw HTML update failed: "
                    f"mongo_id={mongo_id}"
                )

                return False

            logger.info(
                "Raw HTML updated: "
                f"mongo_id={mongo_id}, "
                f"content_hash={content_hash}"
            )

            return True

        except Exception as e:

            logger.exception(
                "Raw HTML update failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Delete By MongoDB ID
    # ==================================================

    def delete_by_id(
        self,
        mongo_id
    ):
        """
        依 MongoDB ObjectId
        刪除 Raw HTML Snapshot。
        """

        if not mongo_id:

            return False

        try:

            object_id = ObjectId(
                str(
                    mongo_id
                )
            )

            result = (
                self.collection.delete_one(
                    {
                        "_id":
                            object_id
                    }
                )
            )

            if result.deleted_count == 0:

                return False

            logger.info(
                "Raw HTML deleted: "
                f"mongo_id={mongo_id}"
            )

            return True

        except Exception as e:

            logger.exception(
                "Raw HTML delete_by_id failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Delete By Document ID
    # ==================================================

    def delete_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID
        刪除所有相關 Raw HTML Snapshot。
        """

        if not document_id:

            return False

        document_id = str(
            document_id
        ).strip()

        if not document_id:

            return False

        try:

            result = (
                self.collection.delete_many(

                    {
                        "document_id":
                            document_id
                    }

                )
            )

            if result.deleted_count == 0:

                return False

            logger.info(
                "Raw HTML deleted: "
                f"document_id={document_id}, "
                f"deleted={result.deleted_count}"
            )

            return True

        except PyMongoError as e:

            logger.exception(
                "Raw HTML delete_by_document_id failed: "
                f"{e}"
            )

            return False

    # ==================================================
    # Count
    # ==================================================

    def count(
        self
    ):
        """
        取得 Raw HTML Snapshot 數量。
        """

        try:

            return (
                self.collection.count_documents(
                    {}
                )
            )

        except PyMongoError as e:

            logger.exception(
                "Raw HTML count failed: "
                f"{e}"
            )

            return 0


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "RawHTMLRepository",
]