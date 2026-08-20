"""
database/raw_html_repository.py

AutoSearch V4

Raw HTML Repository

用途：

    使用 MongoDB 儲存 Article 原始 HTML。

架構：

    Article
        |
        v
    ArchiveService
        |
        v
    RawHTMLRepository
        |
        v
    MongoDB
        |
        v
    autosearch.raw_html


功能：

    - Raw HTML Create
    - Raw HTML Query
    - Raw HTML Update
    - Raw HTML Delete
    - Article ID Query
    - Document ID Query
    - URL Query
    - Content Hash Query
    - Count


MongoDB Document：

    {
        "_id": ObjectId,

        "article_id": int,

        "document_id": str,

        "url": str,

        "html": str,

        "content_hash": str,

        "created_at": datetime,

        "updated_at": datetime
    }


重要設計：

    RawHTMLRepository 不負責 Archive Duplicate Detection。


    Archive Duplicate Detection 唯一由：

        ArchiveService

    負責。


Duplicate Detection Policy：

    URL
    +
    HTML Content Hash
        ↓
    ArchiveService
        ↓
    Duplicate / New Version


因此：

    RawHTMLRepository.save()

    不會再使用：

        document_id

    判斷 HTML 是否重複。


document_id 用途：

    Article Document Identity

    主要用於：

        1. MongoDB Raw HTML Document Identity
        2. Article Document Query
        3. Article / Raw HTML 關聯


content_hash 用途：

    Raw HTML Content Identity

    主要由：

        ArchiveService
            ↓
        generate_content_hash(html)

    產生。


重要：

    document_id

    與

    content_hash

    是不同用途的識別資訊。


本 Repository 不負責：

    - Crawler
    - Article Model
    - MySQL ArticleRepository
    - HTML Parser
    - Archive Duplicate Detection
    - Archive Version
    - Hash Calculation
    - AI Analysis
"""


from datetime import datetime


from pymongo.errors import (
    PyMongoError
)


from config.mongo_config import (
    MONGO_RAW_HTML_COLLECTION
)


from database.mongo_connection import (
    get_mongo_collection
)


from utils.logger import (
    logger
)


