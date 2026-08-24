"""
tests/V5/test_target_service.py

AutoSearch V5

V5.3 P3.4

TargetService Integration Test

測試：

    Target Model
        ↓
    TargetService
        ↓
    TargetValidator
        ↓
    TargetRepository
        ↓
    MySQL targets


測試內容：

    1. 建立 URL Target
    2. 建立 Search Target
    3. 建立 Google Search Target
    4. 建立 Google News Target
    5. find_all()
    6. get_by_id()
    7. get_by_url()
    8. get_by_keyword()
    9. get_by_search()
    10. find_active()
    11. find_by_status()
    12. find_by_type()
    13. find_url_targets()
    14. find_search_targets()
    15. update()
    16. update_status()
    17. enable()
    18. disable()
    19. exists()
    20. exists_by_url()
    21. exists_by_search()
    22. count()
    23. count_active()
    24. count_by_type()
    25. Duplicate Check
    26. delete()


注意：

    這是 Integration Test。

    會實際操作 MySQL targets table。

    執行前請確認：

        - MySQL 已啟動
        - .env Database 設定正確
        - targets table 已建立


執行：

    python -m tests.V5.test_target_service
"""


# ============================================================
#
# Imports
#
# ============================================================

from models.target import Target

from services.target_service import (
    TargetService,
)


# ============================================================
#
# Test Helpers
#
# ============================================================


def print_section(
    title,
):
    """
    顯示測試區段。
    """

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_target(
    target,
):
    """
    顯示 Target。
    """

    if target is None:

        print(
            "Target: None"
        )

        return

    print(
        target.to_dict()
    )


# ============================================================
#
# Test Create
#
# ============================================================


def test_create_targets(
    service,
):
    """
    測試建立四種 Target。
    """

    print_section(
        "TEST 1 - CREATE TARGETS"
    )

    # --------------------------------------------------------
    # URL Target
    # --------------------------------------------------------

    url_target = (
        service.create_url_target(

            url=(
                "https://example.com"
            ),

            name=(
                "TEST SERVICE - URL"
            ),

            description=(
                "V5 TargetService test - URL"
            ),
        )
    )

    print(
        "[PASS] URL Target created:"
    )

    print_target(
        url_target
    )

    assert url_target.id is not None

    assert (
        url_target.target_type
        == Target.TYPE_URL
    )

    # --------------------------------------------------------
    # Search Target
    # --------------------------------------------------------

    search_target = (
        service.create_search_target(

            keyword=(
                "TEST service semiconductor"
            ),

            search_provider=(
                Target.PROVIDER_GOOGLE_SEARCH
            ),

            name=(
                "TEST SERVICE - Search"
            ),

            description=(
                "V5 TargetService test - Search"
            ),
        )
    )

    print(
        "[PASS] Search Target created:"
    )

    print_target(
        search_target
    )

    assert search_target.id is not None

    assert (
        search_target.target_type
        == Target.TYPE_SEARCH
    )

    # --------------------------------------------------------
    # Google Search
    # --------------------------------------------------------

    google_search_target = (
        service.create_google_search_target(

            keyword=(
                "TEST google search"
            ),

            name=(
                "TEST SERVICE - Google Search"
            ),

            description=(
                "V5 TargetService test - Google Search"
            ),
        )
    )

    print(
        "[PASS] Google Search Target created:"
    )

    print_target(
        google_search_target
    )

    assert google_search_target.id is not None

    assert (
        google_search_target.search_provider
        == Target.PROVIDER_GOOGLE_SEARCH
    )

    # --------------------------------------------------------
    # Google News
    # --------------------------------------------------------

    google_news_target = (
        service.create_google_news_target(

            keyword=(
                "TEST google news"
            ),

            name=(
                "TEST SERVICE - Google News"
            ),

            description=(
                "V5 TargetService test - Google News"
            ),
        )
    )

    print(
        "[PASS] Google News Target created:"
    )

    print_target(
        google_news_target
    )

    assert google_news_target.id is not None

    assert (
        google_news_target.search_provider
        == Target.PROVIDER_GOOGLE_NEWS
    )

    return (
        url_target,
        search_target,
        google_search_target,
        google_news_target,
    )


