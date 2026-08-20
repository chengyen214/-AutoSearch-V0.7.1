"""
models/raw_html.py

AutoSearch V4

P4.5

Raw HTML MongoDB Model

功能:

1. 定義 MongoDB Raw HTML 資料結構
2. 儲存原始 HTML 本體
3. 儲存 HTML Metadata
4. 提供 Repository 使用
5. 不負責 MongoDB Connection
6. 不負責 HTML File Storage
7. 不負責 Archive Version

Storage:

    MongoDB
        ↓
    raw_html collection

注意:

    本 Model 不是 Local HTML Migration Tool。

    不負責:

        archive/html
            ↓
        MongoDB

    舊 HTML Migration
    將於後續 Migration 階段處理。
"""


from datetime import datetime


class RawHTML:
    """
    Raw HTML Model

    代表 MongoDB 中的一筆
    原始 HTML Archive。

    Storage:

        MongoDB

    Collection:

        raw_html
    """

    # ======================================
    # Initialize
    # ======================================

    def __init__(
        self,
        document_id=None,
        article_id=None,
        url=None,
        html=None,
        content_hash=None,
        mime_type="text/html",
        file_size=None,
        created_time=None,
        mongo_id=None
    ):
        """
        建立 RawHTML Model。

        Args:

            document_id:
                Article document_id

            article_id:
                Article database ID

            url:
                Original URL

            html:
                原始 HTML 本體

            content_hash:
                HTML Content SHA256

            mime_type:
                MIME Type

            file_size:
                HTML Size in Bytes

            created_time:
                建立時間

            mongo_id:
                MongoDB ObjectId
        """

        self.mongo_id = mongo_id

        self.document_id = (
            document_id
        )

        self.article_id = (
            article_id
        )

        self.url = (
            url
        )

        self.html = (
            html
        )

        self.content_hash = (
            content_hash
        )

        self.mime_type = (
            mime_type
        )

        self.file_size = (
            file_size
        )

        self.created_time = (
            created_time
            if created_time is not None
            else datetime.now()
        )

    # ======================================
    # To Mongo Document
    # ======================================

    def to_dict(self):
        """
        RawHTML Model
        ↓
        MongoDB Document

        MongoDB Repository
        將使用此方法建立 Document。
        """

        document = {

            "document_id":
                self.document_id,

            "article_id":
                self.article_id,

            "url":
                self.url,

            "html":
                self.html,

            "content_hash":
                self.content_hash,

            "mime_type":
                self.mime_type,

            "file_size":
                self.file_size,

            "created_time":
                self.created_time

        }

        # ----------------------------------
        # MongoDB ObjectId
        #
        # 只有已存在的 Mongo Document
        # 才加入 _id。
        # ----------------------------------

        if self.mongo_id is not None:

            document["_id"] = (
                self.mongo_id
            )

        return document

    # ======================================
    # From Mongo Document
    # ======================================

    @classmethod
    def from_dict(
        cls,
        document
    ):
        """
        MongoDB Document
        ↓
        RawHTML Model
        """

        if document is None:

            return None

        return cls(

            mongo_id=document.get(
                "_id"
            ),

            document_id=document.get(
                "document_id"
            ),

            article_id=document.get(
                "article_id"
            ),

            url=document.get(
                "url"
            ),

            html=document.get(
                "html"
            ),

            content_hash=document.get(
                "content_hash"
            ),

            mime_type=document.get(
                "mime_type",
                "text/html"
            ),

            file_size=document.get(
                "file_size"
            ),

            created_time=document.get(
                "created_time"
            )

        )

    # ======================================
    # String
    # ======================================

    def __repr__(self):
        """
        Debug representation。

        不直接輸出完整 HTML，
        避免 Log / Console 出現大量內容。
        """

        return (

            "RawHTML("

            f"document_id={self.document_id!r}, "

            f"article_id={self.article_id!r}, "

            f"url={self.url!r}, "

            f"content_hash={self.content_hash!r}, "

            f"file_size={self.file_size!r}, "

            f"mongo_id={self.mongo_id!r}"

            ")"

        )


# ======================================
# Public API
# ======================================

__all__ = [
    "RawHTML",
]
