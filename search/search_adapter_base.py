"""
search/search_adapter_base.py

AutoSearch V4

P4 Data Sources

Search Adapter Base Interface

用途:

1. 定義所有 Search Adapter 共用介面
2. 避免 Search Adapter 之間循環 import
3. 統一 Search Adapter API

注意:

本模組只負責:

    SearchAdapter Interface

不負責:

- Google News
- TSMC
- HTML Download
- Parser
- Archive
- AI
- Database
"""


class SearchAdapter:
    """
    Search Adapter 基礎介面。

    所有 Search Source Adapter
    都應實作:

        search(
            keyword,
            max_results
        )

    並回傳:

        list[SearchResult]
    """

    # ----------------------------------------------
    # Default Result Limit
    # ----------------------------------------------

    max_results = 10

    # ----------------------------------------------
    # Search Source Name
    # ----------------------------------------------

    search_source = ""

    # ==================================================
    #
    # Search
    #
    # ==================================================

    def search(
        self,
        keyword,
        max_results=None,
    ):
        """
        執行搜尋。

        子類別必須實作。
        """

        raise NotImplementedError(
            "SearchAdapter.search() "
            "must be implemented"
        )


__all__ = [
    "SearchAdapter",
]