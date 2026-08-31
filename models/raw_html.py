"""
models/raw_html.py

AutoSearch V5

Raw HTML MongoDB Model

功能：

1. 定義 MongoDB Raw HTML Snapshot 資料結構
2. 儲存原始 HTML 本體
3. 儲存 HTML Metadata
4. 儲存 Snapshot Resources
5. 提供 Repository 使用
6. 不負責 MongoDB Connection
7. 不負責 HTTP Download
8. 不負責 Resource Download
9. 不負責 Hash Calculation
10. 不負責 Archive Version

Storage：

    MongoDB
        ↓
    raw_html collection


MongoDB Document：

    raw_html
    ├── _id
    ├── url
    ├── html
    ├── content_hash
    ├── resolved_url
    ├── document_id
    ├── created_at
    ├── updated_at
    │
    └── resources
        ├── css[]
        │   ├── url
        │   ├── content
        │   ├── content_hash
        │   ├── mime_type
        │   └── file_size
        │
        └── images[]
            ├── url
            ├── data
            ├── content_hash
            ├── mime_type
            └── file_size


注意：

    本 Model 只描述資料結構。

    不負責：

        HTTP Download
        CSS Download
        Image Download
        Resource Extraction
        Hash Calculation
        MongoDB Connection
        Archive Version
        Duplicate Detection
"""


# ==================================================
#
# Standard Library
#
# ==================================================

from datetime import (
    datetime,
)


# ==================================================
#
# Raw HTML Model
#
# ==================================================

class RawHTML:
    """
    Raw HTML Model。

    代表 MongoDB raw_html
    Collection 中的一筆 Snapshot。

    正式欄位：

        _id
        url
        html
        content_hash
        resolved_url
        document_id
        created_at
        updated_at
        resources

    Resources：

        resources.css[]
        resources.images[]
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        url=None,
        html=None,
        content_hash=None,
        resolved_url=None,
        document_id=None,
        created_at=None,
        updated_at=None,
        resources=None,
        mongo_id=None,
    ):
        """
        建立 RawHTML Model。

        Parameters
        ----------
        url : str
            原始 URL。

        html : str
            原始 HTML。

        content_hash : str
            Raw HTML SHA-256。

        resolved_url : str
            Redirect 後 URL。

        document_id : str
            Article Document Identity。

        created_at : datetime
            Snapshot 建立時間。

        updated_at : datetime
            Snapshot 最後更新時間。

        resources : dict
            Snapshot Resource。

            結構：

                {
                    "css": [],
                    "images": []
                }

        mongo_id :
            MongoDB ObjectId。

        注意：

            Model 不負責：

                Resource Download
                Hash Calculation
                MongoDB Connection
        """

        # --------------------------------------------------
        # MongoDB ObjectId
        # --------------------------------------------------

        self.mongo_id = mongo_id

        # --------------------------------------------------
        # Original URL
        # --------------------------------------------------

        self.url = url

        # --------------------------------------------------
        # Raw HTML
        # --------------------------------------------------

        self.html = html

        # --------------------------------------------------
        # HTML Content Hash
        # --------------------------------------------------

        self.content_hash = content_hash

        # --------------------------------------------------
        # Resolved URL
        # --------------------------------------------------

        self.resolved_url = resolved_url

        # --------------------------------------------------
        # Document ID
        # --------------------------------------------------

        self.document_id = document_id

        # --------------------------------------------------
        # Created At
        # --------------------------------------------------

        self.created_at = created_at

        # --------------------------------------------------
        # Updated At
        # --------------------------------------------------

        self.updated_at = updated_at

        # --------------------------------------------------
        # Resources
        # --------------------------------------------------

        if resources is None:

            resources = {
                "css": [],
                "images": [],
            }

        self.resources = resources

    # ==================================================
    # To Mongo Document
    # ==================================================

    def to_dict(self):
        """
        RawHTML Model
            ↓
        MongoDB Document

        保留目前 MongoDB
        raw_html 正式欄位。

        不新增其他欄位。
        """

        document = {

            "url":
                self.url,

            "html":
                self.html,

            "content_hash":
                self.content_hash,

            "resolved_url":
                self.resolved_url,

            "document_id":
                self.document_id,

            "created_at":
                self.created_at,

            "updated_at":
                self.updated_at,

            "resources":
                self.resources,

        }

        # --------------------------------------------------
        # MongoDB ObjectId
        #
        # 只有既有 MongoDB Document
        # 才加入 _id。
        # --------------------------------------------------

        if self.mongo_id is not None:

            document["_id"] = (
                self.mongo_id
            )

        return document

    # ==================================================
    # From Mongo Document
    # ==================================================

    @classmethod
    def from_dict(
        cls,
        document,
    ):
        """
        MongoDB Document
            ↓
        RawHTML Model
        """

        if document is None:

            return None

        resources = (
            document.get(
                "resources"
            )
        )

        # --------------------------------------------------
        # Resource Default
        # --------------------------------------------------

        if resources is None:

            resources = {
                "css": [],
                "images": [],
            }

        return cls(

            mongo_id=document.get(
                "_id"
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

            resolved_url=document.get(
                "resolved_url"
            ),

            document_id=document.get(
                "document_id"
            ),

            created_at=document.get(
                "created_at"
            ),

            updated_at=document.get(
                "updated_at"
            ),

            resources=resources,

        )

    # ==================================================
    # Resource Helpers
    # ==================================================

    @property
    def css_resources(self):
        """
        取得 CSS Resources。
        """

        return self.resources.get(
            "css",
            []
        )

    # ==================================================

    @property
    def image_resources(self):
        """
        取得 Image Resources。
        """

        return self.resources.get(
            "images",
            []
        )

    # ==================================================
    # String
    # ==================================================

    def __repr__(self):
        """
        Debug representation。

        不輸出：

            完整 HTML
            CSS Content
            Image Data

        避免 Log / Console
        出現大量資料。
        """

        return (

            "RawHTML("

            f"mongo_id={self.mongo_id!r}, "

            f"url={self.url!r}, "

            f"content_hash="
            f"{self.content_hash!r}, "

            f"resolved_url="
            f"{self.resolved_url!r}, "

            f"document_id="
            f"{self.document_id!r}, "

            f"created_at="
            f"{self.created_at!r}, "

            f"updated_at="
            f"{self.updated_at!r}, "

            f"css_count="
            f"{len(self.css_resources)}, "

            f"image_count="
            f"{len(self.image_resources)}"

            ")"

        )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "RawHTML",
]