# ============================================================
#
# Test Find All
#
# ============================================================


def test_find_all(
    service,
):
    """
    測試 find_all().
    """

    print_section(
        "TEST 2 - FIND ALL"
    )

    targets = (
        service.find_all()
    )

    print(
        f"[PASS] Total Targets: "
        f"{len(targets)}"
    )

    for target in targets:

        print_target(
            target
        )

    assert isinstance(
        targets,
        list,
    )


# ============================================================
#
# Test Get By ID
#
# ============================================================


def test_get_by_id(
    service,
    target,
):
    """
    測試 get_by_id().
    """

    print_section(
        "TEST 3 - GET BY ID"
    )

    result = (
        service.get_by_id(
            target.id
        )
    )

    print_target(
        result
    )

    assert result is not None

    assert (
        result.id
        == target.id
    )

    print(
        "[PASS] get_by_id()"
    )


# ============================================================
#
# Test Get By URL
#
# ============================================================


def test_get_by_url(
    service,
    target,
):
    """
    測試 get_by_url().
    """

    print_section(
        "TEST 4 - GET BY URL"
    )

    result = (
        service.get_by_url(
            "https://example.com/"
        )
    )

    print_target(
        result
    )

    assert result is not None

    assert (
        result.id
        == target.id
    )

    print(
        "[PASS] get_by_url()"
    )


# ============================================================
#
# Test Get By Keyword
#
# ============================================================


def test_get_by_keyword(
    service,
    target,
):
    """
    測試 get_by_keyword().
    """

    print_section(
        "TEST 5 - GET BY KEYWORD"
    )

    result = (
        service.get_by_keyword(
            target.keyword
        )
    )

    print_target(
        result
    )

    assert result is not None

    assert (
        result.keyword
        == target.keyword
    )

    print(
        "[PASS] get_by_keyword()"
    )


# ============================================================
#
# Test Get By Search
#
# ============================================================


def test_get_by_search(
    service,
    target,
):
    """
    測試 get_by_search().
    """

    print_section(
        "TEST 6 - GET BY SEARCH"
    )

    result = (
        service.get_by_search(

            keyword=(
                target.keyword
            ),

            search_provider=(
                target.search_provider
            ),
        )
    )

    print_target(
        result
    )

    assert result is not None

    assert (
        result.keyword
        == target.keyword
    )

    assert (
        result.search_provider
        == target.search_provider
    )

    print(
        "[PASS] get_by_search()"
    )


# ============================================================
#
# Test Find Active
#
# ============================================================


def test_find_active(
    service,
):
    """
    測試 find_active().
    """

    print_section(
        "TEST 7 - FIND ACTIVE"
    )

    targets = (
        service.find_active()
    )

    print(
        f"[PASS] Active Targets: "
        f"{len(targets)}"
    )

    for target in targets:

        print_target(
            target
        )

    assert isinstance(
        targets,
        list,
    )


# ============================================================
#
# Test Find By Status
#
# ============================================================


def test_find_by_status(
    service,
):
    """
    測試 find_by_status().
    """

    print_section(
        "TEST 8 - FIND BY STATUS"
    )

    active_targets = (
        service.find_by_status(
            "active"
        )
    )

    completed_targets = (
        service.find_by_status(
            "completed"
        )
    )

    unknown_targets = (
        service.find_by_status(
            "unknown"
        )
    )

    print(
        f"Active Targets: "
        f"{len(active_targets)}"
    )

    for target in active_targets:

        print_target(
            target
        )

    print(
        f"Completed Targets: "
        f"{len(completed_targets)}"
    )

    for target in completed_targets:

        print_target(
            target
        )

    print(
        f"Unknown Status Targets: "
        f"{len(unknown_targets)}"
    )

    assert isinstance(
        active_targets,
        list,
    )

    assert isinstance(
        completed_targets,
        list,
    )

    assert isinstance(
        unknown_targets,
        list,
    )

    print(
        "[PASS] find_by_status()"
    )


