"""
tests/V6_4/test_gemini_url_source_discovery_to_target.py

AutoSearch V6.4

Gemini URL Source Discovery → Target Persistence Test

完整流程：

    articles
        ↓
    URL Source Grouping
        ↓
    排除 targets.crawler_url
        ↓
    Source Groups
        ↓
    Gemini Source Discovery
        ↓
    Gemini Result
        ↓
    targets INSERT / UPDATE
"""

from services.gemini_url_source_discovery_service import (
    GeminiURLSourceDiscoveryService,
)


def test_gemini_url_source_discovery_to_target():
    """
    測試完整：

        URL Source Grouping
            ↓
        Gemini Source Discovery
            ↓
        targets INSERT / UPDATE
    """

    service = (
        GeminiURLSourceDiscoveryService()
    )

    # ==========================================================
    # Step 1
    # ==========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "STEP 1 - URL SOURCE GROUPING"
    )

    print(
        "=" * 60
    )

    grouping_result = (
        service.grouping_service.execute()
    )

    assert isinstance(
        grouping_result,
        dict,
    )

    source_groups = (
        grouping_result.get(
            "source_groups",
            {},
        )
    )

    assert isinstance(
        source_groups,
        dict,
    )

    print(
        f"Articles URLs: "
        f"{grouping_result['article_url_count']}"
    )

    print(
        f"Target crawler URLs: "
        f"{grouping_result['crawler_url_count']}"
    )

    print(
        f"Excluded URLs: "
        f"{grouping_result['excluded_url_count']}"
    )

    print(
        f"Remaining URLs: "
        f"{grouping_result['remaining_url_count']}"
    )

    print(
        f"Candidate sources: "
        f"{grouping_result['source_count']}"
    )

    # ==========================================================
    # Step 2
    # ==========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "STEP 2 - GEMINI SOURCE DISCOVERY"
    )

    print(
        "=" * 60
    )

    results = (
        service.execute(
            source_groups=source_groups
        )
    )

    assert isinstance(
        results,
        list,
    )

    print(
        f"Gemini source count: "
        f"{len(results)}"
    )

    for result in results:

        print(
            f"\n[{result.get('host', '')}]"
        )

        if "error" in result:
            print(
                f"ERROR: "
                f"{result['error']}"
            )

            continue

        print(
            f"name: "
            f"{result.get('name', '')}"
        )

        print(
            f"url: "
            f"{result.get('url', '')}"
        )

        print(
            f"crawler_url: "
            f"{result.get('crawler_url', '')}"
        )

        print(
            f"keyword: "
            f"{result.get('keyword', '')}"
        )

        print(
            f"description: "
            f"{result.get('description', '')}"
        )

    # ==========================================================
    # Step 3
    # ==========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "STEP 3 - SAVE TO TARGETS"
    )

    print(
        "=" * 60
    )

    saved_results = (
        service.save_results_to_targets(
            results
        )
    )

    assert isinstance(
        saved_results,
        list,
    )

    print(
        f"Target persistence count: "
        f"{len(saved_results)}"
    )

    # ==========================================================
    # Persistence Result
    # ==========================================================

    inserted_count = 0
    updated_count = 0
    skipped_count = 0

    for saved in saved_results:

        action = saved.get(
            "action",
            "",
        )

        if action == "inserted":
            inserted_count += 1

        elif action == "updated":
            updated_count += 1

        elif action == "skipped":
            skipped_count += 1

    print(
        f"Inserted: "
        f"{inserted_count}"
    )

    print(
        f"Updated: "
        f"{updated_count}"
    )

    print(
        f"Skipped: "
        f"{skipped_count}"
    )

    # ==========================================================
    # Final
    # ==========================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "COMPLETE FLOW FINISHED"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":

    test_gemini_url_source_discovery_to_target()