"""
tests/V7_7/test_real_google_news_provider.py

AutoSearch V7.7

GoogleNewsProvider Real Integration Test

用途：

    使用目前正式 GoogleNewsProvider
    真實搜尋 Google News。

測試 Keyword：

    IC semiconductor

測試流程：

    IC semiconductor
        ↓
    GoogleNewsProvider
        ↓
    Google News RSS
        ↓
    when:7d
        ↓
    30 Candidate Results
        ↓
    Target crawler_url exclusion
        ↓
    articles.url Database Priority
        ↓
    最多 10 筆
"""


from __future__ import annotations


from search.google_news_provider import (
    GoogleNewsProvider,
)


# ==================================================
#
# Configuration
#
# ==================================================

KEYWORD = "IC semiconductor"


# ==================================================
#
# Main
#
# ==================================================

def main():

    print("=" * 80)
    print("REAL GoogleNewsProvider TEST")
    print("=" * 80)

    print(
        f"Keyword        : {KEYWORD}"
    )

    print(
        "Time Range     : when:7d"
    )

    print(
        "Candidate Limit: 30"
    )

    print(
        "Result Limit   : 10"
    )

    print("=" * 80)
    print()

    # --------------------------------------------------
    # Create Provider
    # --------------------------------------------------

    provider = GoogleNewsProvider()

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    print(
        "[1] Start GoogleNewsProvider.search()"
    )

    print()

    results = provider.search(
        KEYWORD
    )

    # --------------------------------------------------
    # Result Validation
    # --------------------------------------------------

    print("=" * 80)
    print("SEARCH RESULT")
    print("=" * 80)

    print(
        f"Returned Results: {len(results)}"
    )

    print(
        f"Maximum Allowed : {provider.max_results}"
    )

    print()

    # --------------------------------------------------
    # Result Count Check
    # --------------------------------------------------

    if len(results) > provider.max_results:

        print(
            "ERROR: Result count exceeded "
            "Provider max_results."
        )

        print("=" * 80)

        return 1

    if not results:

        print(
            "No Google News results returned."
        )

        print("=" * 80)

        return 0

    # --------------------------------------------------
    # Database Classification
    #
    # 使用 Provider 真實 SQL lookup，
    # 但這裡直接再查一次只是為了輸出統計。
    # 不改 Provider 行為。
    # --------------------------------------------------

    result_urls = [
        item.url
        for item in results
        if getattr(item, "url", None)
    ]

    existing_urls = (
        provider._get_existing_urls(
            result_urls
        )
    )

    new_count = 0
    existing_count = 0

    # --------------------------------------------------
    # Print Results
    # --------------------------------------------------

    for index, item in enumerate(
        results,
        start=1,
    ):

        url = getattr(
            item,
            "url",
            "",
        )

        title = getattr(
            item,
            "title",
            "",
        )

        rank = getattr(
            item,
            "rank",
            index,
        )

        if url in existing_urls:

            database_status = "EXISTING"

            existing_count += 1

        else:

            database_status = "NEW"

            new_count += 1

        print(
            f"[{index:02d}] "
            f"rank={rank:<3} "
            f"db={database_status:<9} "
            f"title={title}"
        )

        print(
            f"     URL: {url}"
        )

        print()

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(
        f"Keyword          : {KEYWORD}"
    )

    print(
        "Google News Query: "
        f"{KEYWORD} when:7d"
    )

    print(
        f"Candidate Limit  : {provider.candidate_results}"
    )

    print(
        f"Final Limit      : {provider.max_results}"
    )

    print(
        f"Returned         : {len(results)}"
    )

    print(
        f"NEW URLs         : {new_count}"
    )

    print(
        f"EXISTING URLs    : {existing_count}"
    )

    print(
        f"Total Classified : "
        f"{new_count + existing_count}"
    )

    print("=" * 80)

    # --------------------------------------------------
    # Final Checks
    # --------------------------------------------------

    print()

    if len(results) <= 10:

        print(
            "Result Limit     : PASS"
        )

    else:

        print(
            "Result Limit     : FAIL"
        )

        return 1

    if new_count > 0:

        print(
            "Database Priority: NEW URLs detected"
        )

    else:

        print(
            "Database Priority: "
            "No NEW URL in final result"
        )

    print(
        "Real Google News : PASS"
    )

    print("=" * 80)

    return 0


# ==================================================
#
# Entry Point
#
# ==================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )