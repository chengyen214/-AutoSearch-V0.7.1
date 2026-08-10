"""
archive/knowledge_history.py

AutoSearch V4

P2.3.8 Knowledge History

用途:

    追蹤 Article 在不同 Archive Version
    中的 Knowledge 演變。

功能:

    1. 取得 Article Knowledge History
    2. 取得最新 Knowledge
    3. 取得第一筆 Knowledge
    4. 取得指定 Version Knowledge
    5. 取得 Knowledge Timeline
    6. 比較兩個 Version 的 Knowledge
    7. 取得 Category 演變
    8. 取得 Keywords 演變
    9. 取得 Importance History
    10. 取得 Confidence History
    11. 判斷是否存在 Knowledge History
    12. 計算 Knowledge History 數量
    13. 取得完整 Knowledge Evolution

設計:

    Repository
          ↓
    KnowledgeHistory
          ↓
    Knowledge History Engine

注意:

    本模組不直接操作 Database。
"""

from models.knowledge_history import KnowledgeHistory


class KnowledgeHistoryEngine:

    """
    Knowledge History Engine
    """

    # ==================================
    # Init
    # ==================================

    def __init__(
        self,
        knowledge_repository=None
    ):

        self.knowledge_repository = (
            knowledge_repository
        )

    # ==================================
    # Internal Repository
    # ==================================

    def _get_repository(self):

        """
        取得 Knowledge Repository。
        """

        if self.knowledge_repository is None:

            from database.knowledge_repository import (
                KnowledgeRepository
            )

            self.knowledge_repository = (
                KnowledgeRepository()
            )

        return self.knowledge_repository

    # ==================================
    # Convert
    # ==================================

    @staticmethod
    def _to_model(
        knowledge,
        article_id=None,
        version_id=None,
        version_number=None
    ):

        """
        將 Repository 回傳資料轉成
        KnowledgeHistory Model。
        """

        if knowledge is None:

            return None

        # ----------------------------------
        # Already Model
        # ----------------------------------

        if isinstance(
            knowledge,
            KnowledgeHistory
        ):

            return knowledge

        # ----------------------------------
        # Dictionary
        # ----------------------------------

        if isinstance(
            knowledge,
            dict
        ):

            return KnowledgeHistory(

                article_id=(
                    knowledge.get(
                        "article_id",
                        article_id
                    )
                ),

                version_id=(
                    knowledge.get(
                        "version_id",
                        version_id
                    )
                ),

                version_number=(
                    knowledge.get(
                        "version_number",
                        version_number
                    )
                ),

                summary=knowledge.get(
                    "summary",
                    ""
                ),

                category=knowledge.get(
                    "category",
                    ""
                ),

                keywords=knowledge.get(
                    "keywords",
                    []
                ),

                importance=knowledge.get(
                    "importance",
                    0
                ),

                confidence=knowledge.get(
                    "confidence",
                    0.0
                ),

                analyze_time=knowledge.get(
                    "analyze_time"
                )
            )

        # ----------------------------------
        # Object
        # ----------------------------------

        return KnowledgeHistory(

            article_id=(
                getattr(
                    knowledge,
                    "article_id",
                    article_id
                )
            ),

            version_id=(
                getattr(
                    knowledge,
                    "version_id",
                    version_id
                )
            ),

            version_number=(
                getattr(
                    knowledge,
                    "version_number",
                    version_number
                )
            ),

            summary=(
                getattr(
                    knowledge,
                    "summary",
                    ""
                )
            ),

            category=(
                getattr(
                    knowledge,
                    "category",
                    ""
                )
            ),

            keywords=(
                getattr(
                    knowledge,
                    "keywords",
                    []
                )
            ),

            importance=(
                getattr(
                    knowledge,
                    "importance",
                    0
                )
            ),

            confidence=(
                getattr(
                    knowledge,
                    "confidence",
                    0.0
                )
            ),

            analyze_time=(
                getattr(
                    knowledge,
                    "analyze_time",
                    None
                )
            )
        )

    # ==================================
    # Get History
    # ==================================

    def get_history(
        self,
        article_id
    ):

        """
        取得 Article 完整 Knowledge History。
        """

        repository = self._get_repository()

        # ----------------------------------
        # Preferred Repository API
        # ----------------------------------

        if hasattr(
            repository,
            "get_history"
        ):

            results = repository.get_history(
                article_id
            )

        # ----------------------------------
        # Compatibility API
        # ----------------------------------

        elif hasattr(
            repository,
            "get_by_article_id"
        ):

            results = repository.get_by_article_id(
                article_id
            )

        else:

            return []

        if results is None:

            return []

        return [

            self._to_model(
                item,
                article_id=article_id
            )

            for item in results
        ]

    # ==================================
    # Get Latest
    # ==================================

    def get_latest(
        self,
        article_id
    ):

        """
        取得最新 Knowledge。
        """

        history = self.get_history(
            article_id
        )

        if not history:

            return None

        return max(

            history,

            key=lambda item: (

                item.version_number

                if item.version_number is not None

                else 0
            )
        )

    # ==================================
    # Get First
    # ==================================

    def get_first(
        self,
        article_id
    ):

        """
        取得第一筆 Knowledge。
        """

        history = self.get_history(
            article_id
        )

        if not history:

            return None

        return min(

            history,

            key=lambda item: (

                item.version_number

                if item.version_number is not None

                else 0
            )
        )

    # ==================================
    # Get Version
    # ==================================

    def get_version(
        self,
        article_id,
        version_number
    ):

        """
        取得指定 Version 的 Knowledge。
        """

        history = self.get_history(
            article_id
        )

        for item in history:

            if (
                item.version_number
                == version_number
            ):

                return item

        return None

    # ==================================
    # Get Version By ID
    # ==================================

    def get_version_by_id(
        self,
        version_id
    ):

        """
        依 Version ID 取得 Knowledge。
        """

        repository = self._get_repository()

        if hasattr(
            repository,
            "get_by_version_id"
        ):

            result = repository.get_by_version_id(
                version_id
            )

            return self._to_model(
                result,
                version_id=version_id
            )

        if hasattr(
            repository,
            "get_version_by_id"
        ):

            result = repository.get_version_by_id(
                version_id
            )

            return self._to_model(
                result,
                version_id=version_id
            )

        return None

    # ==================================
    # Get Timeline
    # ==================================

    def get_timeline(
        self,
        article_id
    ):

        """
        取得 Knowledge Timeline。

        按 Version Number
        由舊到新排序。
        """

        history = self.get_history(
            article_id
        )

        return sorted(

            history,

            key=lambda item: (

                item.version_number

                if item.version_number is not None

                else 0
            )
        )

    # ==================================
    # Get Changes
    # ==================================

    def get_changes(
        self,
        old_knowledge,
        new_knowledge
    ):

        """
        比較兩筆 Knowledge。

        回傳:

            summary_changed
            category_changed
            keywords_added
            keywords_removed
            importance_changed
            confidence_changed
        """

        old = self._to_model(
            old_knowledge
        )

        new = self._to_model(
            new_knowledge
        )

        if old is None or new is None:

            return {

                "summary_changed": False,

                "category_changed": False,

                "keywords_added": [],

                "keywords_removed": [],

                "importance_changed": False,

                "confidence_changed": False
            }

        old_keywords = set(
            old.keywords
        )

        new_keywords = set(
            new.keywords
        )

        return {

            "summary_changed": (
                old.summary
                != new.summary
            ),

            "category_changed": (
                old.category
                != new.category
            ),

            "keywords_added": sorted(
                new_keywords
                - old_keywords
            ),

            "keywords_removed": sorted(
                old_keywords
                - new_keywords
            ),

            "importance_changed": (
                old.importance
                != new.importance
            ),

            "confidence_changed": (
                old.confidence
                != new.confidence
            )
        }

    # ==================================
    # Get Categories
    # ==================================

    def get_categories(
        self,
        article_id
    ):

        """
        取得 Category 演變。
        """

        history = self.get_timeline(
            article_id
        )

        return [

            {
                "version_number":
                    item.version_number,

                "category":
                    item.category
            }

            for item in history
        ]

    # ==================================
    # Get Keywords
    # ==================================

    def get_keywords(
        self,
        article_id
    ):

        """
        取得 Keywords 演變。
        """

        history = self.get_timeline(
            article_id
        )

        return [

            {
                "version_number":
                    item.version_number,

                "keywords":
                    list(item.keywords)
            }

            for item in history
        ]

    # ==================================
    # Get Importance History
    # ==================================

    def get_importance_history(
        self,
        article_id
    ):

        """
        取得 Importance 演變。
        """

        history = self.get_timeline(
            article_id
        )

        return [

            {
                "version_number":
                    item.version_number,

                "importance":
                    item.importance
            }

            for item in history
        ]

    # ==================================
    # Get Confidence History
    # ==================================

    def get_confidence_history(
        self,
        article_id
    ):

        """
        取得 Confidence 演變。
        """

        history = self.get_timeline(
            article_id
        )

        return [

            {
                "version_number":
                    item.version_number,

                "confidence":
                    item.confidence
            }

            for item in history
        ]

    # ==================================
    # Has History
    # ==================================

    def has_history(
        self,
        article_id
    ):

        """
        判斷 Article 是否存在
        Knowledge History。
        """

        return (
            self.count(article_id)
            > 0
        )

    # ==================================
    # Count
    # ==================================

    def count(
        self,
        article_id
    ):

        """
        計算 Knowledge History 數量。
        """

        return len(
            self.get_history(
                article_id
            )
        )

    # ==================================
    # Get Knowledge Evolution
    # ==================================

    def get_knowledge_evolution(
        self,
        article_id
    ):

        """
        取得完整 Knowledge Evolution。

        包含:

            Version
            Summary
            Category
            Keywords
            Importance
            Confidence
        """

        history = self.get_timeline(
            article_id
        )

        return [

            item.to_dict()

            for item in history
        ]

    # ==================================
    # Repr
    # ==================================

    def __repr__(self):

        return (
            "KnowledgeHistoryEngine("
            f"repository="
            f"{self.knowledge_repository!r}"
            ")"
        )