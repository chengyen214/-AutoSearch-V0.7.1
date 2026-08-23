"""
tests/V5/test_target_source_resolution.py

AutoSearch V5

V5.6.2
Target Source Resolution Test

測試：

    SQL Target
        ↓
    TargetSourceService
        ↓
    Source Definition

目前測試 Target：

    #16 Google News
        search / google_news

    #17 Intel
        url

    #18 TSMC
        url

注意：

    本測試不執行：

        Search
        SearchAdapter
        Crawler
        Parser
        ArticleService
        Archive
        AI
"""

from database.target_repository import TargetRepository
from services.target_source_service import TargetSourceService


# ==================================================
#
# Configuration
#
# ==================================================

TARGET_IDS = [
    16, 17, 18
]


# ==================================================
#
# Main Test
#
# ==================================================

def main():

    print("=" * 70)
    print("AutoSearch V5")
    print("V5.6.2 Target Source Resolution Test")
    print("=" * 70)

    # --------------------------------------------------
    # Target Repository
    # --------------------------------------------------

    repository = TargetRepository()

    # --------------------------------------------------
    # Target Source Service
    # --------------------------------------------------

    service = TargetSourceService()

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
            f"  search_provider  = {target.search_provider}"
        )

    # ==================================================
    #
    # 2. Target → Source Definition
    #
    # ==================================================

    print()
    print("[2] Target → Source Definition")
    print("-" * 70)

    if not targets:

        print(
            "❌ 沒有可測試的 Target"
        )

        return

    for target in targets:

        print()
        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        try:

            source_definition = (
                service.resolve(
                    target
                )
            )

        except Exception as exc:

            print(
                "❌ Source Resolution 失敗"
            )

            print(
                f"  error = {exc}"
            )

            continue

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
            == service.SOURCE_TYPE_SEARCH
        ):

            print(
                f"  keyword     = "
                f"{source_definition.get('keyword')}"
            )

            print(
                f"  provider    = "
                f"{source_definition.get('provider')}"
            )

        elif (
            source_definition.get(
                "source_type"
            )
            == service.SOURCE_TYPE_DIRECT_URL
        ):

            print(
                f"  url         = "
                f"{source_definition.get('url')}"
            )

    # ==================================================
    #
    # 3. Provider Check
    #
    # ==================================================

    print()
    print("[3] Provider Check")
    print("-" * 70)

    for target in targets:

        if not service.is_search_target(
            target
        ):

            print(
                f"Target #{target.id} "
                f"({target.name})"
            )

            print(
                "  type = direct_url"
            )

            print(
                "  provider = None"
            )

            continue

        provider = service.get_provider(
            target
        )

        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        print(
            f"  provider = {provider}"
        )

        print(
            f"  supported = "
            f"{service.is_supported_provider(provider)}"
        )

    # ==================================================
    #
    # 4. Target Type Check
    #
    # ==================================================

    print()
    print("[4] Target Type Check")
    print("-" * 70)

    for target in targets:

        is_url = service.is_url_target(
            target
        )

        is_search = service.is_search_target(
            target
        )

        source_type = service.get_source_type(
            target
        )

        print(
            f"Target #{target.id} "
            f"({target.name})"
        )

        print(
            f"  is_url_target    = {is_url}"
        )

        print(
            f"  is_search_target = {is_search}"
        )

        print(
            f"  source_type      = {source_type}"
        )

    # ==================================================
    #
    # 5. Google News Check
    #
    # ==================================================

    print()
    print("[5] Google News Check")
    print("-" * 70)

    for target in targets:

        if service.is_google_news(
            target
        ):

            print(
                f"Target #{target.id} "
                f"({target.name})"
            )

            print(
                "  ✅ Google News Target"
            )

            resolved = (
                service.resolve_google_news(
                    target
                )
            )

            print(
                f"  resolved = {resolved}"
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
