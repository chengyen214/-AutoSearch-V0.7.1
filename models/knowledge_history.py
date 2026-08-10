"""
models/knowledge_history.py

AutoSearch V4

P2.3.8 Knowledge History

用途:

    儲存 Article 在不同 Archive Version
    的 Knowledge 演變資訊。

功能:

    1. 儲存 Article ID
    2. 儲存 Version 資訊
    3. 儲存 Knowledge Summary
    4. 儲存 Category
    5. 儲存 Keywords
    6. 儲存 Importance
    7. 儲存 Confidence
    8. 判斷是否有 Knowledge
    9. 計算 Knowledge 變化
    10. 產生 Dictionary

設計:

    Archive Version
            ↓
    Knowledge History
            ↓
    Knowledge Evolution

注意:

    本 Model 不直接操作 Database。
"""


class KnowledgeHistory:

    """
    Knowledge History Model
    """

    # ==================================
    # Init
    # ==================================

    def __init__(
        self,
        article_id=None,
        version_id=None,
        version_number=None,
        summary="",
        category="",
        keywords=None,
        importance=0,
        confidence=0.0,
        analyze_time=None
    ):

        self.article_id = article_id

        self.version_id = version_id

        self.version_number = version_number

        self.summary = (
            summary
            if summary is not None
            else ""
        )

        self.category = (
            category
            if category is not None
            else ""
        )

        self.keywords = (
            list(keywords)
            if keywords is not None
            else []
        )

        self.importance = (
            importance
            if importance is not None
            else 0
        )

        self.confidence = (
            confidence
            if confidence is not None
            else 0.0
        )

        self.analyze_time = analyze_time

    # ==================================
    # Has Knowledge
    # ==================================

    def has_knowledge(self):

        """
        判斷是否存在 Knowledge。
        """

        return bool(
            self.summary
            or self.category
            or self.keywords
        )

    # ==================================
    # Has Summary
    # ==================================

    def has_summary(self):

        """
        判斷是否存在 Summary。
        """

        return bool(
            self.summary
        )

    # ==================================
    # Has Category
    # ==================================

    def has_category(self):

        """
        判斷是否存在 Category。
        """

        return bool(
            self.category
        )

    # ==================================
    # Has Keywords
    # ==================================

    def has_keywords(self):

        """
        判斷是否存在 Keywords。
        """

        return bool(
            self.keywords
        )

    # ==================================
    # Keyword Count
    # ==================================

    def keyword_count(self):

        """
        取得 Keyword 數量。
        """

        return len(
            self.keywords
        )

    # ==================================
    # Knowledge Score
    # ==================================

    def knowledge_score(self):

        """
        計算簡單 Knowledge Score。

        Importance:
            0 ~ 10

        Confidence:
            0.0 ~ 1.0

        Score:
            Importance × Confidence
        """

        return (
            self.importance
            * self.confidence
        )

    # ==================================
    # To Dict
    # ==================================

    def to_dict(self):

        """
        將 Knowledge History
        轉換成 Dictionary。
        """

        return {

            "article_id":
                self.article_id,

            "version_id":
                self.version_id,

            "version_number":
                self.version_number,

            "summary":
                self.summary,

            "category":
                self.category,

            "keywords":
                list(self.keywords),

            "importance":
                self.importance,

            "confidence":
                self.confidence,

            "analyze_time":
                self.analyze_time
        }

    # ==================================
    # Summary
    # ==================================

    def summary_text(self):

        """
        取得 Knowledge 摘要。
        """

        if self.summary:

            return self.summary

        return ""

    # ==================================
    # Repr
    # ==================================

    def __repr__(self):

        return (
            "KnowledgeHistory("
            f"article_id={self.article_id}, "
            f"version_id={self.version_id}, "
            f"version_number={self.version_number}, "
            f"category={self.category!r}, "
            f"importance={self.importance}, "
            f"confidence={self.confidence}"
            ")"
        )