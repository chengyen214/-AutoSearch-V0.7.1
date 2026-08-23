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

        article_id = None
        document_id = None

    但已經具有：

        url
        resolved_url
        html
        content_hash


Article 建立後：

    RawHTMLRepository.update_metadata()

    補回：

        article_id
        document_id


Duplicate Detection：

    本 Repository 只提供 Lookup。

    不負責：

        Duplicate Decision
        New Version Decision
        Archive Version


Duplicate Identity：

    URL
    +
    Content Hash

    由 ArchiveService 負責。


Hash：

    不由 Repository 計算。

    Hash 由：

        CrawlService

    或：

        ArchiveService

    產生。


本 Repository 不負責：

    - Crawler
    - HTTP Download
    - Hash Calculation
    - Parser
    - Article Model
    - MySQL ArticleRepository
    - Archive Duplicate Detection
    - Archive Version
    - AI Analysis
"""


# ==================================================
#
# Standard Library
#
# ==================================================

from datetime import datetime


# ==================================================
#
# MongoDB
#
# ==================================================

from bson import ObjectId

from pymongo.errors import (
    PyMongoError
)


# ==================================================
#
# Project
#
# ==================================================

from config.mongo_config import (
    MONGO_RAW_HTML_COLLECTION
)


from database.mongo_connection import (
    get_mongo_collection
)


from utils.logger import (
    logger
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


    Repository 不負責：

        - Hash Calculation
        - Duplicate Detection
        - Archive Version
        - Parser
        - Article
        - AI
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
        建立 Raw HTML Lookup Index。

        Index：

            article_id
            document_id
            url
            resolved_url
            content_hash

            url + content_hash

        注意：

            所有 Index 都不是 Unique。

            Duplicate Detection
            仍由 ArchiveService 負責。
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
                "resolved_url"
            )

            self.collection.create_index(
                "content_hash"
            )

            self.collection.create_index(
                [
                    ("url", 1),
                    ("content_hash", 1)
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
        article_id=None,
        document_id=None
    ):
        """
        儲存 Raw HTML Snapshot。

        Crawl 階段最小需求：

            url
            html
            content_hash


        Article 建立前：

            article_id=None
            document_id=None


        Article 建立後：

            可透過 update_metadata()
            補回 Article Identity。


        本方法不負責：

            Hash Calculation
            Duplicate Detection
            Archive Version
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
        # Normalize Article ID
        # ==================================================

        if article_id is not None:

            try:

                article_id = int(
                    article_id
                )

            except (
                TypeError,
                ValueError
            ):

                logger.error(
                    "Raw HTML save failed: "
                    f"invalid article_id={article_id}"
                )

                return None

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
        # Current Time
        # ==================================================

        now = datetime.now()

        # ==================================================
        # MongoDB Document
        # ==================================================

        document = {

            "article_id":
                article_id,

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
                now

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
                f"article_id={article_id}, "
                f"document_id={document_id}, "
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

            article_id=None
            document_id=None


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

            article_id=None,

            document_id=None

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
    # Find By Article ID
    # ==================================================

    def find_by_article_id(
        self,
        article_id
    ):
        """
        查詢 Article 最新 Raw HTML Snapshot。
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
        查詢 Article Document
        最新 Raw HTML Snapshot。
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

            不代表：

                Duplicate

            Duplicate Decision：

                ArchiveService
        """

        if not url:

            return False

        if not content_hash:

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
        article_id=None,
        document_id=None
    ):
        """
        Crawl 完成後：

            MongoDB Raw HTML
                    ↓
            Article 建立
                    ↓
            補回 Article Identity


        更新：

            article_id
            document_id


        不更新：

            url
            resolved_url
            html
            content_hash
        """

        if not mongo_id:

            return False

        update_data = {}

        # ==================================================
        # Article ID
        # ==================================================

        if article_id is not None:

            try:

                article_id = int(
                    article_id
                )

                update_data[
                    "article_id"
                ] = article_id

            except (
                TypeError,
                ValueError
            ):

                logger.error(
                    "Invalid article_id: "
                    f"{article_id}"
                )

                return False

        # ==================================================
        # Document ID
        # ==================================================

        if document_id is not None:

            document_id = str(
                document_id
            ).strip()

            if document_id:

                update_data[
                    "document_id"
                ] = document_id

        # ==================================================
        # Nothing To Update
        # ==================================================

        if not update_data:

            return False

        update_data[
            "updated_at"
        ] = datetime.now()

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
                f"article_id={article_id}, "
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
                                datetime.now()

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
