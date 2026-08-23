"""
services/parser_service.py

AutoSearch V5

V5 Parser Service

用途：

    將 CrawlService 產生的 CrawlResult
    交給既有 parser/parser.py
    執行 HTML Parsing 與 Article 建立。

Pipeline：

    CrawlResult
        |
        v
    ParserService
        |
        v
    parser.parse()
        |
        v
    Article
        |
        v
    ArticleService

本 Service 負責：

    - 接收 CrawlResult
    - 驗證 CrawlResult
    - 取得 Raw HTML
    - 取得 URL
    - 接收 Keyword
    - 呼叫 parser.parse()
    - 建立 Article
    - Batch Parse
    - Parser Error Handling

本 Service 不負責：

    - Search
    - Search Provider
    - SearchAdapter
    - Crawl
    - HTTP Download
    - MongoDB
    - MySQL
    - ArticleRepository
    - Archive
    - AI
    - Job
    - Scheduler
    - Duplicate Detection


V5 Pipeline：

    SearchResult[]
          |
          v
    CrawlService
          |
          v
    CrawlResult[]
          |
          v
    ParserService
          |
          v
    parser.parse()
          |
          v
       Article[]
          |
          v
    ArticleService
          |
          v
       MySQL


單筆 Pipeline：

    CrawlResult
        |
        +-- html
        +-- url
        +-- resolved_url
        +-- content_hash
        |
        v
    ParserService.parse()
        |
        v
      Article


重要：

    parser/parser.py
    是底層 Parser Engine。

    ParserService
    是 V5 Pipeline Service Boundary。

    ParserService 不重新實作：

        BeautifulSoup
        Noise Removal
        Content Scoring
        Main Content Detection
        Cleaner
        Extractor

    上述功能全部由：

        parser.parser.parse()

    負責。
"""


# ==================================================
#
# Project Parser
#
# ==================================================