# ============================================================
#
# Test Find By Type
#
# ============================================================


def test_find_by_type(
    service,
):
    """
    測試 find_by_type().
    """

    print_section(
        "TEST 9 - FIND BY TYPE"
    )

    url_targets = (
        service.find_by_type(
            Target.TYPE_URL
        )
    )

    search_targets = (
        service.find_by_type(
            Target.TYPE_SEARCH
        )
    )

    print(
        "URL Targets:"
    )

    for target in url_targets:

        print_target(
            target
        )

    print(
        "Search Targets:"
    )

    for target in search_targets:

        print_target(
            target
        )

    assert isinstance(
        url_targets,
        list,
    )

    assert isinstance(
        search_targets,
        list,
    )

    print(
        "[PASS] find_by_type()"
    )


# ============================================================
#
# Test Find URL Targets
#
# ============================================================


def test_find_url_targets(
    service,
):
    """
    測試 find_url_targets().
    """

    print_section(
        "TEST 10 - FIND URL TARGETS"
    )

    targets = (
        service.find_url_targets()
    )

    print(
        f"URL Targets: "
        f"{len(targets)}"
    )

    for target in targets:

        print_target(
            target
        )

    assert isinstance(
        targets,
        list,
    )

    for target in targets:

        assert (
            target.target_type
            == Target.TYPE_URL
        )

    print(
        "[PASS] find_url_targets()"
    )


# ============================================================
#
# Test Find Search Targets
#
# ============================================================


def test_find_search_targets(
    service,
):
    """
    測試 find_search_targets().
    """

    print_section(
        "TEST 11 - FIND SEARCH TARGETS"
    )

    targets = (
        service.find_search_targets()
    )

    print(
        f"Search Targets: "
        f"{len(targets)}"
    )

    for target in targets:

        print_target(
            target
        )

    assert isinstance(
        targets,
        list,
    )

    for target in targets:

        assert (
            target.target_type
            == Target.TYPE_SEARCH
        )

    print(
        "[PASS] find_search_targets()"
    )


# ============================================================
#
# Test Update
#
# ============================================================


def test_update(
    service,
    target,
):
    """
    測試 update().
    """

    print_section(
        "TEST 12 - UPDATE"
    )

    target.name = (
        "TEST SERVICE - URL UPDATED"
    )

    target.description = (
        "Updated by TargetService test"
    )

    updated = (
        service.update(
            target
        )
    )

    print_target(
        updated
    )

    assert updated is not None

    assert (
        updated.id
        == target.id
    )

    assert (
        updated.name
        == "TEST SERVICE - URL UPDATED"
    )

    print(
        "[PASS] update()"
    )


# ============================================================
#
# Test Update Status
#
# ============================================================


def test_update_status(
    service,
    target,
):
    """
    測試 update_status().
    """

    print_section(
        "TEST 13 - UPDATE STATUS"
    )

    updated = (
        service.update_status(

            target_id=(
                target.id
            ),

            status="completed",
        )
    )

    assert updated is True

    result = (
        service.get_by_id(
            target.id
        )
    )

    print_target(
        result
    )

    assert result is not None

    assert (
        result.status
        == "completed"
    )

    print(
        "[PASS] update_status()"
    )


# ============================================================
#
# Test Enable
#
# ============================================================


def test_enable(
    service,
    target,
):
    """
    測試 enable().
    """

    print_section(
        "TEST 14 - ENABLE"
    )

    updated = (
        service.enable(
            target.id
        )
    )

    assert updated is True

    result = (
        service.get_by_id(
            target.id
        )
    )

    assert result is not None

    assert (
        result.status
        == "active"
    )

    print(
        "[PASS] enable()"
    )


# ============================================================
#
# Test Disable
#
# ============================================================


