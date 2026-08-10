"""
models/archive_view.py

AutoSearch V4

P2.3.5 Archive Viewer / Historical Content Retrieval

用途:

    儲存 Archive Viewer 所需要的歷史版本資料。

功能:

    1. 儲存 Article 基本資訊
    2. 儲存 Archive Version 資訊
    3. 儲存歷史內容
    4. 儲存 Archive Metadata
    5. 提供 Viewer 統一資料格式

設計:

    Archive Repository
            ↓
      Archive Viewer
            ↓
        ArchiveView
            ↓
      Archive Web UI

注意:

    本 Model 不直接操作 Database。
"""


class ArchiveView:

    """
    Archive Viewer Data Model
    """

    # ==================================
    # Constructor
    # ==================================

    def __init__(
        self,
        article_id=None,
        version_id=None,
        version_number=None,
        title="",
        url="",
        content="",
        storage_path=None,
        file_hash=None,
        file_size=0,
        mime_type="text/html",
        created_time=None,
        metadata=None
    ):

        self.article_id = article_id

        self.version_id = version_id

        self.version_number = version_number

        self.title = title

        self.url = url

        self.content = content

        self.storage_path = storage_path

        self.file_hash = file_hash

        self.file_size = file_size

        self.mime_type = mime_type

        self.created_time = created_time

        self.metadata = (
            metadata
            if metadata is not None
            else {}
        )

    # ==================================
    # Has Content
    # ==================================

    @property
    def has_content(self):

        return bool(
            self.content
        )

    # ==================================
    # Is Latest
    # ==================================

    def is_latest(
        self,
        latest_version
    ):

        return (
            self.version_number
            == latest_version
        )

    # ==================================
    # Is First
    # ==================================

    def is_first(self):

        return (
            self.version_number
            == 1
        )

    # ==================================
    # Content Length
    # ==================================

    @property
    def content_length(self):

        return len(
            self.content
            if self.content
            else ""
        )

    # ==================================
    # To Dict
    # ==================================

    def to_dict(self):

        return {

            "article_id":
                self.article_id,

            "version_id":
                self.version_id,

            "version_number":
                self.version_number,

            "title":
                self.title,

            "url":
                self.url,

            "content":
                self.content,

            "storage_path":
                self.storage_path,

            "file_hash":
                self.file_hash,

            "file_size":
                self.file_size,

            "mime_type":
                self.mime_type,

            "created_time":
                self.created_time,

            "metadata":
                self.metadata
        }

    # ==================================
    # Summary
    # ==================================

    def summary(self):

        return {

            "article_id":
                self.article_id,

            "version_id":
                self.version_id,

            "version_number":
                self.version_number,

            "title":
                self.title,

            "content_length":
                self.content_length,

            "has_content":
                self.has_content,

            "created_time":
                self.created_time
        }

    # ==================================
    # Repr
    # ==================================

    def __repr__(self):

        return (
            "ArchiveView("
            f"article_id={self.article_id}, "
            f"version_id={self.version_id}, "
            f"version_number={self.version_number}, "
            f"title={self.title!r}, "
            f"content_length={self.content_length}"
            ")"
        )