class RawHTMLRepository:
    """
    MongoDB Raw HTML Repository。

    職責：

        將 ArchiveService 傳入的
        Raw HTML Snapshot 寫入 MongoDB。

    不負責：

        Archive Duplicate Detection。
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
    # Ensure Indexes
    # ==================================================

    def _ensure_indexes(
        self
    ):
        """
        建立 Raw HTML 查詢所需 Index。

        Index：

            article_id
            document_id
            url
            content_hash


        注意：

            document_id 不再設為 unique。

            原因：

                document_id
                =
                Article Document Identity

            content_hash
                =
                Raw HTML Content Identity

            Archive Duplicate Detection：

                URL + content_hash

            由 ArchiveService 負責。
        """

        try:

            self.collection.create_index(
                "article_id"
            )

            self.collection.create_index(
                "document_id"
            )

            self.collection.create_index(
                "url"
            )

            self.collection.create_index(
                "content_hash"
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
        article_id,
        document_id,
        url,
        html,
        content_hash=None
    ):
        """
        儲存原始 HTML Snapshot。

        Parameters
        ----------

        article_id :
            MySQL articles.id

        document_id :
            Article Document ID

        url :
            原始網頁 URL

        html :
            原始 HTML 內容

        content_hash :
            Raw HTML Content Hash

            由 ArchiveService 使用：

                generate_content_hash(html)

            產生。

        Returns
        -------

        str
            MongoDB Document ID

        None
            儲存失敗


        Important
        ---------

        本方法不執行 Duplicate Detection。

        Duplicate Detection 唯一由：

            ArchiveService

        根據：

            URL + content_hash

        判斷。
        """

        # ==========================================
        # Validate Article ID
        # ==========================================

        if article_id is None:

            logger.error(
                "Raw HTML save failed: "
                "article_id is None"
            )

            return None

        # ==========================================
        # Validate Document ID
        # ==========================================

        if not document_id:

            logger.error(
                "Raw HTML save failed: "
                "document_id is empty"
            )

            return None

        # ==========================================
        # Validate URL
        # ==========================================

        if not url:

            logger.error(
                "Raw HTML save failed: "
                "url is empty"
            )

            return None

        # ==========================================
        # Validate HTML
        # ==========================================

        if html is None:

            logger.error(
                "Raw HTML save failed: "
                "html is None"
            )

            return None

        # ==========================================
        # Normalize
        # ==========================================

        document_id = str(
            document_id
        ).strip()

        url = str(
            url
        ).strip()

        html = str(
            html
        )

        if not document_id:

            logger.error(
                "Raw HTML save failed: "
                "document_id is empty after normalization"
            )

            return None

        if not url:

            logger.error(
                "Raw HTML save failed: "
                "url is empty after normalization"
            )

            return None

        if not html:

            logger.error(
                "Raw HTML save failed: "
                "html is empty after normalization"
            )

            return None

        # ==========================================
        # Normalize Content Hash
        # ==========================================

        if content_hash is not None:

            content_hash = str(
                content_hash
            ).strip()

            if not content_hash:

                content_hash = None

        # ==========================================
        # Current Time
        # ==========================================

        now = datetime.now()

        # ==========================================
        # MongoDB Document
        # ==========================================

        document = {

            "article_id": article_id,

            "document_id": document_id,

            "url": url,

            "html": html,

            "content_hash": content_hash,

            "created_at": now,

            "updated_at": now

        }

        try:

            # ======================================
            # IMPORTANT
            #
            # 不在 Repository 執行：
            #
            #     document_id Duplicate Detection
            #
            # 不執行：
            #
            #     find_one(
            #         {"document_id": document_id}
            #     )
            #
            # 原因：
            #
            # Archive Duplicate Detection
            # 已由 ArchiveService 負責。
            #
            # 唯一條件：
            #
            #     URL + HTML Content Hash
            #
            # ======================================

            # ======================================
            # Insert
            # ======================================

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
                f"article_id={article_id}, "
                f"document_id={document_id}, "
                f"mongo_id={mongo_id}, "
                f"url={url}, "
                f"content_hash={content_hash}"
            )

            return mongo_id

        except PyMongoError as e:

            logger.exception(
                "Raw HTML save failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find By MongoDB ID
    # ==================================================

    def find_by_id(
        self,
        mongo_id
    ):
        """
        依 MongoDB ObjectId 查詢 Raw HTML。
        """

        if not mongo_id:

            return None

        try:

            from bson import ObjectId

            result = (
                self.collection.find_one(
                    {
                        "_id":
                            ObjectId(
                                mongo_id
                            )
                    }
                )
            )

            return result

        except Exception as e:

            logger.warning(
                "Raw HTML find_by_id failed: "
                f"{e}"
            )

            return None

    # ==================================================
    # Find By Article ID
    # ==================================================

    def find_by_article_id(
        self,
        article_id
    ):
        """
        依 MySQL Article ID 查詢最新 Raw HTML Snapshot。
        """

        if article_id is None:

            return None

        try:

            return (
                self.collection.find_one(
                    {
                        "article_id":
                            article_id
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
                "Raw HTML find_by_article_id failed: "
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
        依 Article Document ID 查詢 Raw HTML。

        注意：

            document_id 不代表 Archive Version
            的唯一判斷條件。

            Archive Duplicate Detection：

                URL + content_hash
        """

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
        依 URL 查詢最新 Raw HTML Snapshot。

        如果同一 URL 有多個 Archive Version，
        回傳最新建立的 Snapshot。
        """

        if not url:

            return None

        try:

            return (
                self.collection.find_one(
                    {
                        "url": url
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
    # Find By URL + Content Hash
    # ==================================================

    def find_by_url_and_content_hash(
        self,
        url,
        content_hash
    ):
        """
        依：

            URL
            +
            Content Hash

        查詢 Raw HTML Snapshot。

        注意：

            此方法只提供查詢能力。

            不負責：

                Archive Duplicate Decision

            Duplicate Authority：

                ArchiveService
        """

        if not url:

            return None

        if not content_hash:

            return None

        try:

            return (
                self.collection.find_one(
                    {
                        "url": url,
                        "content_hash": content_hash
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

        注意：

            此方法只是 Entity Lookup。

            不代表：

                Archive Duplicate Detection
        """

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
        檢查：

            URL + Content Hash

        是否存在。

        注意：

            此方法只提供 Repository Lookup。

            最終 Duplicate Decision
            仍由 ArchiveService 負責。
        """

        if not url:

            return False

        if not content_hash:

            return False

        try:

            result = (
                self.collection.find_one(
                    {
                        "url": url,
                        "content_hash": content_hash
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
    # Update HTML
    # ==================================================

    def update_html(
        self,
        document_id,
        html,
        content_hash=None
    ):
        """
        更新指定 Document ID 的 Raw HTML。

        Parameters
        ----------

        document_id :
            Article Document ID

        html :
            新的 Raw HTML

        content_hash :
            新 HTML Content Hash


        注意：

            這是 Repository Update API。

            不負責 Archive Version。

            Archive Version 仍由：

                ArchiveService

            管理。
        """

        if not document_id:

            logger.error(
                "Raw HTML update failed: "
                "document_id is empty"
            )

            return False

        if html is None:

            logger.error(
                "Raw HTML update failed: "
                "html is None"
            )

            return False

        html = str(
            html
        )

        if not html:

            logger.error(
                "Raw HTML update failed: "
                "html is empty"
            )

            return False

        if content_hash is not None:

            content_hash = str(
                content_hash
            ).strip()

            if not content_hash:

                content_hash = None

        try:

            update_data = {

                "html": html,

                "updated_at":
                    datetime.now()

            }

            if content_hash is not None:

                update_data[
                    "content_hash"
                ] = content_hash

            result = (
                self.collection.update_one(

                    {
                        "document_id":
                            document_id
                    },

                    {
                        "$set":
                            update_data
                    }

                )
            )

            if result.matched_count == 0:

                logger.warning(
                    "Raw HTML update failed: "
                    f"document not found "
                    f"document_id={document_id}"
                )

                return False

            logger.info(
                "Raw HTML updated: "
                f"document_id={document_id}, "
                f"content_hash={content_hash}"
            )

            return True

        except PyMongoError as e:

            logger.exception(
                "Raw HTML update failed: "
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
        依 Document ID 刪除 Raw HTML。
        """

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

                logger.warning(
                    "Raw HTML delete failed: "
                    f"document not found "
                    f"document_id={document_id}"
                )

                return False

            logger.info(
                "Raw HTML deleted: "
                f"document_id={document_id}, "
                f"deleted={result.deleted_count}"
            )

            return True

        except PyMongoError as e:

            logger.exception(
                "Raw HTML delete failed: "
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
        取得 Raw HTML Document 數量。
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


# ======================================
#
# Public API
#
# ======================================

__all__ = [
    "RawHTMLRepository",
]
