"""
tests/V6_3/test_target_repository_crawler_url.py

AutoSearch V6

Test:
    TargetRepository.get_crawler_url_by_url_keyword()

用途：

    驗證：

        URL + Keyword
            ↓
        targets
            ↓
        crawler_url

測試資料：

    Target ID:
        18

    Name:
        TSMC

    Target Type:
        url

    URL:
        https://www.tsmc.com/

    crawler_url:
        https://pr.tsmc.com/chinese/news/

    Keyword:
        IC semiconductor

    Search Provider:
        google_search
"""


from database.target_repository import (
    TargetRepository,
)


def main():

    print()
    print("========================================")
    print(" V6.3 Target Repository Test")
    print("========================================")

    url = (
        "https://www.tsmc.com/"
    )

    keyword = (
        "IC semiconductor"
    )

    expected_crawler_url = (
        "https://pr.tsmc.com/chinese/news/"
    )

    print()
    print("URL:")
    print(url)

    print()
    print("Keyword:")
    print(keyword)

    print()
    print("Expected crawler_url:")
    print(expected_crawler_url)

    # ==========================================
    # Repository
    # ==========================================

    repository = TargetRepository()

    # ==========================================
    # Query
    # ==========================================

    crawler_url = (
        repository.get_crawler_url_by_url_keyword(
            url=url,
            keyword=keyword,
        )
    )

    print()
    print("Actual crawler_url:")
    print(crawler_url)

    # ==========================================
    # Validation
    # ==========================================

    assert crawler_url is not None, (
        "crawler_url should not be None"
    )

    assert crawler_url == expected_crawler_url, (
        f"Unexpected crawler_url: "
        f"{crawler_url}"
    )

    print()
    print("========================================")
    print(" TEST PASSED")
    print("========================================")
    print()


if __name__ == "__main__":

    main()