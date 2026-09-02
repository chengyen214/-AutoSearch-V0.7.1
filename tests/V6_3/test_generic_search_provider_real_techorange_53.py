"""
tests/V6_3/test_generic_search_provider_real_techorange_53.py

AutoSearch V5

P5.6.3

Generic Search Provider Real Target Test

Target 53:

    Name:
        TechOrange

    Target URL:
        https://techorange.com/author/industry-update/

    Crawler URL:
        https://techorange.com/

    Keyword:
        IC semiconductor

    Search Provider:
        google_search

    Status:
        active

執行：

    python -m pytest tests/V6_3/test_generic_search_provider_real_techorange_53.py -s -v
"""


from search.generic_search_provider import (
    GenericSearchProvider,
)


# ==================================================
#
# Target 53
#
# ==================================================

TARGET_ID = 53

TARGET_NAME = "TechOrange"

TARGET_URL = (
    "https://techorange.com/author/industry-update/"
)

CRAWLER_URL = (
    "https://techorange.com/"
)

KEYWORD = "IC semiconductor"

MAX_RESULTS = 20


# ==================================================
#
# Test
#
# ==================================================

def test_generic_search_real_techorange_target_53():

    print()
    print("=" * 60)
    print(
        f"Target {TARGET_ID} "
        f"Generic Search Provider Real Test"
    )
    print("=" * 60)

    print()
    print(f"Target       : {TARGET_NAME}")
    print(f"Target URL   : {TARGET_URL}")
    print(f"Crawler URL  : {CRAWLER_URL}")
    print(f"Keyword      : {KEYWORD}")
    print(f"Max Results  : {MAX_RESULTS}")

    # ==================================================
    #
    # Provider
    #
    # ==================================================

    provider = GenericSearchProvider()

    # ==================================================
    #
    # Execute Generic Search
    #
    # ==================================================

    results = provider.search(
        keyword=KEYWORD,
        max_results=MAX_RESULTS,
        url=TARGET_URL,
        crawler_url=CRAWLER_URL,
    )

    # ==================================================
    #
    # Basic Validation
    #
    # ==================================================

    assert isinstance(
        results,
        list,
    )

    # ==================================================
    #
    # Print Matching URLs Only
    #
    # ==================================================

    print()
    print("=" * 60)
    print("MATCHING URLS")
    print("=" * 60)

    print(
        f"Result Count : {len(results)}"
    )

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"[{index}] {result.url}"
        )

    print("=" * 60)

    # ==================================================
    #
    # Verify crawler URL
    #
    # ==================================================

    for result in results:

        assert result.url.startswith(
            CRAWLER_URL
        )

    # ==================================================
    #
    # Result Limit
    #
    # ==================================================

    assert len(results) <= MAX_RESULTS