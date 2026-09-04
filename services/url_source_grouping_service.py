"""
services/url_source_grouping_service.py

AutoSearch V6.4

URL Source Grouping Service

功能：

1. 從 articles 取得所有 URL
2. 從 targets 取得 crawler_url
3. 排除已存在於 targets 的來源 URL
4. 將剩餘 URL 依 hostname 分組
5. 只保留 URL 數量 >= 3 的來源
6. 回傳 Source Groups

注意：

本 Service 只負責：

    Article URL
        ↓
    Target Crawler URL Exclusion
        ↓
    URL Source Grouping
        ↓
    Source Groups

本 Service 不負責：

- Gemini
- AIAnalyzer
- AI Worker
- Target INSERT / UPDATE
- Crawl
- Parser
"""

from urllib.parse import urlparse

from database.connection import get_connection


class URLSourceGroupingService:
    """
    AutoSearch V6.4

    URL Source Grouping Service。

    將 articles.url：

        1. 排除已存在 targets.crawler_url
        2. 依 hostname 分組
        3. 只保留至少指定數量 URL 的來源
    """

    # ==========================================================
    # Configuration
    # ==========================================================

    MIN_URLS_PER_SOURCE = 3

    # ==========================================================
    # Initialization
    # ==========================================================

    def __init__(
        self,
        min_urls_per_source=None,
    ):
        """
        初始化 URL Source Grouping Service。

        Args:
            min_urls_per_source:
                每個來源至少需要幾個不同 URL。
                預設為 MIN_URLS_PER_SOURCE。
        """

        if min_urls_per_source is None:
            min_urls_per_source = (
                self.MIN_URLS_PER_SOURCE
            )

        try:
            min_urls_per_source = int(
                min_urls_per_source
            )
        except (
            TypeError,
            ValueError,
        ):
            min_urls_per_source = (
                self.MIN_URLS_PER_SOURCE
            )

        if min_urls_per_source <= 0:
            min_urls_per_source = (
                self.MIN_URLS_PER_SOURCE
            )

        self.min_urls_per_source = (
            min_urls_per_source
        )

    # ==========================================================
    # URL Normalization
    # ==========================================================

    @staticmethod
    def normalize_url(
        url,
    ):
        """
        Normalize URL。

        規則：

        - 移除前後空白
        - scheme lowercase
        - netloc lowercase
        - 移除 fragment
        - 保留 path
        - 保留 query
        """

        if url is None:
            return ""

        value = str(
            url
        ).strip()

        if not value:
            return ""

        parsed = urlparse(
            value
        )

        if not parsed.scheme:
            return ""

        if not parsed.netloc:
            return ""

        scheme = (
            parsed.scheme
            .lower()
        )

        netloc = (
            parsed.netloc
            .lower()
        )

        normalized = (
            f"{scheme}://"
            f"{netloc}"
            f"{parsed.path}"
        )

        if parsed.query:
            normalized += (
                f"?{parsed.query}"
            )

        return normalized

    # ==========================================================
    # Host Normalization
    # ==========================================================

    @staticmethod
    def normalize_host(
        url,
    ):
        """
        取得 URL hostname。

        例如：

            https://www.tsmc.com/news/a
                ↓
            www.tsmc.com
        """

        if url is None:
            return ""

        value = str(
            url
        ).strip()

        if not value:
            return ""

        parsed = urlparse(
            value
        )

        if not parsed.hostname:
            return ""

        return (
            parsed.hostname
            .strip()
            .lower()
        )

    # ==========================================================
    # Crawler URL Matching
    # ==========================================================

    @classmethod
    def is_excluded_by_crawler_url(
        cls,
        article_url,
        crawler_url,
    ):
        """
        判斷 article URL 是否應該被 crawler_url 排除。

        規則：

        crawler_url：

            https://www.example.com/

        排除：

            https://www.example.com/a
            https://www.example.com/b
            https://www.example.com/news/a

        但不排除：

            https://www.other.com/a

        如果 crawler_url 有 path：

            https://www.example.com/news/

        則排除：

            https://www.example.com/news/a
            https://www.example.com/news/b

        但不排除：

            https://www.example.com/article/a
        """

        normalized_article = (
            cls.normalize_url(
                article_url
            )
        )

        normalized_crawler = (
            cls.normalize_url(
                crawler_url
            )
        )

        if not normalized_article:
            return False

        if not normalized_crawler:
            return False

        article_parsed = urlparse(
            normalized_article
        )

        crawler_parsed = urlparse(
            normalized_crawler
        )

        article_host = (
            article_parsed.hostname
            or ""
        ).lower()

        crawler_host = (
            crawler_parsed.hostname
            or ""
        ).lower()

        if article_host != crawler_host:
            return False

        crawler_path = (
            crawler_parsed.path
            or "/"
        )

        article_path = (
            article_parsed.path
            or "/"
        )

        crawler_path = (
            crawler_path.rstrip("/")
            or "/"
        )

        article_path = (
            article_path.rstrip("/")
            or "/"
        )

        # ------------------------------------------------------
        # crawler_url 是網站 root
        # ------------------------------------------------------

        if crawler_path == "/":
            return True

        # ------------------------------------------------------
        # 完全相同 path
        # ------------------------------------------------------

        if article_path == crawler_path:
            return True

        # ------------------------------------------------------
        # crawler path 是 article path 的父層
        # ------------------------------------------------------

        prefix = (
            crawler_path.rstrip("/")
            + "/"
        )

        if article_path.startswith(
            prefix
        ):
            return True

        return False

    # ==========================================================
    # Fetch Article URLs
    # ==========================================================

    def fetch_article_urls(
        self,
    ):
        """
        從 articles 取得所有 URL。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:
            sql = """
            SELECT url
            FROM articles
            WHERE url IS NOT NULL
              AND TRIM(url) <> ''
            ORDER BY id ASC
            """

            cursor.execute(
                sql
            )

            rows = cursor.fetchall()

            urls = []

            for row in rows:

                if isinstance(
                    row,
                    dict,
                ):
                    value = row.get(
                        "url"
                    )

                else:
                    value = row[0]

                if value is None:
                    continue

                value = str(
                    value
                ).strip()

                if not value:
                    continue

                urls.append(
                    value
                )

            return urls

        finally:

            cursor.close()
            conn.close()

    # ==========================================================
    # Fetch Target Crawler URLs
    # ==========================================================

    def fetch_crawler_urls(
        self,
    ):
        """
        從 targets 取得 crawler_url。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:
            sql = """
            SELECT crawler_url
            FROM targets
            WHERE crawler_url IS NOT NULL
              AND TRIM(crawler_url) <> ''
            ORDER BY id ASC
            """

            cursor.execute(
                sql
            )

            rows = cursor.fetchall()

            urls = []

            for row in rows:

                if isinstance(
                    row,
                    dict,
                ):
                    value = row.get(
                        "crawler_url"
                    )

                else:
                    value = row[0]

                if value is None:
                    continue

                value = str(
                    value
                ).strip()

                if not value:
                    continue

                urls.append(
                    value
                )

            return urls

        finally:

            cursor.close()
            conn.close()

    # ==========================================================
    # Exclude Crawler URLs
    # ==========================================================

    @classmethod
    def exclude_crawler_urls(
        cls,
        article_urls,
        crawler_urls,
    ):
        """
        排除已經存在 targets.crawler_url
        所代表來源的 Article URL。

        Returns:
            (
                remaining_urls,
                excluded_urls
            )
        """

        if article_urls is None:
            article_urls = []

        if crawler_urls is None:
            crawler_urls = []

        normalized_crawler_urls = []

        for crawler_url in crawler_urls:

            normalized = (
                cls.normalize_url(
                    crawler_url
                )
            )

            if not normalized:
                continue

            if normalized not in (
                normalized_crawler_urls
            ):
                normalized_crawler_urls.append(
                    normalized
                )

        remaining_urls = []
        excluded_urls = []

        seen_urls = set()

        for article_url in article_urls:

            normalized_article = (
                cls.normalize_url(
                    article_url
                )
            )

            if not normalized_article:
                continue

            # --------------------------------------------------
            # Deduplicate Article URL
            # --------------------------------------------------

            if normalized_article in seen_urls:
                continue

            seen_urls.add(
                normalized_article
            )

            # --------------------------------------------------
            # Crawler URL Exclusion
            # --------------------------------------------------

            excluded = False

            for crawler_url in (
                normalized_crawler_urls
            ):

                if cls.is_excluded_by_crawler_url(
                    normalized_article,
                    crawler_url,
                ):
                    excluded = True
                    break

            if excluded:
                excluded_urls.append(
                    normalized_article
                )
            else:
                remaining_urls.append(
                    normalized_article
                )

        return (
            remaining_urls,
            excluded_urls,
        )

    # ==========================================================
    # Group By Source
    # ==========================================================

    def group_by_source(
        self,
        urls,
    ):
        """
        將 URL 依 hostname 分組。

        只保留：

            URL 數量 >=
            self.min_urls_per_source

        的來源。

        Returns:
            dict

        Example:

            {
                "www.digitimes.com.tw": [
                    "...",
                    "...",
                    "..."
                ],

                "www.tsmc.com": [
                    "...",
                    "..."
                ]
            }
        """

        if urls is None:
            return {}

        groups = {}

        for url in urls:

            normalized_url = (
                self.normalize_url(
                    url
                )
            )

            if not normalized_url:
                continue

            host = (
                self.normalize_host(
                    normalized_url
                )
            )

            if not host:
                continue

            if host not in groups:
                groups[host] = []

            if normalized_url not in (
                groups[host]
            ):
                groups[host].append(
                    normalized_url
                )

        filtered_groups = {}

        for host, source_urls in (
            groups.items()
        ):

            if len(source_urls) < (
                self.min_urls_per_source
            ):
                continue

            filtered_groups[
                host
            ] = source_urls

        return filtered_groups

    # ==========================================================
    # Execute
    # ==========================================================

    def execute(
        self,
    ):
        """
        執行完整 URL Source Grouping。

        流程：

            articles
                ↓
            fetch article URLs
                ↓
            targets
                ↓
            fetch crawler URLs
                ↓
            exclude crawler sources
                ↓
            group by source
                ↓
            minimum URL threshold

        Returns:
            dict
        """

        # ------------------------------------------------------
        # Fetch
        # ------------------------------------------------------

        article_urls = (
            self.fetch_article_urls()
        )

        crawler_urls = (
            self.fetch_crawler_urls()
        )

        # ------------------------------------------------------
        # Exclude
        # ------------------------------------------------------

        (
            remaining_urls,
            excluded_urls,
        ) = self.exclude_crawler_urls(
            article_urls=article_urls,
            crawler_urls=crawler_urls,
        )

        # ------------------------------------------------------
        # Group
        # ------------------------------------------------------

        source_groups = (
            self.group_by_source(
                remaining_urls
            )
        )

        # ------------------------------------------------------
        # Return
        #
        # 注意：
        #
        # 這裡不再 print：
        #
        #     SOURCE GROUPS
        #
        # 也不 print source groups 的內容。
        #
        # Gemini Service 仍然可以正常取得：
        #
        #     result["source_groups"]
        #
        # ------------------------------------------------------

        return {
            "article_url_count": len(
                article_urls
            ),
            "crawler_url_count": len(
                crawler_urls
            ),
            "excluded_url_count": len(
                excluded_urls
            ),
            "remaining_url_count": len(
                remaining_urls
            ),
            "source_count": len(
                source_groups
            ),
            "source_groups": source_groups,
        }


# ==============================================================
# Manual Test
# ==============================================================

if __name__ == "__main__":

    service = (
        URLSourceGroupingService()
    )

    result = service.execute()

    print(
        "\n"
        + "=" * 60
    )

    print(
        "URL SOURCE GROUPING"
    )

    print(
        "=" * 60
    )

    print(
        f"Articles URLs: "
        f"{result['article_url_count']}"
    )

    print(
        f"Target crawler URLs: "
        f"{result['crawler_url_count']}"
    )

    print(
        f"Excluded URLs: "
        f"{result['excluded_url_count']}"
    )

    print(
        f"Remaining URLs: "
        f"{result['remaining_url_count']}"
    )

    print(
        f"Candidate sources: "
        f"{result['source_count']}"
    )

    print(
        "\n"
        + "=" * 60
    )