def test_disable(
    service,
    target,
):
    """
    測試 disable().
    """

    print_section(
        "TEST 15 - DISABLE"
    )

    updated = (
        service.disable(
            target.id
        )
    )

    assert updated is True

    result = (
        service.get_by_id(
            target.id
        )
    )

    assert result is not None

    assert (
        result.status
        != "active"
    )

    print_target(
        result
    )

    print(
        "[PASS] disable()"
    )

    # Restore for later tests.

    service.enable(
        target.id
    )


# ============================================================
#
# Test Exists
#
# ============================================================


def test_exists(
    service,
    target,
):
    """
    測試 exists().
    """

    print_section(
        "TEST 16 - EXISTS"
    )

    assert (
        service.exists(
            target.id
        )
        is True
    )

    assert (
        service.exists(
            999999999
        )
        is False
    )

    print(
        "[PASS] exists()"
    )


# ============================================================
#
# Test Exists By URL
#
# ============================================================


def test_exists_by_url(
    service,
    target,
):
    """
    測試 exists_by_url().
    """

    print_section(
        "TEST 17 - EXISTS BY URL"
    )

    assert (
        service.exists_by_url(
            "https://example.com/"
        )
        is True
    )

    assert (
        service.exists_by_url(
            "https://not-exists.example.com"
        )
        is False
    )

    print(
        "[PASS] exists_by_url()"
    )


# ============================================================
#
# Test Exists By Search
#
# ============================================================


def test_exists_by_search(
    service,
    target,
):
    """
    測試 exists_by_search().
    """

    print_section(
        "TEST 18 - EXISTS BY SEARCH"
    )

    assert (
        service.exists_by_search(

            keyword=(
                target.keyword
            ),

            search_provider=(
                target.search_provider
            ),
        )
        is True
    )

    assert (
        service.exists_by_search(

            keyword=(
                "THIS DOES NOT EXIST"
            ),

            search_provider=(
                Target.PROVIDER_GOOGLE_SEARCH
            ),
        )
        is False
    )

    print(
        "[PASS] exists_by_search()"
    )


# ============================================================
#
# Test Count
#
# ============================================================


def test_count(
    service,
):
    """
    測試 count().
    """

    print_section(
        "TEST 19 - COUNT"
    )

    total = (
        service.count()
    )

    print(
        f"Total Targets: "
        f"{total}"
    )

    assert isinstance(
        total,
        int,
    )

    assert total >= 0

    print(
        "[PASS] count()"
    )


# ============================================================
#
# Test Count Active
#
# ============================================================


def test_count_active(
    service,
):
    """
    測試 count_active().
    """

    print_section(
        "TEST 20 - COUNT ACTIVE"
    )

    total = (
        service.count_active()
    )

    print(
        f"Active Targets: "
        f"{total}"
    )

    assert isinstance(
        total,
        int,
    )

    assert total >= 0

    print(
        "[PASS] count_active()"
    )


# ============================================================
#
# Test Count By Type
#
# ============================================================


def test_count_by_type(
    service,
):
    """
    測試 count_by_type().
    """

    print_section(
        "TEST 21 - COUNT BY TYPE"
    )

    url_count = (
        service.count_by_type(
            Target.TYPE_URL
        )
    )

    search_count = (
        service.count_by_type(
            Target.TYPE_SEARCH
        )
    )

    print(
        f"URL Count: "
        f"{url_count}"
    )

    print(
        f"Search Count: "
        f"{search_count}"
    )

    assert isinstance(
        url_count,
        int,
    )

    assert isinstance(
        search_count,
        int,
    )

    assert url_count >= 0

    assert search_count >= 0

    print(
        "[PASS] count_by_type()"
    )


# ============================================================
#
# Test Duplicate Check
#
# ============================================================


