"""
tests/V6_4/test_url_source_grouping_service.py

AutoSearch V6.4

URL Source Grouping Service Test

測試目的：

    articles.url
        ↓
    排除 targets.crawler_url
        ↓
    URL Source Grouping
        ↓
    只輸出 >= 3 個不同 URL 的來源

注意：

本測試目前不使用：

- Gemini
- LLMClient
- AIAnalyzer
- AI Worker

本測試只確認：

SQL
 ↓
URL Filter
 ↓
Source Grouping
 ↓
Final Source Groups
"""


from services.url_source_grouping_service import (
    URLSourceGroupingService,
)


# ==================================================
# TEST
# ==================================================

def test_url_source_grouping():
    """
    測試完整 URL Source Grouping。

    最後只輸出：

        Source
        URL count
        URLs
    """

    service = URLSourceGroupingService()

    result = service.execute()

    assert isinstance(
        result,
        dict,
    )

    source_groups = result.get(
        "source_groups",
        {}
    )

    assert isinstance(
        source_groups,
        dict,
    )

    # ----------------------------------------------
    # Validation
    # ----------------------------------------------

    for host, urls in source_groups.items():

        assert len(urls) >= 3, (
            f"Source {host} has only "
            f"{len(urls)} URLs."
        )

    # ----------------------------------------------
    # Final Output
    # ----------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "FINAL SOURCE GROUPS"
    )

    print(
        "=" * 60
    )

    if not source_groups:

        print(
            "\nNo candidate source found."
        )

    else:

        for host, urls in sorted(
            source_groups.items()
        ):

            print(
                f"\n[{host}]"
            )

            print(
                f"URL count: {len(urls)}"
            )

            for index, url in enumerate(
                urls,
                start=1,
            ):

                print(
                    f"  {index}. {url}"
                )

    print(
        "\n"
        + "=" * 60
    )

    print(
        f"Candidate source count: "
        f"{len(source_groups)}"
    )

    print(
        "=" * 60
    )


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "AutoSearch V6.4 "
        "URL Source Grouping Test"
    )

    print(
        "=" * 60
    )

    test_url_source_grouping()