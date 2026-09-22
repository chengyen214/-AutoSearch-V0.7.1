"""
tests/V7_7/test_real_crawl_service_related.py

AutoSearch V7.7

使用 CrawlService 實際抓取真實網站，
確認：

    CrawlService
        ↓
    KeywordProcessor
        ↓
    KeywordLinkDetector
        ↓
    SQL articles.url
        ↓
    Related URLs
        ↓
    RelatedCrawlService

注意：

    這不是 mock test。

    會真正執行 CrawlService 的下載流程，
    並由 CrawlService 直接啟動
    RelatedCrawlService。

    related_urls 不存在 CrawlResult 裡。

    CrawlResult 只代表 Original Crawl。

    resources 只顯示摘要，
    不直接印出 image/css binary data。
"""

from services.crawl_service import CrawlService


TEST_URL = (
    "https://www.digitimes.com.tw/"
    "tech/industries/?CnlID=1&cat=40"
)

KEYWORD = "半導體"


# ==================================================
#
# Resource Summary
#
# ==================================================

def print_resource_summary(
    resources,
):
    """
    只輸出 resources 摘要，
    避免直接印出 image/css binary data。
    """

    print()
    print("=" * 70)
    print("RESOURCE SUMMARY")
    print("=" * 70)

    if not resources:
        print("No resources.")
        print("=" * 70)
        return

    # --------------------------------------------------
    #
    # Dictionary Resources
    #
    # --------------------------------------------------

    if isinstance(
        resources,
        dict,
    ):

        for key, value in resources.items():

            if value is None:
                print(f"{key}: 0")
                continue

            if isinstance(
                value,
                (list, tuple),
            ):

                print(
                    f"{key}: {len(value)}"
                )

                # ------------------------------------------
                # 只列出最多 10 筆摘要
                # ------------------------------------------

                for index, item in enumerate(
                    value[:10],
                    start=1,
                ):

                    if isinstance(
                        item,
                        dict,
                    ):

                        url = item.get(
                            "url",
                            "",
                        )

                        mime_type = item.get(
                            "mime_type",
                            "",
                        )

                        file_size = item.get(
                            "file_size",
                            "",
                        )

                        print(
                            f"  {index}. "
                            f"url={url} "
                            f"mime={mime_type} "
                            f"size={file_size}"
                        )

                    elif isinstance(
                        item,
                        str,
                    ):

                        print(
                            f"  {index}. {item}"
                        )

                    else:

                        print(
                            f"  {index}. "
                            f"type="
                            f"{type(item).__name__}"
                        )

                if len(value) > 10:

                    print(
                        f"  ... "
                        f"({len(value) - 10} more)"
                    )

                continue

            print(
                f"{key}: "
                f"{type(value).__name__}"
            )

        print("=" * 70)
        return

    # --------------------------------------------------
    #
    # Unexpected Resource Type
    #
    # --------------------------------------------------

    print(
        f"type: {type(resources).__name__}"
    )

    print("=" * 70)


# ==================================================
#
# Main
#
# ==================================================

def main():

    print("=" * 70)
    print("REAL CrawlService + RelatedCrawlService TEST")
    print("=" * 70)

    print(
        f"URL     : {TEST_URL}"
    )

    print(
        f"Keyword : {KEYWORD}"
    )

    print()

    # --------------------------------------------------
    #
    # Create CrawlService
    #
    # --------------------------------------------------

    # 不再傳入 related_url_handler。
    #
    # CrawlService 會在 runtime：
    #
    #     Related URLs
    #          ↓
    #     RelatedCrawlService
    #
    # 使用 Lazy Import 避免 circular import。

    service = CrawlService()

    print(
        "[1] Start CrawlService.crawl()"
    )

    print()

    # --------------------------------------------------
    #
    # Crawl
    #
    # --------------------------------------------------

    result = service.crawl(
        TEST_URL,
        keyword=KEYWORD,
        target_language="en",
    )

    # --------------------------------------------------
    #
    # Crawl Result
    #
    # --------------------------------------------------

    print()
    print("=" * 70)
    print("ORIGINAL CRAWL RESULT")
    print("=" * 70)

    print(
        f"success       : {result.success}"
    )

    print(
        f"url           : {result.url}"
    )

    print(
        f"resolved_url  : {result.resolved_url}"
    )

    print(
        "html length   : "
        f"{len(result.html) if result.html else 0}"
    )

    print(
        f"content_hash  : {result.content_hash}"
    )

    print(
        f"error         : {result.error}"
    )

    # --------------------------------------------------
    #
    # Architecture Check
    #
    # --------------------------------------------------

    print()

    print(
        "has related_urls      : "
        f"{hasattr(result, 'related_urls')}"
    )

    print(
        "has related_results   : "
        f"{hasattr(result, 'related_results')}"
    )

    print("=" * 70)

    # --------------------------------------------------
    #
    # Resource Summary
    #
    # --------------------------------------------------

    print_resource_summary(
        result.resources
    )

    # --------------------------------------------------
    #
    # Final Status
    #
    # --------------------------------------------------

    print()

    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    if result.success:

        print(
            "Original Crawl : SUCCESS"
        )

    else:

        print(
            "Original Crawl : FAILED"
        )

    print(
        "Related Crawl  : "
        "Triggered by CrawlService "
        "when related URLs were detected"
    )

    print(
        "CrawlResult    : Original Crawl only"
    )

    print("=" * 70)


# ==================================================
#
# Entry Point
#
# ==================================================

if __name__ == "__main__":
    main()