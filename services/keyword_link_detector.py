"""
services/keyword_link_detector.py

AutoSearch V5

Keyword Link Detector

用途：

    從已取得的 HTML 中，
    找出與 Keyword 相關的 <a> 連結。

Pipeline:

    HTML
      +
    Processed Keyword
      ↓
    KeywordLinkDetector
      ↓
    Related URLs


責任：

    - HTML Link Extraction
    - Keyword Matching
    - Related URL Detection
    - URL Normalization
    - URL Filtering
    - Duplicate URL Removal
    - SQL URL Priority
    - Random Related URL Selection

不負責：

    - Keyword Processing
    - Keyword Translation
    - Crawler
    - Parser
    - Article
    - Archive
    - Job
    - Search

SQL URL Priority：

    MySQL:
        articles.url

    URL 不存在 SQL：
        優先選取

    URL 已存在 SQL：
        max_results 名額不足時補足
"""

# ==================================================
#
# Imports
#
# ==================================================

import random
import re

from urllib.parse import (
    urljoin,
    urlparse,
)

from bs4 import BeautifulSoup


# ==================================================
#
# Database
#
# ==================================================

from database.connection import (
    get_connection,
)


# ==================================================
#
# Logger
#
# ==================================================

from utils.logger import (
    logger,
)


# ==================================================
#
# Keyword Link Detector
#
# ==================================================

