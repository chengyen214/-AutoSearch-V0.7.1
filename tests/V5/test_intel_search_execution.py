"""
tests/V5/test_intel_search_execution.py

AutoSearch V5

V5.6.3

Intel Target Search Execution Test

測試：

    SQL Target #17 Intel
        ↓
    TargetSourceService
        ↓
    Source Definition
        ↓
    SourceResolutionBridge
        ↓
    Resolved Source
        ↓
    GoogleSearchProvider
        ↓
    ProviderSearchAdapter
        ↓
    SearchExecutionBridge
        ↓
    SerpApi
        ↓
    SearchResult[]

本測試：

    ✅ 從 SQL 取得 Intel Target #17
    ✅ 確認 Target 設定
    ✅ Target → Source Definition
    ✅ 確認 search source
    ✅ 確認 Intel site
    ✅ Source Definition → Resolved Source
    ✅ 確認 Google Search Provider
    ✅ 確認 Provider Adapter
    ✅ 確認 Search Site
    ✅ 真正執行 Search
    ✅ 確認 SearchResult
    ✅ 確認 SearchResult 使用 google_search

不測試：

    ❌ website_search
    ❌ Crawl
    ❌ Parser
    ❌ ArticleService
    ❌ Archive
    ❌ AI
"""


# ==================================================
#
# Imports
#
# ==================================================

from database.target_repository import (
    TargetRepository,
)

from services.target_source_service import (
    TargetSourceService,
)

from services.source_resolution_bridge import (
    SourceResolutionBridge,
)

from services.search_execution_bridge import (
    SearchExecutionBridge,
)

from models.search_result import (
    SearchResult,
)


# ==================================================
#
# Configuration
#
# ==================================================

TARGET_ID = 17

EXPECTED_NAME = "Intel"

EXPECTED_KEYWORD = (
    "IC semiconductor"
)

EXPECTED_URL = (
    "https://www.intel.com/"
)

EXPECTED_PROVIDER = (
    "google_search"
)

EXPECTED_SOURCE_TYPE = (
    "search"
)


# ==================================================
#
# Main Test
#
# ==================================================

