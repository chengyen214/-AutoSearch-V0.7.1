"""
services/archive_web_service.py

AutoSearch V4

P2.4.2 Composite Archive Search

功能：

P2.3.9:

- Archive Browser
- Article Browser
- Version Browser
- Date Browser
- Source Browser
- Archive Search
- Archive Statistics
- Pagination
- Knowledge History
- Knowledge Evolution
- Latest Knowledge

P2.4.2:

- Composite Archive Search
- Optional Filters
- Advanced Filtering
- Pagination
- Dynamic Query Conditions
- Optional URL Search

設計：

API / Web UI
      ↓
ArchiveWebService
      ↓
ArchiveBrowserRepository
      ↓
KnowledgeHistoryEngine
      ↓
Database

注意：

本 Service 不直接操作 Database。

Composite Search 原則：

    使用者提供什麼條件
            ↓
    只啟用該條件
            ↓
    組合搜尋
            ↓
    回傳結果
"""


from database.archive_browser_repository import (
    ArchiveBrowserRepository
)

from archive.knowledge_history import (
    KnowledgeHistoryEngine
)


class ArchiveWebService:

    """
    Archive Web UI / API Service

    P2.3.9
    P2.4.2

    負責：

    1. Archive Browser
    2. Archive Search
    3. Composite Archive Search
    4. Archive Statistics
    5. Knowledge History
    6. Knowledge Evolution
    """

    # ==================================================
    # Init
    # ==================================================

    def __init__(
        self,
        repository=None,
        knowledge_history=None
    ):

        # ----------------------------------------------
        # Archive Browser Repository
        # ----------------------------------------------

        if repository is None:

            repository = (
                ArchiveBrowserRepository()
            )

        self.repository = repository

        # ----------------------------------------------
        # Knowledge History
        # ----------------------------------------------

        if knowledge_history is None:

            knowledge_history = (
                KnowledgeHistoryEngine()
            )

        self.knowledge_history = (
            knowledge_history
        )

    # ==================================================
    # Articles
    # ==================================================

    def get_articles(
        self,
        limit=None
    ):
        """
        取得 Archive Articles。
        """

        if hasattr(
            self.repository,
            "get_articles"
        ):

            if limit is None:

                return self.repository.get_articles()

            return self.repository.get_articles(
                limit=limit
            )

        return []

    # ==================================================

    def get_articles_with_pagination(
        self,
        page=1,
        page_size=20
    ):
        """
        取得分頁 Archive Articles。
        """

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 20

        offset = (
            (page - 1)
            * page_size
        )

        if hasattr(
            self.repository,
            "get_articles_with_pagination"
        ):

            return (
                self.repository
                .get_articles_with_pagination(
                    page=page,
                    page_size=page_size
                )
            )

        # ----------------------------------------------
        # Fallback
        # ----------------------------------------------

        articles = self.get_articles()

        return articles[
            offset:
            offset + page_size
        ]

    # ==================================================
    # Article
    # ==================================================

    def get_article(
        self,
        article_id
    ):
        """
        取得單一 Article。
        """

        if hasattr(
            self.repository,
            "get_article"
        ):

            return self.repository.get_article(
                article_id
            )

        if hasattr(
            self.repository,
            "get_by_id"
        ):

            return self.repository.get_by_id(
                article_id
            )

        return None

    # ==================================================
    # Versions
    # ==================================================

    def get_versions(
        self,
        article_id
    ):
        """
        取得 Article 所有 Archive Versions。
        """

        if hasattr(
            self.repository,
            "get_versions"
        ):

            return self.repository.get_versions(
                article_id
            )

        return []

    # ==================================================

    def get_latest_version(
        self,
        article_id
    ):
        """
        取得最新 Archive Version。
        """

        if hasattr(
            self.repository,
            "get_latest_version"
        ):

            return (
                self.repository
                .get_latest_version(
                    article_id
                )
            )

        versions = self.get_versions(
            article_id
        )

        if not versions:
            return None

        return max(
            versions,
            key=lambda item: (
                item.get(
                    "version_number",
                    0
                )
                if isinstance(
                    item,
                    dict
                )
                else getattr(
                    item,
                    "version_number",
                    0
                )
            )
        )

    # ==================================================
    # Date Browser
    # ==================================================

    def get_by_date(
        self,
        archive_date
    ):
        """
        依日期取得 Archive。
        """

        if hasattr(
            self.repository,
            "get_by_date"
        ):

            return (
                self.repository
                .get_by_date(
                    archive_date
                )
            )

        return []

    # ==================================================

    def get_by_month(
        self,
        year,
        month
    ):
        """
        依月份取得 Archive。
        """

        if hasattr(
            self.repository,
            "get_by_month"
        ):

            return (
                self.repository
                .get_by_month(
                    year,
                    month
                )
            )

        return []

    # ==================================================

    def get_by_year(
        self,
        year
    ):
        """
        依年份取得 Archive。
        """

        if hasattr(
            self.repository,
            "get_by_year"
        ):

            return (
                self.repository
                .get_by_year(
                    year
                )
            )

        return []

    # ==================================================
    # Source Browser
    # ==================================================

    def get_by_source(
        self,
        source
    ):
        """
        依來源取得 Archive。
        """

        if hasattr(
            self.repository,
            "get_by_source"
        ):

            return (
                self.repository
                .get_by_source(
                    source
                )
            )

        return []

    # ==================================================
    # Basic Search
    # ==================================================

    def search(
        self,
        keyword
    ):
        """
        Archive Browser 基本搜尋。

        P2.3.9。
        """

        if keyword is None:
            return []

        keyword = str(
            keyword
        ).strip()

        if not keyword:
            return []

        if hasattr(
            self.repository,
            "search"
        ):

            return (
                self.repository
                .search(
                    keyword
                )
            )

        return []

    # ==================================================
    # P2.4.2
    # Composite Archive Search
    # ==================================================

    def composite_search(
        self,
        keyword=None,
        source=None,
        url=None,
        date_from=None,
        date_to=None,
        year=None,
        month=None,
        category=None,
        importance_min=None,
        importance_max=None,
        page=1,
        page_size=20
    ):
        """
        P2.4.2

        Composite Archive Search。

        所有條件皆為 Optional。

        只有使用者提供的條件
        才會參與搜尋。

        支援：

            keyword
            source
            url
            date_from
            date_to
            year
            month
            category
            importance_min
            importance_max

        分頁：

            page
            page_size

        URL 搜尋：

            url="tsmc.com"

        Example:

            keyword="TSMC"

            keyword="TSMC",
            source="CNA"

            keyword="TSMC",
            url="tsmc.com"

            keyword="TSMC",
            source="CNA",
            url="cna.com.tw",
            date_from="2026-08-01",
            date_to="2026-08-09"

            category="Semiconductor",
            importance_min=8
        """

        # ==================================================
        # Normalize
        # ==================================================

        if keyword is not None:

            keyword = str(
                keyword
            ).strip()

            if not keyword:

                keyword = None

        if source is not None:

            source = str(
                source
            ).strip()

            if not source:

                source = None

        if url is not None:

            url = str(
                url
            ).strip()

            if not url:

                url = None

        if category is not None:

            category = str(
                category
            ).strip()

            if not category:

                category = None

        # ==================================================
        # Pagination Normalize
        # ==================================================

        try:

            page = int(page)

        except (
            TypeError,
            ValueError
        ):

            page = 1

        try:

            page_size = int(page_size)

        except (
            TypeError,
            ValueError
        ):

            page_size = 20

        if page < 1:

            page = 1

        if page_size < 1:

            page_size = 20

        # ==================================================
        # Repository Native Composite Search
        # ==================================================

        if hasattr(
            self.repository,
            "composite_search"
        ):

            return (
                self.repository
                .composite_search(
                    keyword=keyword,
                    source=source,
                    url=url,
                    date_from=date_from,
                    date_to=date_to,
                    year=year,
                    month=month,
                    category=category,
                    importance_min=importance_min,
                    importance_max=importance_max,
                    page=page,
                    page_size=page_size
                )
            )

        # ==================================================
        # Fallback Search
        # ==================================================

        articles = self.get_articles()

        if articles is None:

            articles = []

        # ==================================================
        # Filter Helper
        # ==================================================

        def get_value(
            item,
            *names
        ):

            for name in names:

                if isinstance(
                    item,
                    dict
                ):

                    if name in item:

                        return item[name]

                else:

                    if hasattr(
                        item,
                        name
                    ):

                        return getattr(
                            item,
                            name
                        )

            return None

        # ==================================================
        # Date Normalize Helper
        # ==================================================

        def normalize_date(
            value
        ):

            if value is None:

                return ""

            return str(
                value
            )[:10]

        # ==================================================
        # Numeric Helper
        # ==================================================

        def numeric_value(
            value
        ):

            if value is None:

                return None

            try:

                return float(
                    value
                )

            except (
                TypeError,
                ValueError
            ):

                return None

        # ==================================================
        # Filter
        # ==================================================

        filtered = []

        for article in articles:

            # ------------------------------------------
            # Keyword
            # ------------------------------------------

            if keyword is not None:

                title = get_value(
                    article,
                    "title"
                )

                content = get_value(
                    article,
                    "content"
                )

                article_keyword = get_value(
                    article,
                    "keyword",
                    "keywords"
                )

                searchable_text = " ".join(
                    str(value)
                    for value in (
                        title,
                        content,
                        article_keyword
                    )
                    if value is not None
                ).lower()

                if keyword.lower() not in (
                    searchable_text
                ):

                    continue

            # ------------------------------------------
            # Source
            # ------------------------------------------

            if source is not None:

                article_source = get_value(
                    article,
                    "source"
                )

                if article_source is None:

                    continue

                if str(
                    article_source
                ).lower() != source.lower():

                    continue

            # ------------------------------------------
            # URL
            # ------------------------------------------

            if url is not None:

                article_url = get_value(
                    article,
                    "url"
                )

                if article_url is None:

                    continue

                if url.lower() not in str(
                    article_url
                ).lower():

                    continue

            # ------------------------------------------
            # Archive Date
            # ------------------------------------------

            article_date = get_value(
                article,
                "archive_date",
                "published",
                "crawl_time",
                "created_at",
                "date"
            )

            normalized_article_date = (
                normalize_date(
                    article_date
                )
            )

            # ------------------------------------------
            # Date From
            # ------------------------------------------

            if date_from is not None:

                normalized_date_from = (
                    normalize_date(
                        date_from
                    )
                )

                if (
                    not normalized_article_date
                    or normalized_article_date
                    < normalized_date_from
                ):

                    continue

            # ------------------------------------------
            # Date To
            # ------------------------------------------

            if date_to is not None:

                normalized_date_to = (
                    normalize_date(
                        date_to
                    )
                )

                if (
                    not normalized_article_date
                    or normalized_article_date
                    > normalized_date_to
                ):

                    continue

            # ------------------------------------------
            # Year
            # ------------------------------------------

            if year is not None:

                try:

                    article_year = int(
                        normalized_article_date[
                            :4
                        ]
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    continue

                if article_year != int(
                    year
                ):

                    continue

            # ------------------------------------------
            # Month
            # ------------------------------------------

            if month is not None:

                try:

                    article_month = int(
                        normalized_article_date[
                            5:7
                        ]
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    continue

                if article_month != int(
                    month
                ):

                    continue

            # ------------------------------------------
            # Category
            # ------------------------------------------

            if category is not None:

                article_category = get_value(
                    article,
                    "category",
                    "ai_category"
                )

                if article_category is None:

                    continue

                if str(
                    article_category
                ).lower() != category.lower():

                    continue

            # ------------------------------------------
            # Importance
            # ------------------------------------------

            importance = get_value(
                article,
                "importance",
                "ai_importance"
            )

            numeric_importance = (
                numeric_value(
                    importance
                )
            )

            if importance_min is not None:

                if (
                    numeric_importance is None
                    or numeric_importance
                    < float(importance_min)
                ):

                    continue

            if importance_max is not None:

                if (
                    numeric_importance is None
                    or numeric_importance
                    > float(importance_max)
                ):

                    continue

            # ------------------------------------------
            # Passed all active filters
            # ------------------------------------------

            filtered.append(
                article
            )

        # ==================================================
        # Pagination
        # ==================================================

        total = len(
            filtered
        )

        offset = (
            (page - 1)
            * page_size
        )

        results = filtered[
            offset:
            offset + page_size
        ]

        # ==================================================
        # Active Filters
        # ==================================================

        filters = {}

        if keyword is not None:
            filters["keyword"] = keyword

        if source is not None:
            filters["source"] = source

        if url is not None:
            filters["url"] = url

        if date_from is not None:
            filters["date_from"] = date_from

        if date_to is not None:
            filters["date_to"] = date_to

        if year is not None:
            filters["year"] = year

        if month is not None:
            filters["month"] = month

        if category is not None:
            filters["category"] = category

        if importance_min is not None:
            filters["importance_min"] = (
                importance_min
            )

        if importance_max is not None:
            filters["importance_max"] = (
                importance_max
            )

        # ==================================================
        # Result
        # ==================================================

        return {

            "results":
                results,

            "total":
                total,

            "page":
                page,

            "page_size":
                page_size,

            "filters":
                filters

        }

    # ==================================================
    # Count
    # ==================================================

    def count(self):
        """
        取得 Archive 總數。
        """

        if hasattr(
            self.repository,
            "count"
        ):

            return self.repository.count()

        return 0

    # ==================================================

    def count_articles(self):
        """
        取得 Article 數量。
        """

        if hasattr(
            self.repository,
            "count_articles"
        ):

            return (
                self.repository
                .count_articles()
            )

        return self.count()

    # ==================================================

    def count_by_source(
        self,
        source=None
    ):
        """
        依 Source 統計 Archive 數量。
        """

        if hasattr(
            self.repository,
            "count_by_source"
        ):

            if source is None:

                return (
                    self.repository
                    .count_by_source()
                )

            return (
                self.repository
                .count_by_source(
                    source
                )
            )

        return 0

    # ==================================================

    def count_by_date(
        self,
        archive_date=None
    ):
        """
        依日期統計 Archive 數量。
        """

        if hasattr(
            self.repository,
            "count_by_date"
        ):

            if archive_date is None:

                return (
                    self.repository
                    .count_by_date()
                )

            return (
                self.repository
                .count_by_date(
                    archive_date
                )
            )

        return 0

    # ==================================================
    # Statistics
    # ==================================================

    def get_statistics(self):
        """
        取得 Archive Statistics。
        """

        if hasattr(
            self.repository,
            "get_statistics"
        ):

            return (
                self.repository
                .get_statistics()
            )

        return {

            "count":
                self.count(),

            "articles":
                self.count_articles()

        }

    # ==================================================
    # Knowledge History
    # ==================================================

    def get_knowledge_history(
        self,
        article_id
    ):
        """
        取得 Article Knowledge History。
        """

        if self.knowledge_history is None:

            return []

        return (
            self.knowledge_history
            .get_history(
                article_id
            )
        )

    # ==================================================

    def get_latest_knowledge(
        self,
        article_id
    ):
        """
        取得最新 Knowledge。
        """

        if self.knowledge_history is None:

            return None

        return (
            self.knowledge_history
            .get_latest(
                article_id
            )
        )

    # ==================================================

    def get_knowledge_evolution(
        self,
        article_id
    ):
        """
        取得完整 Knowledge Evolution。

        優先：

            get_knowledge_evolution()

        相容：

            get_timeline()

        最後：

            get_history()
        """

        if self.knowledge_history is None:

            return []

        # ==================================
        # Preferred API
        # ==================================

        if hasattr(
            self.knowledge_history,
            "get_knowledge_evolution"
        ):

            result = (
                self.knowledge_history
                .get_knowledge_evolution(
                    article_id
                )
            )

            return result or []

        # ==================================
        # Compatibility API
        # ==================================

        if hasattr(
            self.knowledge_history,
            "get_timeline"
        ):

            result = (
                self.knowledge_history
                .get_timeline(
                    article_id
                )
            )

            return result or []

        # ==================================
        # History fallback
        # ==================================

        if hasattr(
            self.knowledge_history,
            "get_history"
        ):

            result = (
                self.knowledge_history
                .get_history(
                    article_id
                )
            )

            return result or []

        return []

    # ==================================================
    # Knowledge Timeline
    # ==================================================

    def get_knowledge_timeline(
        self,
        article_id
    ):
        """
        取得 Knowledge Timeline。
        """

        if self.knowledge_history is None:

            return []

        return (
            self.knowledge_history
            .get_timeline(
                article_id
            )
        )

    # ==================================================
    # Knowledge Categories
    # ==================================================

    def get_knowledge_categories(
        self,
        article_id
    ):
        """
        取得 Category 演變。
        """

        if self.knowledge_history is None:

            return []

        return (
            self.knowledge_history
            .get_categories(
                article_id
            )
        )

    # ==================================================
    # Knowledge Keywords
    # ==================================================

    def get_knowledge_keywords(
        self,
        article_id
    ):
        """
        取得 Keywords 演變。
        """

        if self.knowledge_history is None:

            return []

        return (
            self.knowledge_history
            .get_keywords(
                article_id
            )
        )

    # ==================================================
    # Knowledge Importance
    # ==================================================

    def get_importance_history(
        self,
        article_id
    ):
        """
        取得 Importance History。
        """

        if self.knowledge_history is None:

            return []

        return (
            self.knowledge_history
            .get_importance_history(
                article_id
            )
        )

    # ==================================================
    # Knowledge Confidence
    # ==================================================

    def get_confidence_history(
        self,
        article_id
    ):
        """
        取得 Confidence History。
        """

        if self.knowledge_history is None:

            return []

        return (
            self.knowledge_history
            .get_confidence_history(
                article_id
            )
        )

    # ==================================================
    # Repr
    # ==================================================

    def __repr__(self):

        return (
            "ArchiveWebService("
            f"repository="
            f"{self.repository!r}, "
            f"knowledge_history="
            f"{self.knowledge_history!r}"
            ")"
        )
