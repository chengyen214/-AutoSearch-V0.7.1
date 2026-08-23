"""
tests/V5/test_target_source_service.py

AutoSearch V5

V5.6.2 / V5.6.3
Target Source Service Test

測試：

    Target
        ↓
    TargetSourceService
        ↓
    Source Definition

目前 Source Resolution 規則：

    Search Target
        → search

    URL Target + keyword
        → website_search

    URL Target + 無 keyword
        → direct_url

測試 Target：

    #16 Google News
        → search

    #17 Intel
        → website_search

    #18 TSMC
        → website_search
"""

from database.target_repository import TargetRepository
from services.target_source_service import TargetSourceService


# ==================================================
#
# Test Header
#
# ==================================================

print("=" * 70)
print("AutoSearch V5")
print("V5.6.2 / V5.6.3 Target Source Service Test")
print("=" * 70)


# ==================================================
#
# Repository
#
# ==================================================

target_repository = TargetRepository()

service = TargetSourceService()


# ==================================================
#
# Target IDs
#
# ==================================================

target_ids = [
    16,  # Google News
    17,  # Intel
    18,  # TSMC
]


# ==================================================
#
# [1] 從 SQL 取得 Target
#
# ==================================================

print()
print("[1] 從 SQL 取得 Target")
print("-" * 70)


targets = []

for target_id in target_ids:

    target = target_repository.get_by_id(
        target_id
    )

    if target is None:

        print(
            f"❌ Target #{target_id} 不存在"
        )

        continue

    targets.append(target)

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
# [2] Target → Source Definition
#
# ==================================================

print()
print("[2] Target → Source Definition")
print("-" * 70)


for target in targets:

    print()

    print(
        f"Target #{target.id} ({target.name})"
    )

    try:

        source = service.resolve(
            target
        )

        print(
            "  ✅ Source Definition resolved"
        )

        print(
            f"  source_type = "
            f"{source.get('source_type')}"
        )

        print(
            f"  target_type = "
            f"{source.get('target_type')}"
        )

        if source.get("url"):

            print(
                f"  url         = "
                f"{source.get('url')}"
            )

        if source.get("keyword"):

            print(
                f"  keyword     = "
                f"{source.get('keyword')}"
            )

        if source.get("provider"):

            print(
                f"  provider    = "
                f"{source.get('provider')}"
            )

    except Exception as e:

        print(
            f"  ❌ Resolution failed: {e}"
        )


# ==================================================
#
# [3] Source Type Check
#
# ==================================================

print()
print("[3] Source Type Check")
print("-" * 70)


for target in targets:

    print()

    print(
        f"Target #{target.id} ({target.name})"
    )

    try:

        source_type = (
            service.get_source_type(
                target
            )
        )

        print(
            f"  source_type = {source_type}"
        )

        if source_type == "website_search":

            print(
                "  ✅ Website Search"
            )

        elif source_type == "direct_url":

            print(
                "  ✅ Direct URL"
            )

        elif source_type == "search":

            print(
                "  ✅ Search Provider"
            )

        else:

            print(
                "  ⚠️ Unknown source type"
            )

    except Exception as e:

        print(
            f"  ❌ Source type check failed: {e}"
        )


# ==================================================
#
# [4] Direct URL Check
#
# ==================================================

print()
print("[4] Direct URL Check")
print("-" * 70)


for target in targets:

    if not service.is_url_target(
        target
    ):

        continue

    print()

    print(
        f"Target #{target.id} ({target.name})"
    )

    result = (
        service.is_direct_url_target(
            target
        )
    )

    print(
        f"  is_direct_url_target = {result}"
    )

    if result:

        print(
            "  ✅ URL without Keyword → Direct URL"
        )

    else:

        print(
            "  → URL + Keyword → Website Search"
        )


# ==================================================
#
# [5] Website Search Check
#
# ==================================================

print()
print("[5] Website Search Check")
print("-" * 70)


for target in targets:

    if not service.is_url_target(
        target
    ):

        continue

    print()

    print(
        f"Target #{target.id} ({target.name})"
    )

    result = (
        service.is_website_search_target(
            target
        )
    )

    print(
        f"  is_website_search_target = "
        f"{result}"
    )

    if result:

        print(
            "  ✅ URL + Keyword → Website Search"
        )

    else:

        print(
            "  → URL without Keyword → Direct URL"
        )


# ==================================================
#
# [6] Provider Check
#
# ==================================================

print()
print("[6] Provider Check")
print("-" * 70)


for target in targets:

    print()

    print(
        f"Target #{target.id} ({target.name})"
    )

    if service.is_search_target(
        target
    ):

        provider = service.get_provider(
            target
        )

        supported = (
            service.is_supported_provider(
                provider
            )
        )

        print(
            f"  provider  = {provider}"
        )

        print(
            f"  supported = {supported}"
        )

    else:

        print(
            "  type = "
            f"{service.get_source_type(target)}"
        )

        print(
            "  provider = None"
        )


# ==================================================
#
# [7] Expected Architecture Check
#
# ==================================================

print()
print("[7] Expected Architecture Check")
print("-" * 70)


for target in targets:

    source = service.resolve(
        target
    )

    source_type = source.get(
        "source_type"
    )

    print()

    print(
        f"Target #{target.id} "
        f"({target.name})"
    )

    # ----------------------------------------------
    # Expected Architecture
    #
    # Search Target
    #     → search
    #
    # URL + Keyword
    #     → website_search
    #
    # URL + No Keyword
    #     → direct_url
    # ----------------------------------------------

    if service.is_search_target(
        target
    ):

        expected = "search"

    elif service.is_website_search_target(
        target
    ):

        expected = "website_search"

    elif service.is_direct_url_target(
        target
    ):

        expected = "direct_url"

    else:

        expected = None

    print(
        f"  expected = {expected}"
    )

    print(
        f"  actual   = {source_type}"
    )

    if source_type == expected:

        print(
            "  ✅ Architecture correct"
        )

    else:

        print(
            "  ❌ Architecture mismatch"
        )


# ==================================================
#
# Finished
#
# ==================================================

print()
print("=" * 70)
print("Target Source Service Test Finished")
print("=" * 70)
