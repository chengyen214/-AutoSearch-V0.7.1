"""
services/related_crawl_service.py

AutoSearch V5

Related Crawl Service

用途：

    處理由 KeywordLinkDetector
    找出的 Related URLs。

核心 Pipeline：

    Related URL
         ↓
    RelatedCrawlService
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
    CrawlResult
         ↓
    ParserService
         ↓
    Parsed Article
         ↓
    ArticleService
         ↓
    MySQL Article


重要：

    RelatedCrawlService：

        - 不使用 CrawlService.crawl()
        - 不呼叫 CrawlService.crawl()
        - 不回 JobExecutorBridge
        - 自己完成完整 Crawl
        - 自己完成 Parser
        - 自己完成 Article Persistence

    但：

        RelatedCrawlService 與 CrawlService
        共用同一個 CrawlResult Model。


因此 Related Crawl：

    Related URL
         ↓
    RelatedCrawlService
         ↓
    Crawl
         ↓
    Parser
         ↓
    Article


責任：

    - Crawl Related URL
    - 呼叫 crawler.resolve_url()
    - 呼叫 crawler.download()
    - 保留原始 URL
    - 保留 Redirect 後 URL
    - 取得 Raw HTML
    - 計算 Content Hash
    - 取得 CSS / Image Resources
    - 建立 CrawlResult
    - 將 Raw HTML 保存至 MongoDB
    - Parser
    - ArticleService
    - Related Crawl Error Handling
    - 批次 Related URL 處理


不負責：

    - CrawlService.crawl()
    - Job
    - Target Repository
    - Search
    - Search Provider
    - SearchAdapter
    - JobExecutorBridge
    - Archive Business Logic
    - AI Task Management


Parser / Article 傳遞方式：

    CrawlResult
            ↓
    ParserService.parse_crawl_result(
        crawl_result,
        keyword
    )
            ↓
       Parser Result
            ↓
      Extract Article
            ↓
    ArticleService.create(
        article=article,
        html=html
    )


Related Crawl Policy：

    Related Crawl 是獨立 Pipeline。

    Original Crawl：

        CrawlService
             ↓
        CrawlResult
             ↓
        JobExecutorBridge
             ↓
        Parser
             ↓
        Article


    Related Crawl：

        RelatedCrawlService
             ↓
        CrawlResult
             ↓
        ParserService
             ↓
        ArticleService


    兩條 Pipeline：

        - Crawl 流程彼此獨立
        - 不互相取代
        - 共用 CrawlResult Model

"""


# ==================================================
#
# Standard Library
#
# ==================================================

import hashlib


