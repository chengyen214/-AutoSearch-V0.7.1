"""
services/crawl_service.py

AutoSearch V5

V5.6.x

Crawl Service

用途：

    將 V5 Pipeline 的 URL
    交給底層 crawler.py 執行 HTTP Download。

架構：

    SearchResult / Target
            ↓
        CrawlService
            ↓
        crawler.py
            ↓
        Raw HTML
            ↓
        Content Hash
            ↓
        Resource Download
            ↓
        CrawlResult
            ↓
        RawHTMLRepository
            ↓
        MongoDB
            ↓
        ParserService
            ↓
        ParsedArticle
            ↓
        ArticleService
            ↓
        MySQL Article


Raw HTML MongoDB Structure：

    raw_html
    ├── url
    ├── html
    ├── content_hash
    ├── resolved_url
    ├── article_id
    ├── document_id
    ├── created_at
    ├── updated_at
    │
    └── resources
        ├── css[]
        └── images[]


責任：

    - Crawl URL
    - 呼叫 crawler.download()
    - 呼叫 crawler.download_resources()
    - 保留原始 URL
    - 保留 Redirect 後 URL
    - 取得 Raw HTML
    - 計算 Raw HTML Content Hash
    - 取得 CSS / Image Resources
    - 建立 CrawlResult
    - 將成功 CrawlResult 保存至 MongoDB
    - Crawl Error Handling
    - 基本 URL Validation

不負責：

    - SQL
    - Job
    - Target Repository
    - Search
    - Search Provider
    - SearchAdapter
    - Parser
    - Article
    - ArticleService
    - MongoDB implementation
    - Archive Business Logic
    - Duplicate Detection
    - Archive Version
    - AI
    - AI Task


設計原則：

    crawler.py
        負責：

            URL
             ↓
            HTTP
             ↓
            HTML
             ↓
            Resource Download

    CrawlService
        負責：

            V5 Pipeline
                ↓
            Crawl
                ↓
            Hash
                ↓
            Resources
                ↓
            CrawlResult
                ↓
            Raw HTML Persistence

    RawHTMLRepository
        負責：

            CrawlResult
                ↓
            MongoDB Raw HTML

    ParserService
        負責：

            Raw HTML
                ↓
            Parsed Article


Hash Policy：

    CrawlService
        ↓
    SHA-256(Raw HTML)
        ↓
    CrawlResult.content_hash

    content_hash 是 Raw HTML Content Identity。


MongoDB Metadata Policy：

    Crawl 階段：

        article_id = None
        document_id = None

    Article 建立後：

        RawHTMLRepository.update_metadata()

    補回：

        article_id
        document_id


Repository Save Failure：

    MongoDB 儲存失敗：

        不視為 HTTP Crawl Failure。

    因此：

        CrawlResult.success
            仍代表 HTTP Crawl 是否成功。


Pipeline：

    SearchResult
          ↓
         URL
          ↓
    CrawlService
          ↓
    crawler.resolve_url()
          ↓
    crawler.download()
          ↓
       Raw HTML
          ↓
    SHA-256 Hash
          ↓
    crawler.download_resources()
          ↓
    CSS / Images
          ↓
     CrawlResult
          ↓
    RawHTMLRepository
          ↓
       MongoDB
"""


# ==================================================
#
# Standard Library
#
# ==================================================

import hashlib


from dataclasses import (
    dataclass,
    field,
)


from datetime import (
    datetime,
    timezone,
)


from typing import (
    Optional,
)


# ==================================================
#
# Existing Crawler
#
# ==================================================

from crawler.crawler import (
    download,
    resolve_url,
    download_resources,
)


# ==================================================
#
# Raw HTML Repository
#
# ==================================================

