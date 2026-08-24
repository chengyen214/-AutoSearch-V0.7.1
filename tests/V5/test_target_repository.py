"""
tests/V5/test_target_repository.py

AutoSearch V5

TargetRepository Integration Test

測試：

    Target Model
        ↓
    TargetRepository
        ↓
    MySQL targets

測試內容：

    1. 建立 Direct URL Target
    2. 建立 Keyword Search Target
    3. 建立 URL + Keyword Search Target
    4. find_all()
    5. get_by_id()
    6. get_by_url()
    7. get_by_keyword()
    8. get_by_search()
    9. find_active()
    10. find_by_status()
    11. find_by_type()
    12. update_status()
    13. delete_by_id()

注意：

    這是 Integration Test。

    會實際操作 MySQL targets table。

    執行前請確認：

        - MySQL 已啟動
        - .env Database 設定正確
        - targets table 已建立

執行：

    python -m tests.V5.test_target_repository
"""


# ============================================================
#
# Imports
#
# ============================================================

from models.target import Target

from database.target_repository import (
    TargetRepository,
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
    repository,
):
    """
    測試建立三種 Target。
    """

    print_section(
        "TEST 1 - CREATE TARGETS"
    )

    # --------------------------------------------------------
    # Direct URL
    # --------------------------------------------------------

    direct_url = Target(

        name=(
            "TEST - Direct URL"
        ),

        target_type=(
            Target.TYPE_URL
        ),

        url=(
            "https://example.com"
        ),

        keyword="",

        search_provider="",

        description=(
            "V5 TargetRepository test - Direct URL"
        ),
    )

    direct_url = repository.save(
        direct_url
    )

    print(
        "[PASS] Direct URL created:"
    )

    print_target(
        direct_url
    )

    assert direct_url.id is not None

    # --------------------------------------------------------
    # Keyword
    # --------------------------------------------------------

    keyword_target = Target(

        name=(
            "TEST - Keyword"
        ),

        target_type=(
            Target.TYPE_SEARCH
        ),

        url="",

        keyword=(
            "TEST semiconductor"
        ),

        search_provider=(
            Target.PROVIDER_GOOGLE_SEARCH
        ),

        description=(
            "V5 TargetRepository test - Keyword"
        ),
    )

    keyword_target = repository.save(
        keyword_target
    )

    print(
        "[PASS] Keyword Target created:"
    )

    print_target(
        keyword_target
    )

    assert keyword_target.id is not None

    # --------------------------------------------------------
    # URL + Keyword
    # --------------------------------------------------------

    url_keyword_target = Target(

        name=(
            "TEST - URL + Keyword"
        ),

        target_type=(
            Target.TYPE_SEARCH
        ),

        url=(
            "https://www.tsmc.com"
        ),

        keyword=(
            "TEST semiconductor"
        ),

        search_provider=(
            Target.PROVIDER_GOOGLE_SEARCH
        ),

        description=(
            "V5 TargetRepository test - URL + Keyword"
        ),
    )

    url_keyword_target = repository.save(
        url_keyword_target
    )

    print(
        "[PASS] URL + Keyword Target created:"
    )

    print_target(
        url_keyword_target
    )

    assert url_keyword_target.id is not None

    return (
        direct_url,
        keyword_target,
        url_keyword_target,
    )


# ============================================================
#
# Test Find All
#
# ============================================================


