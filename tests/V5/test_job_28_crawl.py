"""
tests/V5/test_job_28_crawl.py

AutoSearch V5

V5.6.3
Job #28 Crawl Test

用途：

    測試指定 Job #28 是否可以：

        SQL
          ↓
        Job #28
          ↓
        target_id
          ↓
        Target #18
          ↓
        Direct URL
          ↓
        CrawlService
          ↓
        CrawlResult

本測試不負責：

    - Search
    - SearchAdapter
    - SearchExecutionBridge
    - Parser
    - Article
    - Archive
    - AI
"""


# ==================================================
#
# Database
#
# ==================================================

from database.job_repository import JobRepository


# ==================================================
#
# Batch Target Service
#
# ==================================================

from services.batch_target_service import (
    BatchTargetService,
)


# ==================================================
#
# Crawl Service
#
# ==================================================

from services.crawl_service import (
    CrawlService,
)


def main():

    print("=" * 70)
    print("AutoSearch V5")
    print("V5.6.3 Job #28 Crawl Test")
    print("=" * 70)

    # ==================================================
    #
    # 1. 取得 Job #28
    #
    # ==================================================

    print()
    print("[1] 從 SQL 取得 Job #28")
    print("-" * 70)

    job_repository = JobRepository()

    job = job_repository.get_by_id(28)

    if job is None:

        print("❌ 找不到 Job #28")

        print()
        print("請確認 SQL jobs table 是否存在 id = 28 的 Job。")

        return

    print(f"Job #28")
    print(f"  job.id        = {job.id}")
    print(f"  job.target_id = {job.target_id}")
    print(f"  job.status    = {job.status}")

    # ==================================================
    #
    # 2. Job → Target
    #
    # ==================================================

    print()
    print("[2] Job #28 → Target")
    print("-" * 70)

    target_service = BatchTargetService()

    target = (
        target_service
        .get_target_for_job(job)
    )

    if target is None:

        print("❌ 找不到 Job #28 對應的 Target")

        return

    print("✅ Target retrieved")

    print(f"  target.id            = {target.id}")
    print(f"  target.name          = {target.name}")
    print(f"  target_type          = {target.target_type}")
    print(f"  target.url           = {target.url}")
    print(f"  target.keyword       = {target.keyword}")
    print(
        f"  target.search_provider = "
        f"{target.search_provider}"
    )

    # ==================================================
    #
    # 3. Target Validation
    #
    # ==================================================

    print()
    print("[3] Target Check")
    print("-" * 70)

    if target.target_type != "url":

        print(
            "❌ Job #28 不是 URL Target"
        )

        print(
            f"   target_type = "
            f"{target.target_type}"
        )

        return

    if not target.url:

        print("❌ Target URL 是空的")

        return

    print("✅ Direct URL Target")

    print(f"  URL = {target.url}")

    # ==================================================
    #
    # 4. 建立 CrawlService
    #
    # ==================================================

    print()
    print("[4] 建立 CrawlService")
    print("-" * 70)

    crawler = CrawlService()

    print("✅ CrawlService ready")

    # ==================================================
    #
    # 5. Crawl
    #
    # ==================================================

    print()
    print("[5] 執行 Crawl")
    print("-" * 70)

    print()
    print(f"▶ Crawl URL:")
    print(f"  {target.url}")

    try:

        result = crawler.crawl(
            target.url
        )

    except Exception as exc:

        print()
        print("❌ Crawl Exception")
        print(f"  {type(exc).__name__}: {exc}")

        return

    # ==================================================
    #
    # 6. Crawl Result
    #
    # ==================================================

    print()
    print("[6] Crawl Result")
    print("-" * 70)

    if result is None:

        print("❌ CrawlResult = None")

        return

    print("✅ CrawlResult retrieved")

    print()
    print(f"  result type = {type(result).__name__}")

    # --------------------------------------------------
    # 常見 CrawlResult 欄位
    # --------------------------------------------------

    for field in (
        "url",
        "status_code",
        "content",
        "html",
        "success",
        "error",
    ):

        if hasattr(result, field):

            value = getattr(
                result,
                field,
            )

            if field in (
                "content",
                "html",
            ):

                if value is None:

                    print(
                        f"  {field:<12} = None"
                    )

                else:

                    print(
                        f"  {field:<12} = "
                        f"{len(value)} chars"
                    )

            else:

                print(
                    f"  {field:<12} = {value}"
                )

    # ==================================================
    #
    # 7. HTML Check
    #
    # ==================================================

    print()
    print("[7] HTML Check")
    print("-" * 70)

    html = None

    if hasattr(
        result,
        "content",
    ):

        html = result.content

    elif hasattr(
        result,
        "html",
    ):

        html = result.html

    if html:

        print("✅ HTML successfully retrieved")

        print(
            f"  HTML length = "
            f"{len(html)}"
        )

        print()
        print("HTML Preview")
        print("-" * 70)

        preview = html[:500]

        print(preview)

    else:

        print("❌ HTML is empty")

    # ==================================================
    #
    # Finished
    #
    # ==================================================

    print()
    print("=" * 70)
    print("Job #28 Crawl Test Finished")
    print("=" * 70)


if __name__ == "__main__":

    main()