class KeywordLinkDetector:
    """
    Keyword Link Detector。

    將：

        HTML
        +
        Processed Keyword

    轉換成：

        Related URLs

    預設：

        最多回傳 5 個 Related URLs。

    URL Priority：

        SQL 不存在
            ↓
        優先選取

        SQL 已存在
            ↓
        名額不足時補足

    SQL Table：

        articles

    SQL Column：

        url
    """

    # ==================================================
    #
    # URL Filtering Rules
    #
    # ==================================================

    # 明顯屬於廣告、追蹤、點擊跳轉的 URL。
    BLOCKED_PATH_KEYWORDS = {
        "ad",
        "ads",
        "advert",
        "advertisement",
        "banner",
        "click",
        "tracking",
        "track",
        "redirect",
        "goto",
        "go",
        "out",
    }

    # 常見的非內容型頁面。
    BLOCKED_PATH_SEGMENTS = {
        "category",
        "categories",
        "tag",
        "tags",
        "search",
        "archive",
        "archives",
        "author",
        "authors",
        "login",
        "logout",
        "register",
        "account",
        "user",
        "users",
        "subscribe",
        "subscription",
        "contact",
        "about",
        "privacy",
        "terms",
        "sitemap",
    }

    # 常見追蹤 Query。
    BLOCKED_QUERY_KEYS = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "gclid",
        "fbclid",
    }

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        min_match_count=1,
        max_results=5,
    ):
        """
        Parameters
        ----------
        min_match_count :
            最少需要符合幾個 Keyword Term。

        max_results :
            最多回傳多少 Related URLs。

            預設：

                5

            若設定為 None：

                不限制數量。

            注意：

                SQL URL Priority 後，
                再進行 Random Selection。
        """

        self.min_match_count = max(
            1,
            int(min_match_count),
        )

        self.max_results = (
            None
            if max_results is None
            else max(
                1,
                int(max_results),
            )
        )

    # ==================================================
    #
    # Public Detect
    #
    # ==================================================

    def detect(
        self,
        html,
        processed_keyword,
        base_url=None,
    ):
        """
        從 HTML 找出與 Keyword 相關的 URLs。

        Parameters
        ----------
        html :
            原始 HTML。

        processed_keyword :
            KeywordProcessor.process()
            的結果。

        base_url :
            HTML 所屬頁面的 URL。

        Returns
        -------
        list[str]

            Related URLs。

            優先：

                SQL articles.url
                尚未存在的 URL

            再由：

                已存在 SQL 的 URL

            補足 max_results。
        """

        # ==================================================
        #
        # Validation
        #
        # ==================================================

        if not isinstance(
            html,
            str,
        ):
            return []

        if not html.strip():
            return []

        if not isinstance(
            processed_keyword,
            dict,
        ):
            return []

        # ==================================================
        #
        # Get Terms
        #
        # ==================================================

        terms = self._get_terms(
            processed_keyword
        )

        if not terms:
            return []

        # ==================================================
        #
        # Parse HTML
        #
        # ==================================================

        try:

            soup = BeautifulSoup(
                html,
                "html.parser",
            )

        except Exception:

            return []

        # ==================================================
        #
        # Detect Links
        #
        # ==================================================

        candidates = []

        seen_urls = set()

        for anchor in soup.find_all("a"):

            href = anchor.get(
                "href"
            )

            if not href:
                continue

            # ----------------------------------------------
            #
            # Normalize URL
            #
            # ----------------------------------------------

            url = self._normalize_url(
                href,
                base_url,
            )

            if not url:
                continue

            # ----------------------------------------------
            #
            # URL Filter
            #
            # ----------------------------------------------

            if not self._is_candidate_url(
                url
            ):
                continue

            # ----------------------------------------------
            #
            # Duplicate URL
            #
            # ----------------------------------------------

            if url in seen_urls:
                continue

            # ----------------------------------------------
            #
            # Build Search Text
            #
            # ----------------------------------------------

            link_text = anchor.get_text(
                " ",
                strip=True,
            )

            title = anchor.get(
                "title",
                "",
            )

            aria_label = anchor.get(
                "aria-label",
                "",
            )

            search_text = " ".join(
                [
                    link_text,
                    title,
                    aria_label,
                ]
            ).strip()

            if not search_text:
                continue

            # ----------------------------------------------
            #
            # Keyword Match
            #
            # ----------------------------------------------

            match_count = self._match_count(
                search_text,
                terms,
            )

            if match_count < self.min_match_count:
                continue

            seen_urls.add(
                url
            )

            candidates.append(
                url
            )

        # ==================================================
        #
        # No Candidates
        #
        # ==================================================

        if not candidates:
            return []

        # ==================================================
        #
        # SQL URL Priority
        #
        # ==================================================

        existing_url_set = (
            self._get_existing_urls(
                candidates
            )
        )

        new_urls = []
        existing_urls = []

        for url in candidates:

            if url in existing_url_set:

                existing_urls.append(
                    url
                )

            else:

                new_urls.append(
                    url
                )

        # ==================================================
        #
        # Random Selection
        #
        # ==================================================

        # ----------------------------------------------
        #
        # No Limit
        #
        # ----------------------------------------------

        if self.max_results is None:

            random.shuffle(
                new_urls
            )

            random.shuffle(
                existing_urls
            )

            return (
                new_urls
                + existing_urls
            )

        # ----------------------------------------------
        #
        # Prioritize New URLs
        #
        # ----------------------------------------------

        random.shuffle(
            new_urls
        )

        random.shuffle(
            existing_urls
        )

        selected = new_urls[
            :self.max_results
        ]

        remaining = (
            self.max_results
            - len(selected)
        )

        if remaining > 0:

            selected.extend(
                existing_urls[
                    :remaining
                ]
            )

        return selected

    # ==================================================
    #
    # SQL Existing URL Lookup
    #
    # ==================================================

    @staticmethod
    def _get_existing_urls(
        urls,
    ):
        """
        查詢 MySQL articles.url。

        Parameters
        ----------
        urls :
            candidate URL list。

        Returns
        -------
        set[str]

            已存在於：

                articles.url

            的 URL 集合。

        SQL：

            SELECT url
            FROM articles
            WHERE url IN (...)
        """

        if not urls:
            return set()

        conn = None
        cursor = None

        try:

            # --------------------------------------------------
            # Connection
            # --------------------------------------------------

            conn = get_connection()

            if conn is None:

                logger.warning(
                    "SQL connection unavailable "
                    "during Related URL lookup."
                )

                return set()

            # --------------------------------------------------
            # Cursor
            # --------------------------------------------------

            cursor = conn.cursor()

            # --------------------------------------------------
            # Placeholder
            # --------------------------------------------------

            placeholders = ", ".join(
                ["%s"] * len(urls)
            )

            # --------------------------------------------------
            # SQL
            # --------------------------------------------------

            query = f"""
                SELECT url
                FROM articles
                WHERE url IN ({placeholders})
            """

            cursor.execute(
                query,
                tuple(urls),
            )

            rows = cursor.fetchall()

            # --------------------------------------------------
            # Result
            # --------------------------------------------------

            existing_urls = set()

            for row in rows:

                if not row:
                    continue

                url = row[0]

                if url is None:
                    continue

                existing_urls.add(
                    str(url)
                )

            return existing_urls

        except Exception as exc:

            logger.exception(
                "Failed to query existing "
                "Article URLs: "
                f"error={exc}"
            )

            # SQL 查詢失敗：
            #
            # 不阻斷 Related URL Detection。
            #
            # 視為目前沒有確認到
            # 已存在的 URL。
            #
            # 因此全部進入 new_urls。

            return set()

        finally:

            # --------------------------------------------------
            # Close Cursor
            # --------------------------------------------------

            if cursor is not None:

                try:

                    cursor.close()

                except Exception:

                    pass

            # --------------------------------------------------
            # Close Connection
            # --------------------------------------------------

            if conn is not None:

                try:

                    conn.close()

                except Exception:

                    pass

    # ==================================================
    #
    # URL Candidate Filter
    #
    # ==================================================

    @classmethod
    def _is_candidate_url(
        cls,
        url,
    ):
        """
        判斷 URL 是否適合做為 Related URL。

        排除：

            - 廣告
            - Click tracking
            - Redirect
            - Category
            - Search
            - Tag
            - Archive
            - Login / Account
            - Tracking Query
        """

        if not isinstance(
            url,
            str,
        ):
            return False

        try:

            parsed = urlparse(
                url
            )

        except Exception:

            return False

        scheme = (
            parsed.scheme
            or ""
        ).lower()

        if scheme not in {
            "http",
            "https",
        }:
            return False

        if not parsed.netloc:
            return False

        # ==================================================
        #
        # Path
        #
        # ==================================================

        path = (
            parsed.path
            or ""
        ).strip().lower()

        normalized_path = (
            path.strip("/")
        )

        if normalized_path:

            segments = [
                segment.strip()
                for segment in normalized_path.split("/")
                if segment.strip()
            ]

            # ------------------------------------------
            #
            # Blocked Path Segments
            #
            # ------------------------------------------

            for segment in segments:

                if segment in cls.BLOCKED_PATH_SEGMENTS:

                    return False

                # --------------------------------------
                #
                # Advertisement / Tracking
                #
                # --------------------------------------

                for keyword in (
                    cls.BLOCKED_PATH_KEYWORDS
                ):

                    if keyword in segment:

                        return False

        # ==================================================
        #
        # Filename / Endpoint
        #
        # ==================================================

        last_segment = (
            normalized_path.split("/")[-1]
            if normalized_path
            else ""
        )

        blocked_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".svg",
            ".ico",
            ".css",
            ".js",
            ".pdf",
            ".zip",
            ".rar",
        }

        for extension in blocked_extensions:

            if last_segment.endswith(
                extension
            ):

                return False

        # ==================================================
        #
        # Query
        #
        # ==================================================

        query = (
            parsed.query
            or ""
        )

        if query:

            query_lower = (
                query.lower()
            )

            query_keys = set()

            for part in query_lower.split(
                "&"
            ):

                if "=" in part:

                    key = part.split(
                        "=",
                        1,
                    )[0].strip()

                else:

                    key = part.strip()

                if key:

                    query_keys.add(
                        key
                    )

            # ------------------------------------------
            #
            # Tracking Query
            #
            # ------------------------------------------

            if (
                query_keys
                & cls.BLOCKED_QUERY_KEYS
            ):

                return False

            # ------------------------------------------
            #
            # Redirect Query
            #
            # ------------------------------------------

            for blocked_keyword in (
                "redirect=",
                "redir=",
                "returnurl=",
                "return_url=",
                "target=",
                "dest=",
                "destination=",
            ):

                if (
                    blocked_keyword
                    in query_lower
                ):

                    return False

        return True

    # ==================================================
    #
    # Get Terms
    #
    # ==================================================

    @staticmethod
    def _get_terms(
        processed_keyword,
    ):
        """
        從 KeywordProcessor 結果取得 Terms。

        優先使用：

            original_terms
            +
            translated_terms
        """

        terms = []

        original_terms = (
            processed_keyword.get(
                "original_terms",
                [],
            )
        )

        translated_terms = (
            processed_keyword.get(
                "translated_terms",
                [],
            )
        )

        if not isinstance(
            original_terms,
            list,
        ):

            original_terms = []

        if not isinstance(
            translated_terms,
            list,
        ):

            translated_terms = []

        for term in (
            original_terms
            + translated_terms
        ):

            if term is None:
                continue

            term = str(
                term
            ).strip()

            if not term:
                continue

            normalized = (
                term.casefold()
            )

            if normalized not in terms:

                terms.append(
                    normalized
                )

        return terms

    # ==================================================
    #
    # Match Count
    #
    # ==================================================

    @staticmethod
    def _match_count(
        text,
        terms,
    ):
        """
        計算 HTML Link Text
        符合多少 Keyword Terms。

        English / Technical Terms：

            使用 Word Boundary，
            避免短詞被其他單字包含。

        Chinese / Non-word Terms：

            使用 Substring Match。
        """

        normalized_text = (
            str(text)
            .casefold()
        )

        count = 0

        for term in terms:

            term = str(
                term
            ).strip().casefold()

            if not term:
                continue

            # ----------------------------------------------
            #
            # Chinese / Non-word Terms
            #
            # ----------------------------------------------

            if any(
                "\u4e00" <= char <= "\u9fff"
                for char in term
            ):

                if term in normalized_text:

                    count += 1

                continue

            # ----------------------------------------------
            #
            # English / Technical Terms
            #
            # ----------------------------------------------

            pattern = (
                r"(?<![A-Za-z0-9_])"
                + re.escape(term)
                + r"(?![A-Za-z0-9_])"
            )

            if re.search(
                pattern,
                normalized_text,
            ):

                count += 1

        return count

    # ==================================================
    #
    # Normalize URL
    #
    # ==================================================

    @staticmethod
    def _normalize_url(
        href,
        base_url=None,
    ):
        """
        將 href 正規化成可使用 URL。
        """

        if href is None:
            return None

        href = str(
            href
        ).strip()

        if not href:
            return None

        # ----------------------------------------------
        #
        # Ignore Non-Web Links
        #
        # ----------------------------------------------

        lowered = href.lower()

        if lowered.startswith(
            (
                "#",
                "javascript:",
                "mailto:",
                "tel:",
                "data:",
            )
        ):

            return None

        # ----------------------------------------------
        #
        # Resolve Relative URL
        #
        # ----------------------------------------------

        if base_url:

            href = urljoin(
                base_url,
                href,
            )

        # ----------------------------------------------
        #
        # Validate Scheme
        #
        # ----------------------------------------------

        parsed = urlparse(
            href
        )

        if parsed.scheme.lower() not in {
            "http",
            "https",
        }:

            return None

        if not parsed.netloc:

            return None

        # ----------------------------------------------
        #
        # Remove Fragment
        #
        # ----------------------------------------------

        parsed = parsed._replace(
            fragment=""
        )

        return parsed.geturl()


# ==================================================
#
# Convenience API
#
# ==================================================

def detect_related_urls(
    html,
    processed_keyword,
    base_url=None,
    min_match_count=1,
    max_results=5,
):
    """
    Convenience API。

    預設最多隨機回傳 5 個 Related URLs。

    SQL URL Priority：

        articles.url
            ↓
        不存在優先
    """

    detector = KeywordLinkDetector(
        min_match_count=min_match_count,
        max_results=max_results,
    )

    return detector.detect(
        html,
        processed_keyword,
        base_url=base_url,
    )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "KeywordLinkDetector",
    "detect_related_urls",
]