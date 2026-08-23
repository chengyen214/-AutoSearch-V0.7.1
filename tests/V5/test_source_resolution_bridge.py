"""
tests/V5/test_source_resolution_bridge.py

AutoSearch V5

V5.6.2
Source Resolution Bridge Test

測試：

    SQL Target
        ↓
    TargetSourceService
        ↓
    Source Definition
        ↓
    SourceResolutionBridge
        ↓
    Resolved Source

目前測試 Target：

    #16 Google News
        search / google_news

    #17 Intel
        url

    #18 TSMC
        url

注意：

    本測試只確認 Source Resolution。

    不執行：

        Search
        SearchAdapter.search()
        Crawler
        Parser
        ArticleService
        Archive
        AI
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
# Configuration
#
# ==================================================

TARGET_IDS = [
    16,
    17,
    18,
]


# ==================================================
#
# Main Test
#
# ==================================================

def main():

    print("=" * 70)
    print("AutoSearch V5")
    print("V5.6.2 Source Resolution Bridge Test")
    print("=" * 70)

    # ==================================================
    #
    # Services
    #
    # ==================================================

    repository = TargetRepository()

    target_source_service = (
        TargetSourceService()
    )

    bridge = (
        SourceResolutionBridge()
    )

    # ==================================================
    #
    # 1. SQL → Target
    #
    # ==================================================

    print()
    print("[1] 從 SQL 取得 Target")
    print("-" * 70)

    targets = []

    for target_id in TARGET_IDS:

        target = repository.get_by_id(
            target_id
        )

        if target is None:

            print(
                f"❌ 找不到 Target #{target_id}"
            )

            continue

        targets.append(
            target
        )

        print(
            f"Target #{target.id}"
        )

        print(
            f"  name             = {target.name}"
        )

        print(
            f"  target_type      = {target.target_type}"
        )

        print(
            f"  url              = {target.url}"
        )

        print(
            f"  keyword          = {target.keyword}"
        )

        print(
            f"  search_provider  = "
            f"{target.search_provider}"
        )

    if not targets:

        print()
        print(
            "❌ 沒有可測試的 Target"
        )
        return

    # ==================================================
    #
    # 2. Target → Source Definition
    #
    # ==================================================

    print()
    print("[2] Target → Source Definition")
    print("-" * 70)

    source_definitions = []

    for target in targets:

        print()
        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        try:

            source_definition = (
                target_source_service.resolve(
                    target
                )
            )

            source_definitions.append(
                (
                    target,
                    source_definition,
                )
            )

            print(
                "  ✅ Source Definition resolved"
            )

            print(
                f"  source_type = "
                f"{source_definition.get('source_type')}"
            )

            print(
                f"  target_type = "
                f"{source_definition.get('target_type')}"
            )

            if (
                source_definition.get(
                    "source_type"
                )
                == target_source_service.SOURCE_TYPE_SEARCH
            ):

                print(
                    f"  keyword     = "
                    f"{source_definition.get('keyword')}"
                )

                print(
                    f"  provider    = "
                    f"{source_definition.get('provider')}"
                )

            else:

                print(
                    f"  url         = "
                    f"{source_definition.get('url')}"
                )

        except Exception as exc:

            print(
                "  ❌ Source Definition failed"
            )

            print(
                f"  error = {exc}"
            )

    if not source_definitions:

        print()
        print(
            "❌ 沒有成功的 Source Definition"
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

    resolved_sources = []

    for target, source_definition in (
        source_definitions
    ):

        print()
        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        try:

            resolved_source = (
                bridge.resolve(
                    source_definition
                )
            )

            resolved_sources.append(
                (
                    target,
                    resolved_source,
                )
            )

            print(
                "  ✅ Resolved Source"
            )

            print(
                f"  resolved_type = "
                f"{type(resolved_source).__name__}"
            )

            print(
                f"  resolved     = "
                f"{resolved_source}"
            )

        except Exception as exc:

            print(
                "  ❌ Resolution failed"
            )

            print(
                f"  error = {exc}"
            )

    # ==================================================
    #
    # 4. Resolved Source Type
    #
    # ==================================================

    print()
    print("[4] Resolved Source Type")
    print("-" * 70)

    for target, resolved_source in (
        resolved_sources
    ):

        print()
        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        try:

            is_direct_url = (
                bridge.is_direct_url(
                    resolved_source
                )
            )

            is_search = (
                bridge.is_search(
                    resolved_source
                )
            )

            print(
                f"  is_direct_url = "
                f"{is_direct_url}"
            )

            print(
                f"  is_search     = "
                f"{is_search}"
            )

        except Exception as exc:

            print(
                "  ❌ Source type check failed"
            )

            print(
                f"  error = {exc}"
            )

    # ==================================================
    #
    # 5. Provider Resolution
    #
    # ==================================================

    print()
    print("[5] Provider Resolution")
    print("-" * 70)

    for target, resolved_source in (
        resolved_sources
    ):

        print()
        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        if not bridge.is_search(
            resolved_source
        ):

            print(
                "  type = direct_url"
            )

            print(
                "  provider = None"
            )

            continue

        try:

            provider = (
                bridge.get_provider(
                    resolved_source
                )
            )

            print(
                f"  provider type = "
                f"{type(provider).__name__}"
            )

            print(
                f"  provider      = "
                f"{provider}"
            )

        except Exception as exc:

            print(
                "  ❌ Provider resolution failed"
            )

            print(
                f"  error = {exc}"
            )

    # ==================================================
    #
    # 6. Adapter Resolution
    #
    # ==================================================

    print()
    print("[6] Adapter Resolution")
    print("-" * 70)

    for target, resolved_source in (
        resolved_sources
    ):

        print()
        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        if not bridge.is_search(
            resolved_source
        ):

            print(
                "  type = direct_url"
            )

            print(
                "  adapter = None"
            )

            continue

        try:

            adapter = (
                bridge.get_adapter(
                    resolved_source
                )
            )

            print(
                f"  adapter type = "
                f"{type(adapter).__name__}"
            )

            print(
                f"  adapter      = "
                f"{adapter}"
            )

        except Exception as exc:

            print(
                "  ❌ Adapter resolution failed"
            )

            print(
                f"  error = {exc}"
            )

    # ==================================================
    #
    # 7. Search Source Identity
    #
    # ==================================================

    print()
    print("[7] Search Source Identity")
    print("-" * 70)

    for target, resolved_source in (
        resolved_sources
    ):

        print()
        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        if not bridge.is_search(
            resolved_source
        ):

            print(
                "  type = direct_url"
            )

            print(
                "  search_source = None"
            )

            continue

        try:

            search_source = (
                bridge.get_search_source(
                    resolved_source
                )
            )

            print(
                f"  search_source type = "
                f"{type(search_source).__name__}"
            )

            print(
                f"  search_source      = "
                f"{search_source}"
            )

        except Exception as exc:

            print(
                "  ❌ Search source resolution failed"
            )

            print(
                f"  error = {exc}"
            )

    # ==================================================
    #
    # 8. Provider Support Check
    #
    # ==================================================

    print()
    print("[8] Provider Support Check")
    print("-" * 70)

    providers = [
        "google_search",
        "google_news",
        "invalid_provider",
    ]

    for provider_name in providers:

        try:

            supported = (
                bridge.is_supported_provider(
                    provider_name
                )
            )

            print(
                f"  {provider_name:<20} "
                f"supported = {supported}"
            )

        except Exception as exc:

            print(
                f"  {provider_name:<20} "
                f"❌ error = {exc}"
            )

    # ==================================================
    #
    # Finished
    #
    # ==================================================

    print()
    print("=" * 70)
    print("Test Finished")
    print("=" * 70)


# ==================================================
#
# Entry Point
#
# ==================================================

if __name__ == "__main__":

    main()
