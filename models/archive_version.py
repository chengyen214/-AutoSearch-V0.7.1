"""
models/archive_version.py

AutoSearch V4

P2.2.2 Archive Version History

Archive Version Model

用途:

    保存同一篇 Article 的
    Raw HTML Archive 版本資訊

Database:

    archive_versions

支援:

    - Version Number
    - Raw Document Relation
    - File Hash
    - Storage Path
    - File Size
    - MIME Type
    - Created Time
"""

from datetime import datetime


class ArchiveVersion:

    def __init__(
        self,
        article_id=None,
        raw_document_id=None,
        version_number=1,
        file_hash="",
        storage_path="",
        file_size=0,
        mime_type="text/html",
        created_time=None
    ):

        # ==========================
        # Database ID
        # ==========================

        self.id = None

        # ==========================
        # Article Relation
        # ==========================

        self.article_id = article_id

        # ==========================
        # Raw Document Relation
        # ==========================

        self.raw_document_id = raw_document_id

        # ==========================
        # Version
        # ==========================

        self.version_number = version_number

        # ==========================
        # File Information
        # ==========================

        self.file_hash = file_hash

        self.storage_path = storage_path

        self.file_size = file_size

        self.mime_type = mime_type

        # ==========================
        # Time
        # ==========================

        self.created_time = (
            created_time
            if created_time
            else datetime.now()
        )

    # ==================================
    # Archive Properties
    # ==================================

    @property
    def filename(self):

        if self.storage_path:

            return self.storage_path.replace(
                "\\",
                "/"
            ).split("/")[-1]

        return ""

    @property
    def is_html(self):

        return self.mime_type == "text/html"

    # ==================================
    # Dictionary
    # ==================================

    def to_dict(self):

        return {

            "id":
                self.id,

            "article_id":
                self.article_id,

            "raw_document_id":
                self.raw_document_id,

            "version_number":
                self.version_number,

            "file_hash":
                self.file_hash,

            "storage_path":
                self.storage_path,

            "file_size":
                self.file_size,

            "mime_type":
                self.mime_type,

            "created_time":
                self.created_time
        }

    # ==================================
    # Representation
    # ==================================

    def __repr__(self):

        return (

            f"ArchiveVersion("

            f"article_id={self.article_id}, "

            f"raw_document_id={self.raw_document_id}, "

            f"version={self.version_number}, "

            f"path={self.storage_path}"

            ")"

        )