def test_find_all(
    repository,
):
    """
    測試 find_all().
    """

    print_section(
        "TEST 2 - FIND ALL"
    )

    targets = (
        repository.find_all()
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
    repository,
    target,
):
    """
    測試 get_by_id().
    """

    print_section(
        "TEST 3 - GET BY ID"
    )

    result = (
        repository.get_by_id(
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
    repository,
    target,
):
    """
    測試 get_by_url().
    """

    print_section(
        "TEST 4 - GET BY URL"
    )

    result = (
        repository.get_by_url(
            target.url
        )
    )

    print_target(
        result
    )

    assert result is not None

    assert (
        result.url
        == target.url
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
    repository,
    target,
):
    """
    測試 get_by_keyword().
    """

    print_section(
        "TEST 5 - GET BY KEYWORD"
    )

    result = (
        repository.get_by_keyword(
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
    repository,
    target,
):
    """
    測試 get_by_search().
    """

    print_section(
        "TEST 6 - GET BY SEARCH"
    )

    result = (
        repository.get_by_search(

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
    repository,
):
    """
    測試 find_active().
    """

    print_section(
        "TEST 7 - FIND ACTIVE"
    )

    targets = (
        repository.find_active()
    )

    print(
        f"[PASS] Active Targets: "
        f"{len(targets)}"
    )

    for target in targets:

        print_target(
            target
        )

        assert (
            target.status
            == "active"
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
    repository,
):
    """
    測試 find_by_status()。

    測試：

        active
        completed
        不存在的 status

    """

    print_section(
        "TEST 8 - FIND BY STATUS"
    )

    # --------------------------------------------------------
    # Active
    # --------------------------------------------------------

    active_targets = (
        repository.find_by_status(
            "active"
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

        assert (
            target.status
            == "active"
        )

    assert isinstance(
        active_targets,
        list,
    )

    # --------------------------------------------------------
    # Completed
    # --------------------------------------------------------

    completed_targets = (
        repository.find_by_status(
            "completed"
        )
    )

    print(
        f"Completed Targets: "
        f"{len(completed_targets)}"
    )

    for target in completed_targets:

        print_target(
            target
        )

        assert (
            target.status
            == "completed"
        )

    assert isinstance(
        completed_targets,
        list,
    )

    # --------------------------------------------------------
    # Non-existent Status
    # --------------------------------------------------------

    unknown_targets = (
        repository.find_by_status(
            "TEST_NON_EXISTENT_STATUS"
        )
    )

    print(
        f"Unknown Status Targets: "
        f"{len(unknown_targets)}"
    )

    assert isinstance(
        unknown_targets,
        list,
    )

    assert (
        len(unknown_targets)
        == 0
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
    repository,
):
    """
    測試 URL / Search Target。
    """

    print_section(
        "TEST 9 - FIND BY TYPE"
    )

    url_targets = (
        repository.find_by_type(
            Target.TYPE_URL
        )
    )

    search_targets = (
        repository.find_by_type(
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

        assert (
            target.target_type
            == Target.TYPE_URL
        )

    print(
        "Search Targets:"
    )

    for target in search_targets:

        print_target(
            target
        )

        assert (
            target.target_type
            == Target.TYPE_SEARCH
        )

    assert isinstance(
        url_targets,
        list,
    )

    assert isinstance(
        search_targets,
        list,
    )


# ============================================================
#
# Test Update Status
#
# ============================================================


def test_update_status(
    repository,
    target,
):
    """
    測試 status 更新。

    目前只是確認 Repository
    能正確更新 SQL。

    不代表正式 Crawl 流程。
    """

    print_section(
        "TEST 10 - UPDATE STATUS"
    )

    updated = (
        repository.update_status(

            target_id=(
                target.id
            ),

            status="completed",

        )
    )

    assert updated is True

    result = (
        repository.get_by_id(
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
        "[PASS] status = completed"
    )

    # --------------------------------------------------------
    # Verify find_by_status()
    #
    # 確認 update_status() 後，
    # find_by_status() 可以查到該 Target。
    # --------------------------------------------------------

    completed_targets = (
        repository.find_by_status(
            "completed"
        )
    )

    assert isinstance(
        completed_targets,
        list,
    )

    assert any(
        item.id == target.id
        for item in completed_targets
    )

    print(
        "[PASS] find_by_status('completed') "
        "contains updated target"
    )


# ============================================================
#
# Test Delete
#
# ============================================================


def test_delete(
    repository,
    targets,
):
    """
    測試刪除測試資料。
    """

    print_section(
        "TEST 11 - DELETE TEST DATA"
    )

    for target in targets:

        deleted = (
            repository.delete_by_id(
                target.id
            )
        )

        assert deleted is True

        result = (
            repository.get_by_id(
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
    執行完整 TargetRepository Integration Test。
    """

    print()
    print(
        "AutoSearch V5"
    )
    print(
        "TargetRepository Integration Test"
    )
    print()

    repository = (
        TargetRepository()
    )

    # --------------------------------------------------------
    # Create
    # --------------------------------------------------------

    targets = (
        test_create_targets(
            repository
        )
    )

    direct_url = targets[0]

    keyword_target = targets[1]

    url_keyword_target = targets[2]

    # --------------------------------------------------------
    # Find
    # --------------------------------------------------------

    test_find_all(
        repository
    )

    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    test_get_by_id(
        repository,
        direct_url,
    )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    test_get_by_url(
        repository,
        direct_url,
    )

    # --------------------------------------------------------
    # Keyword
    # --------------------------------------------------------

    test_get_by_keyword(
        repository,
        keyword_target,
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    test_get_by_search(
        repository,
        keyword_target,
    )

    # --------------------------------------------------------
    # Active
    # --------------------------------------------------------

    test_find_active(
        repository
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    test_find_by_status(
        repository
    )

    # --------------------------------------------------------
    # Type
    # --------------------------------------------------------

    test_find_by_type(
        repository
    )

    # --------------------------------------------------------
    # Update Status
    # --------------------------------------------------------

    test_update_status(
        repository,
        direct_url,
    )

    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    test_delete(
        repository,
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
        "ALL TARGET REPOSITORY TESTS PASSED"
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
