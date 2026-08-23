"""
tests/V5/test_search_execution_bridge.py

AutoSearch V5

V5.6.3
Search Execution Bridge Test

測試範圍：

    SQL
      ↓
    Target
      ↓
    TargetSourceService
      ↓
    SourceResolutionBridge
      ↓
    Resolved Source
      ↓
    SearchExecutionBridge
      ↓
    SearchResult[]

本測試：

    ✅ 測試 Search Target
    ✅ 測試 Resolved Source
    ✅ 測試 Provider
    ✅ 測試 Adapter
    ✅ 真正執行 Search
    ✅ 顯示 SearchResult

不測試：

    ❌ Crawl
    ❌ Parser
    ❌ ArticleService
    ❌ Archive
    ❌ AI Task
"""

# ==================================================
#
# Target Repository
#
# ==================================================

from database.target_repository import (
    TargetRepository,
)


# ==================================================
#
# Target Source Service
#
# ==================================================

from services.target_source_service import (
    TargetSourceService,
)


# ==================================================
#
# Source Resolution Bridge
#
# ==================================================

from services.source_resolution_bridge import (
    SourceResolutionBridge,
)


# ==================================================
#
# Search Execution Bridge
#
# ==================================================

from services.search_execution_bridge import (
    SearchExecutionBridge,
)


def main():

    print("=" * 70)
    print("AutoSearch V5")
    print("V5.6.3 Search Execution Bridge Test")
    print("=" * 70)

    # ==================================================
    #
    # Services
    #
    # ==================================================

    target_repository = (
        TargetRepository()
    )

    target_source_service = (
        TargetSourceService()
    )

    source_resolution_bridge = (
        SourceResolutionBridge()
    )

    search_execution_bridge = (
        SearchExecutionBridge()
    )

    # ==================================================
    #
    # 1. 從 SQL 取得 Target
    #
    # ==================================================

    print()
    print("[1] 從 SQL 取得 Search Target")
    print("-" * 70)

    targets = []

    for target_id in (
        16,
        17,
        18,
    ):

        target = (
            target_repository.get_by_id(
                target_id
            )
        )

        if target is None:
            continue

        print(
            f"Target #{target.id}"
        )

        print(
            f"  name             = "
            f"{target.name}"
        )

        print(
            f"  target_type      = "
            f"{target.target_type}"
        )

        print(
            f"  url              = "
            f"{target.url}"
        )

        print(
            f"  keyword          = "
            f"{target.keyword}"
        )

        print(
            f"  search_provider  = "
            f"{target.search_provider}"
        )

        targets.append(target)

    if not targets:

        print()
        print("❌ SQL 中找不到 Target")
        return

    # ==================================================
    #
    # 2. Target → Source Definition
    #
    # ==================================================

    print()
    print("[2] Target → Source Definition")
    print("-" * 70)

    search_target = None
    source_definition = None

    for target in targets:

        if target.target_type != "search":
            continue

        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        source_definition = (
            target_source_service.resolve(
                target
            )
        )

        print(
            "  source_type = "
            f"{source_definition.get('source_type')}"
        )

        print(
            "  keyword     = "
            f"{source_definition.get('keyword')}"
        )

        print(
            "  provider    = "
            f"{source_definition.get('provider')}"
        )

        search_target = target

        print(
            "  ✅ Search Target found"
        )

        break

    if search_target is None:

        print()
        print(
            "❌ 找不到 target_type=search 的 Target"
        )
        return

    # ==================================================
    #
    # 3. Source Definition → Resolved Source
    #
    # ==================================================

    print()
    print("[3] Source Definition → Resolved Source")
    print("-" * 70)

    resolved_source = (
        source_resolution_bridge.resolve(
            source_definition
        )
    )

    if resolved_source is None:

        print(
            "❌ Resolved Source is None"
        )
        return

    print(
        "  resolved_type = "
        f"{type(resolved_source).__name__}"
    )

    print(
        "  resolved      = "
        f"{resolved_source}"
    )

    # ==================================================
    #
    # 4. Resolution Check
    #
    # ==================================================

    print()
    print("[4] Resolved Source Check")
    print("-" * 70)

    is_search = (
        source_resolution_bridge.is_search(
            resolved_source
        )
    )

    print(
        f"  is_search = {is_search}"
    )

    if not is_search:

        print(
            "❌ Resolved Source 不是 Search Source"
        )
        return

    provider = (
        source_resolution_bridge.get_provider(
            resolved_source
        )
    )

    adapter = (
        source_resolution_bridge.get_adapter(
            resolved_source
        )
    )

    search_source = (
        source_resolution_bridge.get_search_source(
            resolved_source
        )
    )

    print(
        "  provider type = "
        f"{type(provider).__name__}"
    )

    print(
        "  adapter type  = "
        f"{type(adapter).__name__}"
    )

    print(
        "  search_source = "
        f"{search_source}"
    )

    # ==================================================
    #
    # 5. Search Execution
    #
    # ==================================================

    print()
    print("[5] 執行 Search")
    print("-" * 70)

    print(
        f"  keyword = {search_target.keyword}"
    )

    print(
        f"  provider = "
        f"{search_target.search_provider}"
    )

    print()
    print(
        "  ▶ SearchExecutionBridge.execute()"
    )

    try:

        search_results = (
            search_execution_bridge.execute(
                resolved_source
            )
        )

    except Exception as exc:

        print()
        print(
            "❌ Search Execution Failed"
        )

        print(
            f"  error = {exc}"
        )

        raise

    # ==================================================
    #
    # 6. Search Result
    #
    # ==================================================

    print()
    print("[6] Search Results")
    print("-" * 70)

    if search_results is None:

        print(
            "❌ SearchExecutionBridge "
            "returned None"
        )

        return

    search_results = list(
        search_results
    )

    print(
        f"  total results = "
        f"{len(search_results)}"
    )

    if not search_results:

        print()
        print(
            "⚠️ Search 執行成功，但沒有結果"
        )

        return

    # ==================================================
    #
    # 7. Display Results
    #
    # ==================================================

    print()

    for index, result in enumerate(
        search_results,
        start=1,
    ):

        print(
            f"Result #{index}"
        )

        print(
            f"  type        = "
            f"{type(result).__name__}"
        )

        # ----------------------------------------------
        # Dict
        # ----------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            print(
                f"  title       = "
                f"{result.get('title')}"
            )

            print(
                f"  url         = "
                f"{result.get('url')}"
            )

            print(
                f"  source      = "
                f"{result.get('source')}"
            )

            print(
                f"  provider    = "
                f"{result.get('provider')}"
            )

        # ----------------------------------------------
        # Object
        # ----------------------------------------------

        else:

            print(
                f"  title       = "
                f"{getattr(result, 'title', None)}"
            )

            print(
                f"  url         = "
                f"{getattr(result, 'url', None)}"
            )

            print(
                f"  source      = "
                f"{getattr(result, 'source', None)}"
            )

            print(
                f"  provider    = "
                f"{getattr(result, 'provider', None)}"
            )

        print()

    # ==================================================
    #
    # Finished
    #
    # ==================================================

    print("=" * 70)
    print("Search Execution Bridge Test Finished")
    print("=" * 70)


if __name__ == "__main__":

    main()