def test_duplicate_check(
    service,
    targets,
):
    """
    測試 Duplicate Check。

    URL Target：

        相同 URL 不允許重複。

    Search Target：

        相同 Keyword +
        Search Provider
        不允許重複。
    """

    print_section(
        "TEST 22 - DUPLICATE CHECK"
    )

    url_target = targets[0]

    search_target = targets[1]

    # --------------------------------------------------------
    # Duplicate URL
    # --------------------------------------------------------

    try:

        service.create_url_target(

            url=url_target.url,

            name=(
                "TEST DUPLICATE URL"
            ),
        )

        raise AssertionError(
            "Duplicate URL should raise ValueError"
        )

    except ValueError as exc:

        print(
            "[PASS] Duplicate URL blocked:"
        )

        print(
            exc
        )

    # --------------------------------------------------------
    # Duplicate Search
    # --------------------------------------------------------

    try:

        service.create_search_target(

            keyword=(
                search_target.keyword
            ),

            search_provider=(
                search_target.search_provider
            ),

            name=(
                "TEST DUPLICATE SEARCH"
            ),
        )

        raise AssertionError(
            "Duplicate Search should raise ValueError"
        )

    except ValueError as exc:

        print(
            "[PASS] Duplicate Search blocked:"
        )

        print(
            exc
        )


# ============================================================
#
# Test Delete
#
# ============================================================


def test_delete(
    service,
    targets,
):
    """
    測試刪除測試資料。
    """

    print_section(
        "TEST 23 - DELETE TEST DATA"
    )

    for target in targets:

        deleted = (
            service.delete(
                target.id
            )
        )

        assert deleted is True

        result = (
            service.get_by_id(
                target.id
            )
        )

        assert result is None

        print(
            f"[PASS] Deleted Target "
            f"id={target.id}"
        )


# ============================================================
#
# Main
#
# ============================================================


def main():
    """
    執行完整 TargetService Integration Test。
    """

    print()
    print(
        "AutoSearch V5"
    )

    print(
        "TargetService Integration Test"
    )

    print()

    service = (
        TargetService()
    )

    # --------------------------------------------------------
    # Create
    # --------------------------------------------------------

    targets = (
        test_create_targets(
            service
        )
    )

    url_target = targets[0]

    search_target = targets[1]

    google_search_target = targets[2]

    google_news_target = targets[3]

    # --------------------------------------------------------
    # Find
    # --------------------------------------------------------

    test_find_all(
        service
    )

    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    test_get_by_id(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    test_get_by_url(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # Keyword
    # --------------------------------------------------------

    test_get_by_keyword(
        service,
        search_target,
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    test_get_by_search(
        service,
        search_target,
    )

    # --------------------------------------------------------
    # Active
    # --------------------------------------------------------

    test_find_active(
        service
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    test_find_by_status(
        service
    )

    # --------------------------------------------------------
    # Type
    # --------------------------------------------------------

    test_find_by_type(
        service
    )

    # --------------------------------------------------------
    # URL Targets
    # --------------------------------------------------------

    test_find_url_targets(
        service
    )

    # --------------------------------------------------------
    # Search Targets
    # --------------------------------------------------------

    test_find_search_targets(
        service
    )

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    test_update(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # Update Status
    # --------------------------------------------------------

    test_update_status(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # Enable
    # --------------------------------------------------------

    test_enable(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # Disable
    # --------------------------------------------------------

    test_disable(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # Exists
    # --------------------------------------------------------

    test_exists(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # Exists By URL
    # --------------------------------------------------------

    test_exists_by_url(
        service,
        url_target,
    )

    # --------------------------------------------------------
    # Exists By Search
    # --------------------------------------------------------

    test_exists_by_search(
        service,
        search_target,
    )

    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------

    test_count(
        service
    )

    # --------------------------------------------------------
    # Count Active
    # --------------------------------------------------------

    test_count_active(
        service
    )

    # --------------------------------------------------------
    # Count By Type
    # --------------------------------------------------------

    test_count_by_type(
        service
    )

    # --------------------------------------------------------
    # Duplicate Check
    # --------------------------------------------------------

    test_duplicate_check(
        service,
        targets,
    )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    test_delete(
        service,
        targets,
    )

    # --------------------------------------------------------
    # Done
    # --------------------------------------------------------

    print()
    print(
        "=" * 60
    )

    print(
        "ALL TARGET SERVICE TESTS PASSED"
    )

    print(
        "=" * 60
    )


# ============================================================
#
# Entry Point
#
# ============================================================


if __name__ == "__main__":

    main()