from parser.parser import (
    parse,
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
# Parser Service
#
# ==================================================

class ParserService:
    """
    V5 Parser Service。

    負責：

        CrawlResult
            ↓
        parser.parse()
            ↓
        Article

    本 Service 是：

        CrawlService
              ↓
        ParserService
              ↓
        ArticleService

    之間的 Pipeline Boundary。

    不負責：

        MongoDB
        MySQL
        Archive
        AI
        Crawl
    """

    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        parser=None,
    ):
        """
        建立 ParserService。

        Parameters
        ----------

        parser :

            底層 Parser Function。

            預設：

                parser.parser.parse

            支援注入自訂 Parser，
            方便測試與未來擴充。
        """

        # ----------------------------------------------
        # Parser
        # ----------------------------------------------

        if parser is None:

            parser = parse

        if not callable(
            parser
        ):

            raise TypeError(
                "parser must be callable"
            )

        self.parser = (
            parser
        )

    # ==================================================
    #
    # Parse Crawl Result
    #
    # ==================================================

    def parse_crawl_result(
        self,
        crawl_result,
        keyword,
    ):
        """
        將單一 CrawlResult
        交給底層 Parser。

        Pipeline：

            CrawlResult
                |
                v
            ParserService
                |
                v
            parser.parse()
                |
                v
              Article

        Parameters
        ----------

        crawl_result :

            CrawlService.CrawlResult。

        keyword :

            本次搜尋 Keyword。

            目前 parser/parser.py
            要求 keyword 必須提供。

        Returns
        -------

        Article

        Raises
        ------

        ValueError
            CrawlResult 無效或 Crawl 失敗。

        """

        # ==================================================
        # Validate CrawlResult
        # ==================================================

        if crawl_result is None:

            raise ValueError(
                "crawl_result cannot be None"
            )

        # ==================================================
        # Validate Type
        # ==================================================

        if not isinstance(
            crawl_result,
            CrawlResult,
        ):

            raise TypeError(
                "crawl_result must be "
                "a CrawlResult"
            )

        # ==================================================
        # Validate Crawl Success
        # ==================================================

        if not crawl_result.success:

            raise ValueError(
                "cannot parse unsuccessful crawl result"
            )

        # ==================================================
        # Validate HTML
        # ==================================================

        html = (
            crawl_result.html
        )

        if html is None:

            raise ValueError(
                "crawl_result has no html"
            )

        if not str(
            html
        ).strip():

            raise ValueError(
                "crawl_result html is empty"
            )

        # ==================================================
        # Validate Keyword
        # ==================================================

        if keyword is None:

            raise ValueError(
                "keyword cannot be None"
            )

        keyword = str(
            keyword
        ).strip()

        if not keyword:

            raise ValueError(
                "keyword cannot be empty"
            )

        # ==================================================
        # Resolve URL
        # ==================================================

        url = (
            crawl_result.resolved_url
            or crawl_result.url
            or ""
        )

        url = str(
            url
        ).strip()

        # ==================================================
        # Parse
        # ==================================================

        article = (
            self.parser(
                html,
                keyword,
                url=url,
            )
        )

        # ==================================================
        # Validate Article
        # ==================================================

        if article is None:

            raise ValueError(
                "parser returned None"
            )

        return article

    # ==================================================
    #
    # Parse Crawl Result Safely
    #
    # ==================================================

    def try_parse_crawl_result(
        self,
        crawl_result,
        keyword,
    ):
        """
        安全解析單一 CrawlResult。

        Parser 發生錯誤時：

            不讓整個 Batch Pipeline 中斷。

        Returns
        -------

        Article
            成功。

        None
            失敗。
        """

        try:

            return (
                self.parse_crawl_result(
                    crawl_result,
                    keyword,
                )
            )

        except Exception:

            return None

    # ==================================================
    #
    # Parse Many Crawl Results
    #
    # ==================================================

    def parse_crawl_results(
        self,
        crawl_results,
        keyword,
    ):
        """
        批次解析 CrawlResult[]。

        Pipeline：

            CrawlResult[]
                  |
                  v
            ParserService
                  |
                  v
              Article[]

        注意：

            失敗的 CrawlResult
            不會送進 Parser。

            單筆 Parser 失敗
            不會讓其他文章停止。

        Returns
        -------

        list

            成功解析的 Article。
        """

        if crawl_results is None:

            return []

        results = []

        for crawl_result in crawl_results:

            try:

                article = (
                    self.parse_crawl_result(
                        crawl_result,
                        keyword,
                    )
                )

            except Exception:

                continue

            if article is not None:

                results.append(
                    article
                )

        return results

    # ==================================================
    #
    # Parse Many Crawl Results
    # With Failure Details
    #
    # ==================================================

    def parse_crawl_results_detailed(
        self,
        crawl_results,
        keyword,
    ):
        """
        批次解析 CrawlResult[]，
        同時保留成功與失敗結果。

        Returns
        -------

        dict

            {
                "articles": [...],
                "failed": [...],
                "total": int,
                "success": int,
                "failed_count": int,
            }

        failed：

            [
                {
                    "crawl_result": CrawlResult,
                    "error": Exception,
                }
            ]
        """

        if crawl_results is None:

            crawl_results = []

        articles = []

        failed = []

        for crawl_result in crawl_results:

            try:

                article = (
                    self.parse_crawl_result(
                        crawl_result,
                        keyword,
                    )
                )

                if article is not None:

                    articles.append(
                        article
                    )

            except Exception as exc:

                failed.append(
                    {
                        "crawl_result":
                            crawl_result,

                        "error":
                            exc,
                    }
                )

        return {

            "articles":
                articles,

            "failed":
                failed,

            "total":
                len(
                    crawl_results
                ),

            "success":
                len(
                    articles
                ),

            "failed_count":
                len(
                    failed
                ),

        }

    # ==================================================
    #
    # Parse HTML Directly
    #
    # ==================================================

    def parse_html(
        self,
        html,
        keyword,
        url="",
    ):
        """
        直接解析 HTML。

        此方法提供給：

            測試
            特殊 Pipeline
            未建立 CrawlResult 的情況

        正式 V5 Pipeline
        建議使用：

            parse_crawl_result()
        """

        # ==================================================
        # Validate HTML
        # ==================================================

        if html is None:

            raise ValueError(
                "html cannot be None"
            )

        if not str(
            html
        ).strip():

            raise ValueError(
                "html cannot be empty"
            )

        # ==================================================
        # Validate Keyword
        # ==================================================

        if keyword is None:

            raise ValueError(
                "keyword cannot be None"
            )

        keyword = str(
            keyword
        ).strip()

        if not keyword:

            raise ValueError(
                "keyword cannot be empty"
            )

        # ==================================================
        # Normalize URL
        # ==================================================

        if url is None:

            url = ""

        url = str(
            url
        ).strip()

        # ==================================================
        # Parser
        # ==================================================

        return (
            self.parser(
                html,
                keyword,
                url=url,
            )
        )

    # ==================================================
    #
    # Is Parseable
    #
    # ==================================================

    @staticmethod
    def is_parseable(
        crawl_result,
    ):
        """
        判斷 CrawlResult
        是否可以進入 Parser。
        """

        if not isinstance(
            crawl_result,
            CrawlResult,
        ):

            return False

        if not crawl_result.success:

            return False

        if not crawl_result.html:

            return False

        if not str(
            crawl_result.html
        ).strip():

            return False

        return True

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
        取得 CrawlResult Raw HTML。
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
                "crawl_result has no html"
            )

        return crawl_result.html

    # ==================================================
    #
    # Get URL
    #
    # ==================================================

    @staticmethod
    def get_url(
        crawl_result,
    ):
        """
        取得 Parser 使用的 URL。

        優先：

            resolved_url

        fallback：

            url
        """

        if not isinstance(
            crawl_result,
            CrawlResult,
        ):

            raise TypeError(
                "crawl_result must be "
                "a CrawlResult"
            )

        return (
            crawl_result.resolved_url
            or crawl_result.url
            or ""
        )


# ==================================================
#
# Default Service
#
# ==================================================

default_parser_service = (
    ParserService()
)


# ==================================================
#
# Convenience API
#
# ==================================================

def parse_crawl_result(
    crawl_result,
    keyword,
):
    """
    使用預設 ParserService
    解析單一 CrawlResult。
    """

    return (
        default_parser_service
        .parse_crawl_result(
            crawl_result,
            keyword,
        )
    )


def parse_crawl_results(
    crawl_results,
    keyword,
):
    """
    使用預設 ParserService
    批次解析 CrawlResult[]。
    """

    return (
        default_parser_service
        .parse_crawl_results(
            crawl_results,
            keyword,
        )
    )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [

    "ParserService",

    "default_parser_service",

    "parse_crawl_result",

    "parse_crawl_results",

]