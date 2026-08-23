"""
models/target.py

AutoSearch V5

V5.3 P3.1

Target Model Extension

用途：

    定義使用者指定的資料取得目標。

支援：

    1. URL Target
    2. Search Target
    3. Search Keyword
    4. Search Provider

架構：

    User Target
        ↓
    Target
        ├── URL Target
        │      ↓
        │   Direct URL
        │
        └── Search Target
               ↓
           Search Provider
               ├── Google Search
               └── Google News
        ↓
    Existing V4 Crawl Pipeline

Target 不負責：

    - Search Provider
    - Search API
    - SearchAdapter
    - Crawler
    - Parser
    - Archive
    - Duplicate Detection
    - AI Analysis
"""


from datetime import datetime


class Target:
    """
    V5 Target Model。

    Target 表示使用者希望 AutoSearch
    處理的資料來源。

    支援兩種主要 Target：

        URL Target
            ↓
        直接指定 URL

        Search Target
            ↓
        使用 Search Provider 搜尋
    """

    # ==================================
    # Target Types
    # ==================================

    TYPE_URL = "url"

    TYPE_SEARCH = "search"

    # ==================================
    # Default Values
    # ==================================

    DEFAULT_TYPE = TYPE_URL

    DEFAULT_STATUS = "active"

    # ==================================
    # Search Providers
    # ==================================

    PROVIDER_GOOGLE_SEARCH = (
        "google_search"
    )

    PROVIDER_GOOGLE_NEWS = (
        "google_news"
    )

    # ==================================
    # Constructor
    # ==================================

    def __init__(
        self,
        name="",
        target_type=None,
        url="",
        keyword="",
        search_provider="",
        status="active",
        description="",
        created_time=None,
        updated_time=None,
    ):

        # ==============================
        # Database ID
        # ==============================

        self.id = None

        # ==============================
        # Target Basic Information
        # ==============================

        self.name = (
            name
            if name is not None
            else ""
        )

        self.target_type = (
            target_type
            if target_type
            else self.DEFAULT_TYPE
        )

        # ==============================
        # URL Target
        # ==============================

        self.url = (
            url
            if url is not None
            else ""
        )

        # ==============================
        # Search Target
        # ==============================

        self.keyword = (
            keyword
            if keyword is not None
            else ""
        )

        self.search_provider = (
            search_provider
            if search_provider is not None
            else ""
        )

        # ==============================
        # Description
        # ==============================

        self.description = (
            description
            if description is not None
            else ""
        )

        # ==============================
        # Target Status
        # ==============================

        self.status = (
            status
            if status
            else self.DEFAULT_STATUS
        )

        # ==============================
        # Time
        # ==============================

        self.created_time = (
            created_time
            if created_time
            else datetime.now()
        )

        self.updated_time = (
            updated_time
            if updated_time
            else datetime.now()
        )

    # ==================================
    # Target Type
    # ==================================

    @property
    def is_url_target(self):
        """
        判斷是否為 URL Target。
        """

        return (
            self.target_type
            == self.TYPE_URL
        )

    # ==================================

    @property
    def is_search_target(self):
        """
        判斷是否為 Search Target。
        """

        return (
            self.target_type
            == self.TYPE_SEARCH
        )

    # ==================================
    # Active
    # ==================================

    @property
    def is_active(self):
        """
        判斷 Target 是否啟用。
        """

        return (
            self.status
            == self.DEFAULT_STATUS
        )

    # ==================================
    # Search Provider
    # ==================================

    @property
    def has_search_provider(self):
        """
        判斷 Search Target
        是否指定 Search Provider。
        """

        return bool(
            self.search_provider
        )

    # ==================================
    # Search Target Configuration
    # ==================================

    @property
    def is_google_search(self):
        """
        判斷是否使用 Google Search。
        """

        return (
            self.search_provider
            == self.PROVIDER_GOOGLE_SEARCH
        )

    # ==================================

    @property
    def is_google_news(self):
        """
        判斷是否使用 Google News。
        """

        return (
            self.search_provider
            == self.PROVIDER_GOOGLE_NEWS
        )

    # ==================================
    # Dictionary
    # ==================================

    def to_dict(self):
        """
        將 Target 轉成 dictionary。
        """

        return {

            "id":
                self.id,

            "name":
                self.name,

            "target_type":
                self.target_type,

            "url":
                self.url,

            "keyword":
                self.keyword,

            "search_provider":
                self.search_provider,

            "description":
                self.description,

            "status":
                self.status,

            "created_time":
                self.created_time,

            "updated_time":
                self.updated_time,
        }

    # ==================================
    # Representation
    # ==================================

    def __repr__(self):

        return (

            "Target("

            f"id={self.id}, "

            f"name={self.name}, "

            f"type={self.target_type}, "

            f"url={self.url}, "

            f"keyword={self.keyword}, "

            f"provider={self.search_provider}, "

            f"status={self.status}"

            ")"
        )


# ==================================
# Public API
# ==================================

__all__ = [
    "Target",
]