from dataclasses import (
    dataclass,
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
# Crawl Result
#
# ==================================================

from services.crawl_service import (
    CrawlResult,
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
# Parser Service
#
# ==================================================

from services.parser_service import (
    ParserService,
)


# ==================================================
#
# Article Service
#
# ==================================================

from services.article_service import (
    ArticleService,
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
# Related Crawl Result
#
# ==================================================

@dataclass
class RelatedCrawlResult:
    """
    Related Crawl 完整處理結果。

    保存：

        - Related URL
        - CrawlResult
        - Parser Result
        - Article Result
        - Article
        - Status
        - Error
        - Success


    注意：

        crawl_result 使用：

            services.crawl_service.CrawlResult

        與 Original Crawl 共用相同的
        CrawlResult Model。
    """

    # --------------------------------------------------
    # Related URL
    # --------------------------------------------------

    url: str

    # --------------------------------------------------
    # Crawl Result
    # --------------------------------------------------

    crawl_result: Optional[CrawlResult] = None

    # --------------------------------------------------
    # Parser Result
    # --------------------------------------------------

    parser_result: Optional[object] = None

    # --------------------------------------------------
    # Article Service Result
    # --------------------------------------------------

    article_result: Optional[object] = None

    # --------------------------------------------------
    # Article
    # --------------------------------------------------

    article: Optional[object] = None

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    status: str = "pending"

    # --------------------------------------------------
    # Error
    # --------------------------------------------------

    error: Optional[str] = None

    # --------------------------------------------------
    # Success
    # --------------------------------------------------

    success: bool = False

    # ==================================================
    #
    # Properties
    #
    # ==================================================

    @property
    def crawl_success(self):
        """
        判斷 Crawl 是否成功。
        """

        return bool(
            self.crawl_result
            and self.crawl_result.success
        )

    # ==================================================

    @property
    def parser_success(self):
        """
        判斷 Parser 是否成功。
        """

        return (
            self.parser_result is not None
        )

    # ==================================================

    @property
    def article_success(self):
        """
        判斷 Article Persistence 是否成功。
        """

        if self.article_result is None:
            return False

        if isinstance(
            self.article_result,
            dict,
        ):

            status = self.article_result.get(
                "status"
            )

            if status:

                status = str(
                    status
                ).strip().lower()

                return status in (
                    "created",
                    "success",
                    "inserted",
                    "new",
                    "updated",
                )

            article_id = (
                self.article_result.get(
                    "article_id"
                )
            )

            return article_id is not None

        return True


# ==================================================
#
# Related Crawl Service
#
# ==================================================

class RelatedCrawlService:
    """
    V5 Related Crawl Service。

    不使用 CrawlService.crawl()。

    自己完成：

        URL
         ↓
        resolve_url()
         ↓
        download()
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
         ↓
        ParserService
         ↓
        ArticleService


    注意：

        CrawlResult 不再由本檔案自行定義。

        直接共用：

            services.crawl_service.CrawlResult

        確保 ParserService 的：

            isinstance(
                crawl_result,
                CrawlResult
            )

        通過。
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
        parser_service=None,
        article_service=None,
    ):
        """
        建立 RelatedCrawlService。
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

        # --------------------------------------------------
        # Parser Service
        # --------------------------------------------------

        if parser_service is None:

            parser_service = (
                ParserService()
            )

        if not hasattr(
            parser_service,
            "parse_crawl_result",
        ):

            raise TypeError(
                "parser_service must provide "
                "parse_crawl_result()"
            )

        self.parser_service = (
            parser_service
        )

        # --------------------------------------------------
        # Article Service
        # --------------------------------------------------

        if article_service is None:

            article_service = (
                ArticleService()
            )

        if not hasattr(
            article_service,
            "create",
        ):

            raise TypeError(
                "article_service must provide "
                "create()"
            )

        self.article_service = (
            article_service
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
        Crawl 單一 Related URL。

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


        注意：

            回傳：

                services.crawl_service.CrawlResult
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

            resolved_url = (
                normalized_url
            )

            logger.warning(
                "Related URL resolution failed: "
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
                "Related crawl download failed: "
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
                "Related crawl download returned None: "
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
                "Related crawler returned invalid HTML type: "
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
                "Related downloaded HTML is empty: "
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
                "Related content hash generation failed: "
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
                    "Related resource downloader returned "
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

            logger.exception(
                "Related resource download failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

            resources = {
                "css": [],
                "images": [],
            }

        # --------------------------------------------------
        # Create Shared CrawlResult
        # --------------------------------------------------

        result = CrawlResult(

            url=normalized_url,

            resolved_url=resolved_url,

            html=html,

            content_hash=content_hash,

            article_id=None,

            document_id=None,

            resources=resources,

            success=True,

            error=None,

        )

        # --------------------------------------------------
        # Save Raw HTML
        # --------------------------------------------------

        if self.save_raw_html:

            self._save_raw_html(
                result
            )

        return result

    # ==================================================
    #
    # Process
    #
    # ==================================================

    def process(
        self,
        url,
        keyword,
    ):
        """
        完整處理單一 Related URL。

        Pipeline：

            Related URL
                 ↓
              Crawl
                 ↓
            CrawlResult
                 ↓
              Parser
                 ↓
           Parser Result
                 ↓
             Article
                 ↓
          ArticleService
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

            return RelatedCrawlResult(

                url=str(
                    url
                ),

                crawl_result=None,

                parser_result=None,

                article_result=None,

                article=None,

                status="crawl_failed",

                error=str(
                    exc
                ),

                success=False,

            )

        # --------------------------------------------------
        # Validate Keyword
        # --------------------------------------------------

        if keyword is None:

            return RelatedCrawlResult(

                url=normalized_url,

                status="invalid_keyword",

                error=(
                    "keyword cannot be None"
                ),

                success=False,

            )

        keyword = str(
            keyword
        ).strip()

        if not keyword:

            return RelatedCrawlResult(

                url=normalized_url,

                status="invalid_keyword",

                error=(
                    "keyword cannot be empty"
                ),

                success=False,

            )

        # --------------------------------------------------
        # Crawl
        # --------------------------------------------------

        try:

            crawl_result = (
                self.crawl(
                    normalized_url
                )
            )

        except Exception as exc:

            logger.exception(
                "Related crawl failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

            return RelatedCrawlResult(

                url=normalized_url,

                status="crawl_failed",

                error=str(
                    exc
                ),

                success=False,

            )

        # --------------------------------------------------
        # Crawl Failure
        # --------------------------------------------------

        if crawl_result is None:

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=None,

                status="crawl_failed",

                error=(
                    "crawl returned None"
                ),

                success=False,

            )

        if not crawl_result.success:

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=crawl_result,

                status="crawl_failed",

                error=crawl_result.error,

                success=False,

            )

        # --------------------------------------------------
        # Parser
        #
        # 注意：
        #
        # crawl_result 現在是：
        #
        #     services.crawl_service.CrawlResult
        #
        # 因此符合 ParserService 的型別要求。
        # --------------------------------------------------

        try:

            parser_result = (
                self.parser_service
                .parse_crawl_result(

                    crawl_result,

                    keyword,

                )
            )

        except Exception as exc:

            logger.exception(
                "Related parser failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=crawl_result,

                parser_result=None,

                article_result=None,

                article=None,

                status="parser_failed",

                error=str(
                    exc
                ),

                success=False,

            )

        # --------------------------------------------------
        # Parser Failure
        # --------------------------------------------------

        if parser_result is None:

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=crawl_result,

                parser_result=None,

                article_result=None,

                article=None,

                status="parser_failed",

                error=(
                    "parser returned None"
                ),

                success=False,

            )

        # --------------------------------------------------
        # Extract Article
        # --------------------------------------------------

        article = self._extract_article(
            parser_result
        )

        if article is None:

            logger.warning(
                "Related parser result does not contain "
                "an Article object: "
                f"url={normalized_url}"
            )

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=crawl_result,

                parser_result=parser_result,

                article_result=None,

                article=None,

                status="parser_result_invalid",

                error=(
                    "Parser result does not contain "
                    "an Article object"
                ),

                success=False,

            )

        # --------------------------------------------------
        # Extract HTML
        # --------------------------------------------------

        html = self._extract_html(
            crawl_result
        )

        if html is None:

            logger.warning(
                "Related crawl result has no HTML: "
                f"url={normalized_url}"
            )

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=crawl_result,

                parser_result=parser_result,

                article_result=None,

                article=article,

                status="html_missing",

                error=(
                    "Crawl result does not contain "
                    "raw HTML"
                ),

                success=False,

            )

        # --------------------------------------------------
        # ArticleService
        # --------------------------------------------------

        try:

            article_result = (
                self.article_service.create(

                    article=article,

                    html=html,

                )
            )

        except Exception as exc:

            logger.exception(
                "Related ArticleService persistence failed: "
                f"url={normalized_url}, "
                f"error={exc}"
            )

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=crawl_result,

                parser_result=parser_result,

                article_result=None,

                article=article,

                status="article_service_failed",

                error=str(
                    exc
                ),

                success=False,

            )

        # --------------------------------------------------
        # ArticleService Result Validation
        # --------------------------------------------------

        if article_result is None:

            logger.error(
                "Related ArticleService.create "
                "returned None: "
                f"url={normalized_url}"
            )

            return RelatedCrawlResult(

                url=normalized_url,

                crawl_result=crawl_result,

                parser_result=parser_result,

                article_result=None,

                article=article,

                status="article_service_failed",

                error=(
                    "ArticleService.create "
                    "returned None"
                ),

                success=False,

            )

        # --------------------------------------------------
        # Normalize Status
        # --------------------------------------------------

        status = (
            self._normalize_article_status(
                article_result
            )
        )

        success = (
            status in (
                "success",
                "updated",
            )
        )

        logger.info(
            "Related pipeline completed: "
            f"url={normalized_url}, "
            f"status={status.upper()}"
        )

        return RelatedCrawlResult(

            url=normalized_url,

            crawl_result=crawl_result,

            parser_result=parser_result,

            article_result=article_result,

            article=article,

            status=status,

            error=None,

            success=success,

        )

    # ==================================================
    #
    # Process Many
    #
    # ==================================================

    def process_many(
        self,
        urls,
        keyword,
    ):
        """
        批次處理 Related URLs。

        單一 URL 失敗：

            記錄失敗
                ↓
            繼續下一個 URL

        不讓單一 Related Crawl
        中斷整批 Related Crawl。
        """

        if urls is None:

            return []

        results = []

        for url in urls:

            try:

                result = (
                    self.process(

                        url,

                        keyword,

                    )
                )

            except Exception as exc:

                logger.exception(
                    "Unexpected related processing error: "
                    f"url={url}, "
                    f"error={exc}"
                )

                result = RelatedCrawlResult(

                    url=str(
                        url
                    ),

                    status="failed",

                    error=str(
                        exc
                    ),

                    success=False,

                )

            results.append(
                result
            )

        return results

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
        後進行 Related Crawl。

        注意：

            這裡只執行 Crawl，
            不執行 Parser / Article。
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
        從 Target 取得 URL
        後進行 Related Crawl。
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
    # Crawl Many
    #
    # ==================================================

    def crawl_many(
        self,
        urls,
    ):
        """
        Crawl 多個 Related URLs。
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
        將成功 Related CrawlResult
        保存至 RawHTMLRepository。
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
                "Related Raw HTML repository "
                "is not configured."
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
                        "Related CrawlResult saved "
                        "to Raw HTML MongoDB: "
                        f"mongo_id={mongo_id}, "
                        f"url={crawl_result.url}"
                    )

                else:

                    logger.warning(
                        "Related Raw HTML repository "
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

            logger.exception(
                "Related Raw HTML MongoDB save failed: "
                f"url={crawl_result.url}, "
                f"error={exc}"
            )

            return None

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
        判斷 Related Crawl 是否成功。
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
        取得 Raw HTML。
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
        取得 Content Hash。
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
        取得 Resources。
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
    # Extract Article
    #
    # ==================================================

    @staticmethod
    def _extract_article(
        parser_result,
    ):
        """
        參考 JobExecutorBridge
        的 Article Extraction。

        支援：

            dict:
                article
                parsed_article
                result
                document_id

            object:
                article
                parsed_article
                result
                document_id
        """

        if parser_result is None:

            return None

        # --------------------------------------------------
        # Dict
        # --------------------------------------------------

        if isinstance(
            parser_result,
            dict,
        ):

            for key in (
                "article",
                "parsed_article",
                "result",
            ):

                value = (
                    parser_result.get(
                        key
                    )
                )

                if value is not None:

                    return value

            if "document_id" in parser_result:

                return parser_result

            return None

        # --------------------------------------------------
        # Object
        # --------------------------------------------------

        for attribute in (
            "article",
            "parsed_article",
            "result",
        ):

            if hasattr(
                parser_result,
                attribute,
            ):

                value = getattr(
                    parser_result,
                    attribute,
                    None,
                )

                if value is not None:

                    return value

        if hasattr(
            parser_result,
            "document_id",
        ):

            return parser_result

        return None

    # ==================================================
    #
    # Extract HTML
    #
    # ==================================================

    @staticmethod
    def _extract_html(
        crawl_result,
    ):
        """
        參考 JobExecutorBridge
        的 HTML Extraction。
        """

        if crawl_result is None:

            return None

        # --------------------------------------------------
        # Dict
        # --------------------------------------------------

        if isinstance(
            crawl_result,
            dict,
        ):

            for key in (
                "html",
                "raw_html",
                "content",
            ):

                value = (
                    crawl_result.get(
                        key
                    )
                )

                if value is not None:

                    return value

            return None

        # --------------------------------------------------
        # Object
        # --------------------------------------------------

        for attribute in (
            "html",
            "raw_html",
            "content",
        ):

            if hasattr(
                crawl_result,
                attribute,
            ):

                value = getattr(
                    crawl_result,
                    attribute,
                    None,
                )

                if value is not None:

                    return value

        return None

    # ==================================================
    #
    # Normalize Article Status
    #
    # ==================================================

    @staticmethod
    def _normalize_article_status(
        article_result,
    ):
        """
        將 ArticleService 狀態
        統一成 Related Crawl Status。
        """

        if not isinstance(
            article_result,
            dict,
        ):

            return "success"

        status = article_result.get(
            "status"
        )

        if status is None:

            return "other"

        status = str(
            status
        ).strip().lower()

        # --------------------------------------------------
        # New Article
        # --------------------------------------------------

        if status in (
            "created",
            "success",
            "inserted",
            "new",
        ):

            return "success"

        # --------------------------------------------------
        # Updated
        # --------------------------------------------------

        if status in (
            "updated",
            "update",
        ):

            return "updated"

        # --------------------------------------------------
        # Duplicate
        # --------------------------------------------------

        if status in (
            "duplicate",
            "duplicated",
            "archive_duplicate",
        ):

            return "duplicate"

        # --------------------------------------------------
        # Known Failure
        # --------------------------------------------------

        if status in (
            "crawl_failed",
            "parser_failed",
            "parser_result_invalid",
            "html_missing",
            "article_service_failed",
        ):

            return status

        return "other"


# ==================================================
#
# Default Service
#
# ==================================================

default_related_crawl_service = (
    RelatedCrawlService()
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
    使用預設 RelatedCrawlService
    Crawl 單一 Related URL。
    """

    return (
        default_related_crawl_service
        .crawl(
            url
        )
    )


def process(
    url,
    keyword,
):
    """
    使用預設 RelatedCrawlService
    完整處理單一 Related URL。

    Pipeline：

        Crawl
          ↓
        Parser
          ↓
        Article
    """

    return (
        default_related_crawl_service
        .process(

            url,

            keyword,

        )
    )


def process_many(
    urls,
    keyword,
):
    """
    使用預設 RelatedCrawlService
    批次處理 Related URLs。
    """

    return (
        default_related_crawl_service
        .process_many(

            urls,

            keyword,

        )
    )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [

    "CrawlResult",

    "RelatedCrawlResult",

    "RelatedCrawlService",

    "default_related_crawl_service",

    "crawl",

    "process",

    "process_many",

]