def main():

    print("=" * 70)
    print("AutoSearch V5")
    print("V5.6.3 Intel Search Execution Test")
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
    # 1. SQL → Target
    #
    # ==================================================

    print()
    print("[1] 從 SQL 取得 Intel Target")
    print("-" * 70)

    target = (
        target_repository.get_by_id(
            TARGET_ID
        )
    )

    assert target is not None, (
        f"Target #{TARGET_ID} 不存在"
    )

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

    # ==================================================
    #
    # 2. Target Validation
    #
    # ==================================================

    print()
    print("[2] Intel Target Validation")
    print("-" * 70)

    assert target.name == EXPECTED_NAME

    assert target.target_type == "url"

    assert target.url == EXPECTED_URL

    assert target.keyword == EXPECTED_KEYWORD

    assert (
        target.search_provider
        == EXPECTED_PROVIDER
    )

    print(
        "  ✅ Target configuration correct"
    )

    # ==================================================
    #
    # 3. Target → Source Definition
    #
    # ==================================================

    print()
    print("[3] Target → Source Definition")
    print("-" * 70)

    source_definition = (
        target_source_service.resolve(
            target
        )
    )

    assert source_definition is not None

    print(
        f"  source_type = "
        f"{source_definition.get('source_type')}"
    )

    print(
        f"  target_type = "
        f"{source_definition.get('target_type')}"
    )

    print(
        f"  site        = "
        f"{source_definition.get('site')}"
    )

    print(
        f"  keyword     = "
        f"{source_definition.get('keyword')}"
    )

    print(
        f"  provider    = "
        f"{source_definition.get('provider')}"
    )

    # --------------------------------------------------
    #
    # Source Type
    #
    # --------------------------------------------------

    assert (
        source_definition.get(
            "source_type"
        )
        == EXPECTED_SOURCE_TYPE
    )

    # --------------------------------------------------
    #
    # Target Type
    #
    # --------------------------------------------------

    assert (
        source_definition.get(
            "target_type"
        )
        == "url"
    )

    # --------------------------------------------------
    #
    # Site
    #
    # --------------------------------------------------

    assert (
        source_definition.get(
            "site"
        )
        == EXPECTED_URL
    )

    # --------------------------------------------------
    #
    # Keyword
    #
    # --------------------------------------------------

    assert (
        source_definition.get(
            "keyword"
        )
        == EXPECTED_KEYWORD
    )

    # --------------------------------------------------
    #
    # Provider
    #
    # --------------------------------------------------

    assert (
        source_definition.get(
            "provider"
        )
        == EXPECTED_PROVIDER
    )

    print(
        "  ✅ Source Definition correct"
    )

    # ==================================================
    #
    # 4. Source Definition → Resolved Source
    #
    # ==================================================

    print()
    print("[4] Source Definition → Resolved Source")
    print("-" * 70)

    resolved_source = (
        source_resolution_bridge.resolve(
            source_definition
        )
    )

    assert resolved_source is not None

    print(
        f"  resolved_type = "
        f"{type(resolved_source).__name__}"
    )

    print(
        f"  resolved      = "
        f"{resolved_source}"
    )

    # ==================================================
    #
    # 5. Resolved Source Validation
    #
    # ==================================================

    print()
    print("[5] Resolved Source Validation")
    print("-" * 70)

    is_search = (
        source_resolution_bridge.is_search(
            resolved_source
        )
    )

    print(
        f"  is_search = {is_search}"
    )

    assert is_search is True

    # --------------------------------------------------
    #
    # Provider
    #
    # --------------------------------------------------

    provider = (
        source_resolution_bridge.get_provider(
            resolved_source
        )
    )

    print(
        f"  provider type = "
        f"{type(provider).__name__}"
    )

    assert provider is not None

    assert (
        getattr(
            provider,
            "provider_name",
            None,
        )
        == EXPECTED_PROVIDER
    )

    # --------------------------------------------------
    #
    # Adapter
    #
    # --------------------------------------------------

    adapter = (
        source_resolution_bridge.get_adapter(
            resolved_source
        )
    )

    print(
        f"  adapter type  = "
        f"{type(adapter).__name__}"
    )

    assert adapter is not None

    # --------------------------------------------------
    #
    # Site
    #
    # --------------------------------------------------

    search_site = (
        source_resolution_bridge.get_site(
            resolved_source
        )
    )

    print(
        f"  search_site   = "
        f"{search_site}"
    )

    assert (
        search_site
        == EXPECTED_URL
    )

    print(
        "  ✅ Resolved Source correct"
    )

    # ==================================================
    #
    # 6. Search Execution
    #
    # ==================================================

    print()
    print("[6] Search Execution")
    print("-" * 70)

    print(
        f"  target   = #{target.id} "
        f"{target.name}"
    )

    print(
        f"  keyword  = {target.keyword}"
    )

    print(
        f"  site     = {target.url}"
    )

    print(
        f"  provider = "
        f"{target.search_provider}"
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
    # 7. Search Result Validation
    #
    # ==================================================

    print()
    print("[7] Search Result Validation")
    print("-" * 70)

    assert search_results is not None

    search_results = list(
        search_results
    )

    print(
        f"  total results = "
        f"{len(search_results)}"
    )

    assert len(search_results) > 0, (
        "Intel Search 沒有回傳任何結果"
    )

    # ==================================================
    #
    # 8. SearchResult Validation
    #
    # ==================================================

    print()
    print("[8] SearchResult Validation")
    print("-" * 70)

    for index, result in enumerate(
        search_results,
        start=1,
    ):

        print(
            f"Result #{index}"
        )

        print(
            f"  type     = "
            f"{type(result).__name__}"
        )

        assert isinstance(
            result,
            SearchResult,
        )

        assert result.url

        assert (
            result.keyword
            == EXPECTED_KEYWORD
        )

        assert result.rank > 0

        print(
            f"  title    = "
            f"{result.title}"
        )

        print(
            f"  url      = "
            f"{result.url}"
        )

        print(
            f"  source   = "
            f"{result.source}"
        )

        print(
            f"  rank     = "
            f"{result.rank}"
        )

        print(
            f"  provider = "
            f"{result.search_source}"
        )

        # --------------------------------------------------
        #
        # Provider Validation
        #
        # --------------------------------------------------

        assert (
            result.search_source
            == EXPECTED_PROVIDER
        )

        print(
            "  ✅ SearchResult correct"
        )

        print()

    # ==================================================
    #
    # 9. Intel Search Result Summary
    #
    # ==================================================

    print()
    print("[9] Intel Search Result Summary")
    print("-" * 70)

    intel_results = [

        result

        for result in search_results

        if "intel.com"
        in result.url.lower()

    ]

    print(
        f"  Intel domain results = "
        f"{len(intel_results)}"
    )

    for result in intel_results:

        print(
            f"  ✓ {result.url}"
        )

    # --------------------------------------------------
    #
    # Important:
    #
    # Google Search Provider 已經使用
    #
    #     site:intel.com
    #
    # 進行搜尋。
    #
    # 但 SerpApi / Google 的實際
    # organic_results 仍可能包含
    # 非 Intel domain 的結果。
    #
    # 因此這裡不把每一筆結果
    # 強制 assert 為 intel.com。
    #
    # --------------------------------------------------

    # ==================================================
    #
    # Finished
    #
    # ==================================================

    print("=" * 70)
    print(
        "Intel Search Execution Test PASSED"
    )
    print("=" * 70)


# ==================================================
#
# Pytest Entry
#
# ==================================================

def test_intel_search_execution():

    main()


# ==================================================
#
# Direct Execution
#
# ==================================================

if __name__ == "__main__":

    main()