from database.raw_html_repository import (
    RawHTMLRepository,
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
# Crawl Result
#
# ==================================================

@dataclass
class CrawlResult:
    """
    CrawlService 的 Crawl 結果。

    保存：

        - 原始 URL
        - Redirect 後 URL
        - Raw HTML
        - Content Hash
        - Article ID
        - Document ID
        - Resources
        - Success
        - Error
        - Crawl Time

    注意：

        本 Model 不負責：

            MongoDB
            Parser
            Article
            Duplicate Detection
            Archive Version
    """

    # --------------------------------------------------
    # Original URL
    # --------------------------------------------------

    url: str

    # --------------------------------------------------
    # Resolved URL
    # --------------------------------------------------

    resolved_url: Optional[str] = None

    # --------------------------------------------------
    # Raw HTML
    # --------------------------------------------------

    html: Optional[str] = None

    # --------------------------------------------------
    # Raw HTML Content Hash
    # --------------------------------------------------

    content_hash: Optional[str] = None

    # --------------------------------------------------
    # Article ID
    #
    # Crawl 階段尚未建立 Article。
    # 因此預設 None。
    # --------------------------------------------------

    article_id: Optional[int] = None

    # --------------------------------------------------
    # Document ID
    #
    # Crawl 階段尚未建立 Article Document Identity。
    # 因此預設 None。
    # --------------------------------------------------

    document_id: Optional[str] = None

    # --------------------------------------------------
    # Resources
    #
    # {
    #     "css": [],
    #     "images": []
    # }
    # --------------------------------------------------

    resources: dict = field(
        default_factory=lambda: {
            "css": [],
            "images": [],
        }
    )

    # --------------------------------------------------
    # Success
    # --------------------------------------------------

    success: bool = False

    # --------------------------------------------------
    # Error
    # --------------------------------------------------

    error: Optional[str] = None

    # --------------------------------------------------
    # Crawl Time
    # --------------------------------------------------

    crawl_time: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    # ==================================================
    #
    # Properties
    #
    # ==================================================

    @property
    def has_html(self):
        """
        判斷是否成功取得 Raw HTML。
        """

        return bool(
            self.success
            and self.html
        )

    # ==================================================

    @property
    def has_hash(self):
        """
        判斷是否已產生 Content Hash。
        """

        return bool(
            self.content_hash
        )

    # ==================================================

    @property
    def has_resources(self):
        """
        判斷是否存在 Resource。

        注意：

            沒有 Resource
            不代表 Crawl Failure。

        某些 HTML 本身可能沒有
        CSS 或 Image。
        """

        if not self.resources:

            return False

        css = self.resources.get(
            "css",
            [],
        )

        images = self.resources.get(
            "images",
            [],
        )

        return bool(
            css
            or images
        )

    # ==================================================

    @property
    def final_url(self):
        """
        取得最終 URL。

        若沒有 resolved_url，
        則退回原始 URL。
        """

        return (
            self.resolved_url
            or self.url
        )


# ==================================================
#
# Crawl Service
#
# ==================================================

class CrawlService:
    """
    V5 Crawl Service。

    負責：

        URL
         ↓
        crawler.py
         ↓
        Raw HTML
         ↓
        SHA-256
         ↓
        Resources
         ↓
        CrawlResult
         ↓
        RawHTMLRepository
         ↓
        MongoDB

    本 Service 不直接處理：

        SQL
        Parser
        Article
        AI
        Archive Business Logic

    Crawl 階段：

        article_id = None
        document_id = None
    """

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        downloader=None,
        url_resolver=None,
        resource_downloader=None,
        raw_html_repository=None,
        save_raw_html=True,
    ):
        """
        建立 CrawlService。

        Parameters
        ----------

        downloader :

            底層 HTML Downloader。

            預設：

                crawler.download

        url_resolver :

            Redirect URL Resolver。

            預設：

                crawler.resolve_url

        resource_downloader :

            CSS / Image Resource Downloader。

            預設：

                crawler.download_resources

        raw_html_repository :

            Raw HTML Repository。

            預設：

                RawHTMLRepository()

        save_raw_html :

            是否在 Crawl 成功後
            將 Raw HTML 保存至 MongoDB。

            預設 True。
        """

        # --------------------------------------------------
        # Downloader
        # --------------------------------------------------

        if downloader is None:

            downloader = download

        if not callable(
            downloader
        ):

            raise TypeError(
                "downloader must be callable"
            )

        self.downloader = (
            downloader
        )

        # --------------------------------------------------
        # URL Resolver
        # --------------------------------------------------

        if url_resolver is None:

            url_resolver = resolve_url

        if not callable(
            url_resolver
        ):

            raise TypeError(
                "url_resolver must be callable"
            )

        self.url_resolver = (
            url_resolver
        )

        # --------------------------------------------------
        # Resource Downloader
        # --------------------------------------------------

        if resource_downloader is None:

            resource_downloader = (
                download_resources
            )

        if not callable(
            resource_downloader
        ):

            raise TypeError(
                "resource_downloader "
                "must be callable"
            )

        self.resource_downloader = (
            resource_downloader
        )

        # --------------------------------------------------
        # Raw HTML Repository
        # --------------------------------------------------

        if raw_html_repository is None:

            raw_html_repository = (
                RawHTMLRepository()
            )

        self.raw_html_repository = (
            raw_html_repository
        )

        # --------------------------------------------------
        # Save Raw HTML
        # --------------------------------------------------

        self.save_raw_html = bool(
            save_raw_html
        )

    # ==================================================
    #
    # Crawl
    #
    # ==================================================

    def crawl(
        self,
        url,
    ):
        """
        Crawl 單一 URL。

        Pipeline：

            URL
             ↓
            URL Validation
             ↓
            resolve_url()
             ↓
            download()
             ↓
            Raw HTML
             ↓
            SHA-256
             ↓
            download_resources()
             ↓
            CrawlResult
             ↓
            RawHTMLRepository
             ↓
            MongoDB

        Parameters
        ----------

        url : str

            目標網頁 URL。

        Returns
        -------

        CrawlResult
        """

        # --------------------------------------------------
        # Validate URL
        # --------------------------------------------------

        try:

            normalized_url = (
                self.normalize_url(
                    url
                )
            )

        except Exception as exc:

            return CrawlResult(

                url=str(
                    url
                ),

                resolved_url=None,

                html=None,

                content_hash=None,

                article_id=None,

                document_id=None,

                resources={
                    "css": [],
                    "images": [],
                },

                success=False,

                error=str(
                    exc
                ),

            )

        # --------------------------------------------------
        # Resolve URL
        # --------------------------------------------------

        resolved_url = (
            normalized_url
        )

        try:

            resolved_url = (
                self.url_resolver(
                    normalized_url
                )
            )

            resolved_url = (
                self.normalize_url(
                    resolved_url
                )
            )

        except Exception as exc:

            # URL Resolution 失敗時，
            # 保留原始 URL。

            resolved_url = (
                normalized_url
            )

            logger.warning(
                "URL resolution failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

        # --------------------------------------------------
        # Download HTML
        # --------------------------------------------------

        try:

            html = (
                self.downloader(
                    normalized_url
                )
            )

        except Exception as exc:

            logger.exception(
                "Crawl download failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

            return CrawlResult(

                url=normalized_url,

                resolved_url=resolved_url,

                html=None,

                content_hash=None,

                article_id=None,

                document_id=None,

                resources={
                    "css": [],
                    "images": [],
                },

                success=False,

                error=str(
                    exc
                ),

            )

        # --------------------------------------------------
        # Download Failed
        # --------------------------------------------------

        if html is None:

            logger.warning(
                "Crawl download returned None: "
                f"url={normalized_url}"
            )

            return CrawlResult(

                url=normalized_url,

                resolved_url=resolved_url,

                html=None,

                content_hash=None,

                article_id=None,

                document_id=None,

                resources={
                    "css": [],
                    "images": [],
                },

                success=False,

                error=(
                    "Failed to download HTML"
                ),

            )

        # --------------------------------------------------
        # Validate HTML
        # --------------------------------------------------

        if not isinstance(
            html,
            str,
        ):

            logger.error(
                "Crawler returned invalid HTML type: "
                f"url={normalized_url}, "
                f"type={type(html).__name__}"
            )

            return CrawlResult(

                url=normalized_url,

                resolved_url=resolved_url,

                html=None,

                content_hash=None,

                article_id=None,

                document_id=None,

                resources={
                    "css": [],
                    "images": [],
                },

                success=False,

                error=(
                    "Downloader must return "
                    "HTML string or None"
                ),

            )

        # --------------------------------------------------
        # Empty HTML
        # --------------------------------------------------

        if not html.strip():

            logger.warning(
                "Downloaded HTML is empty: "
                f"url={normalized_url}"
            )

            return CrawlResult(

                url=normalized_url,

                resolved_url=resolved_url,

                html=None,

                content_hash=None,

                article_id=None,

                document_id=None,

                resources={
                    "css": [],
                    "images": [],
                },

                success=False,

                error=(
                    "Downloaded HTML is empty"
                ),

            )

        # --------------------------------------------------
        # Generate Content Hash
        # --------------------------------------------------

        try:

            content_hash = (
                self.generate_content_hash(
                    html
                )
            )

        except Exception as exc:

            logger.exception(
                "Content hash generation failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

            return CrawlResult(

                url=normalized_url,

                resolved_url=resolved_url,

                html=html,

                content_hash=None,

                article_id=None,

                document_id=None,

                resources={
                    "css": [],
                    "images": [],
                },

                success=False,

                error=str(
                    exc
                ),

            )

        # --------------------------------------------------
        # Download Resources
        #
        # Resource Download Failure
        # 不應該讓 HTML Crawl Failure。
        #
        # HTML 已成功：
        #
        #     success=True
        #
        # 即使：
        #
        #     CSS = []
        #     Images = []
        # --------------------------------------------------

        resources = {
            "css": [],
            "images": [],
        }

        try:

            resources = (
                self.resource_downloader(

                    html,

                    resolved_url,

                )
            )

            # --------------------------------------------------
            # Resource Result Validation
            # --------------------------------------------------

            if resources is None:

                resources = {
                    "css": [],
                    "images": [],
                }

            elif not isinstance(
                resources,
                dict,
            ):

                logger.warning(
                    "Resource downloader returned "
                    "invalid result type: "
                    f"url={normalized_url}, "
                    f"type={type(resources).__name__}"
                )

                resources = {
                    "css": [],
                    "images": [],
                }

            else:

                resources = {
                    "css": resources.get(
                        "css",
                        [],
                    ),

                    "images": resources.get(
                        "images",
                        [],
                    ),
                }

        except Exception as exc:

            # --------------------------------------------------
            # IMPORTANT
            #
            # Resource Failure
            # 不等於 HTML Crawl Failure。
            # --------------------------------------------------

            logger.exception(
                "Resource download failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

            resources = {
                "css": [],
                "images": [],
            }

        # --------------------------------------------------
        # Create Crawl Result
        # --------------------------------------------------

        result = CrawlResult(

            url=normalized_url,

            resolved_url=resolved_url,

            html=html,

            content_hash=content_hash,

            # Crawl 階段尚未建立 Article
            article_id=None,

            # Crawl 階段尚未建立 Document Identity
            document_id=None,

            resources=resources,

            success=True,

            error=None,

        )

        # --------------------------------------------------
        # Save Raw HTML
        #
        # Crawl 階段：
        #
        #     article_id=None
        #     document_id=None
        #
        # 後續 Article 建立後，
        # 再由 Repository.update_metadata()
        # 補回。
        # --------------------------------------------------

        if self.save_raw_html:

            self._save_raw_html(
                result
            )

        return result

    # ==================================================
    #
    # Generate Content Hash
    #
    # ==================================================

    @staticmethod
    def generate_content_hash(
        html,
    ):
        """
        產生 Raw HTML Content Hash。

        Algorithm：

            SHA-256
        """

        if html is None:

            raise ValueError(
                "html cannot be None"
            )

        if not isinstance(
            html,
            str,
        ):

            html = str(
                html
            )

        return hashlib.sha256(
            html.encode(
                "utf-8"
            )
        ).hexdigest()

    # ==================================================
    #
    # Save Raw HTML
    #
    # ==================================================

    def _save_raw_html(
        self,
        crawl_result,
    ):
        """
        將成功 CrawlResult
        保存至 RawHTMLRepository。

        Pipeline：

            CrawlResult
                 ↓
            save_crawl_result()
                 ↓
              MongoDB

        Crawl 階段：

            article_id=None
            document_id=None

        同時保存：

            resources.css[]
            resources.images[]
        """

        if crawl_result is None:

            return None

        if not crawl_result.success:

            return None

        if not crawl_result.html:

            return None

        if not crawl_result.content_hash:

            return None

        if self.raw_html_repository is None:

            logger.warning(
                "Raw HTML repository is not configured."
            )

            return None

        repository = (
            self.raw_html_repository
        )

        try:

            # --------------------------------------------------
            # Preferred API
            # --------------------------------------------------

            save_crawl_result_method = getattr(

                repository,

                "save_crawl_result",

                None,

            )

            if callable(
                save_crawl_result_method
            ):

                mongo_id = (
                    save_crawl_result_method(
                        crawl_result
                    )
                )

                if mongo_id:

                    logger.info(
                        "CrawlResult saved to "
                        "Raw HTML MongoDB: "
                        f"mongo_id={mongo_id}, "
                        f"url={crawl_result.url}"
                    )

                else:

                    logger.warning(
                        "Raw HTML repository "
                        "did not return MongoDB ID: "
                        f"url={crawl_result.url}"
                    )

                return mongo_id

            # --------------------------------------------------
            # Compatibility API
            # --------------------------------------------------

            save_raw_html_method = getattr(

                repository,

                "save_raw_html",

                None,

            )

            if callable(
                save_raw_html_method
            ):

                return (
                    save_raw_html_method(
                        crawl_result
                    )
                )

            # --------------------------------------------------
            # Generic save() Compatibility
            # --------------------------------------------------

            save_method = getattr(

                repository,

                "save",

                None,

            )

            if callable(
                save_method
            ):

                try:

                    return (
                        save_method(

                            url=(
                                crawl_result.url
                            ),

                            html=(
                                crawl_result.html
                            ),

                            content_hash=(
                                crawl_result.content_hash
                            ),

                            resolved_url=(
                                crawl_result.resolved_url
                            ),

                            article_id=(
                                crawl_result.article_id
                            ),

                            document_id=(
                                crawl_result.document_id
                            ),

                            resources=(
                                crawl_result.resources
                            ),

                        )
                    )

                except TypeError:

                    # Compatibility：
                    # 部分 Repository 可能接受
                    # CrawlResult 作為單一參數。

                    return (
                        save_method(
                            crawl_result
                        )
                    )

            raise TypeError(

                "raw_html_repository must provide "

                "save_crawl_result(), "

                "save_raw_html(), or save()"

            )

        except Exception as exc:

            # --------------------------------------------------
            # IMPORTANT
            #
            # MongoDB Save Failure
            # 不等於 HTTP Crawl Failure。
            # --------------------------------------------------

            logger.exception(
                "Raw HTML MongoDB save failed: "
                f"url={crawl_result.url}, "
                f"error={exc}"
            )

            return None

    # ==================================================
    #
    # Crawl Search Result
    #
    # ==================================================

    def crawl_result(
        self,
        search_result,
    ):
        """
        從 SearchResult 取得 URL
        後進行 Crawl。
        """

        if search_result is None:

            raise ValueError(
                "search_result cannot be None"
            )

        url = getattr(
            search_result,
            "url",
            None,
        )

        if url is None:

            raise ValueError(
                "search_result must "
                "provide url"
            )

        return self.crawl(
            url
        )

    # ==================================================
    #
    # Crawl Target
    #
    # ==================================================

    def crawl_target(
        self,
        target,
    ):
        """
        Direct URL Target Crawl。

        只需要：

            target.url
        """

        if target is None:

            raise ValueError(
                "target cannot be None"
            )

        url = getattr(
            target,
            "url",
            None,
        )

        if url is None:

            raise ValueError(
                "target must provide url"
            )

        return self.crawl(
            url
        )

    # ==================================================
    #
    # Crawl Many URLs
    #
    # ==================================================

    def crawl_many(
        self,
        urls,
    ):
        """
        Crawl 多個 URL。

        不負責：

            URL Deduplication
            Search
            SQL
            Job
        """

        if urls is None:

            return []

        results = []

        for url in urls:

            try:

                result = self.crawl(
                    url
                )

            except Exception as exc:

                result = CrawlResult(

                    url=str(
                        url
                    ),

                    resolved_url=None,

                    html=None,

                    content_hash=None,

                    article_id=None,

                    document_id=None,

                    resources={
                        "css": [],
                        "images": [],
                    },

                    success=False,

                    error=str(
                        exc
                    ),

                )

            results.append(
                result
            )

        return results

    # ==================================================
    #
    # Crawl Search Results
    #
    # ==================================================

    def crawl_search_results(
        self,
        search_results,
    ):
        """
        Crawl 一批 SearchResult。

        Pipeline：

            SearchResult[]
                    ↓
              CrawlService
                    ↓
              CrawlResult[]
                    │
                    ├──→ RawHTMLRepository
                    │          ↓
                    │       MongoDB
                    │
                    └──→ ParserService

        每一個成功的 CrawlResult
        都會在 crawl() 階段
        自動保存至 MongoDB。
        """

        if search_results is None:

            return []

        results = []

        for search_result in search_results:

            try:

                result = (
                    self.crawl_result(
                        search_result
                    )
                )

            except Exception as exc:

                url = getattr(

                    search_result,

                    "url",

                    "",

                )

                result = CrawlResult(

                    url=str(
                        url
                    ),

                    resolved_url=None,

                    html=None,

                    content_hash=None,

                    article_id=None,

                    document_id=None,

                    resources={
                        "css": [],
                        "images": [],
                    },

                    success=False,

                    error=str(
                        exc
                    ),

                )

            results.append(
                result
            )

        return results

    # ==================================================
    #
    # Normalize URL
    #
    # ==================================================

    @staticmethod
    def normalize_url(
        url,
    ):
        """
        Normalize URL。

        目前只做：

            1. None Validation
            2. str Conversion
            3. strip()

        不負責：

            URL Deduplication
            URL Canonicalization
            URL Parsing
            URL Validation Service
        """

        if url is None:

            raise ValueError(
                "url cannot be None"
            )

        url = str(
            url
        ).strip()

        if not url:

            raise ValueError(
                "url cannot be empty"
            )

        return url

    # ==================================================
    #
    # Is Success
    #
    # ==================================================

    @staticmethod
    def is_success(
        crawl_result,
    ):
        """
        判斷 Crawl 是否成功。
        """

        if not isinstance(
            crawl_result,
            CrawlResult,
        ):

            return False

        return (
            crawl_result.success
            and crawl_result.has_html
            and crawl_result.has_hash
        )

    # ==================================================
    #
    # Get HTML
    #
    # ==================================================

    @staticmethod
    def get_html(
        crawl_result,
    ):
        """
        從 CrawlResult 取得 Raw HTML。

        只有成功 Crawl
        才允許取得 HTML。
        """

        if not isinstance(
            crawl_result,
            CrawlResult,
        ):

            raise TypeError(
                "crawl_result must be "
                "a CrawlResult"
            )

        if not crawl_result.success:

            raise ValueError(
                "crawl did not succeed"
            )

        if crawl_result.html is None:

            raise ValueError(
                "crawl result has no html"
            )

        return crawl_result.html

    # ==================================================
    #
    # Get Content Hash
    #
    # ==================================================

    @staticmethod
    def get_content_hash(
        crawl_result,
    ):
        """
        從 CrawlResult 取得 Content Hash。

        只有成功 Crawl
        才允許取得 Hash。
        """

        if not isinstance(
            crawl_result,
            CrawlResult,
        ):

            raise TypeError(
                "crawl_result must be "
                "a CrawlResult"
            )

        if not crawl_result.success:

            raise ValueError(
                "crawl did not succeed"
            )

        if not crawl_result.content_hash:

            raise ValueError(
                "crawl result has no content_hash"
            )

        return crawl_result.content_hash

    # ==================================================
    #
    # Get Resources
    #
    # ==================================================

    @staticmethod
    def get_resources(
        crawl_result,
    ):
        """
        從 CrawlResult 取得 Resources。

        Returns：

            {
                "css": [],
                "images": []
            }
        """

        if not isinstance(
            crawl_result,
            CrawlResult,
        ):

            raise TypeError(
                "crawl_result must be "
                "a CrawlResult"
            )

        if not crawl_result.success:

            raise ValueError(
                "crawl did not succeed"
            )

        resources = (
            crawl_result.resources
        )

        if resources is None:

            return {
                "css": [],
                "images": [],
            }

        return resources


# ==================================================
#
# Default Service
#
# ==================================================

default_crawl_service = (
    CrawlService()
)


# ==================================================
#
# Convenience API
#
# ==================================================

def crawl(
    url,
):
    """
    使用預設 CrawlService
    Crawl 單一 URL。

    Crawl 成功後：

        Raw HTML
            +
        Resources
            ↓
        MongoDB
    """

    return (
        default_crawl_service.crawl(
            url
        )
    )


def crawl_search_result(
    search_result,
):
    """
    使用預設 CrawlService
    Crawl 單一 SearchResult。
    """

    return (
        default_crawl_service
        .crawl_result(
            search_result
        )
    )


def crawl_target(
    target,
):
    """
    使用預設 CrawlService
    Crawl Direct URL Target。
    """

    return (
        default_crawl_service
        .crawl_target(
            target
        )
    )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [

    "CrawlResult",

    "CrawlService",

    "default_crawl_service",

    "crawl",

    "crawl_search_result",

    "crawl_target",

]