"""
services/knowledge_score_service.py

AutoSearch V4

P3.7

Knowledge Score Service

用途:

    Knowledge Score 管理服務

負責:

    1. Knowledge Score 建立
    2. Knowledge Score 查詢
    3. Top Ranking
    4. Score Filter
    5. Knowledge Score 更新
    6. Exists 檢查

Architecture:

    Knowledge Score API
            |
            v
    KnowledgeScoreService
            |
            v
    KnowledgeScoreRepository
            |
            v
    knowledge_scores
"""


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)


from models.knowledge_score import (
    KnowledgeScore
)


class KnowledgeScoreService:
    """
    Knowledge Score Service

    負責：

        API Router
            |
            v
        Service
            |
            v
        Repository

    """

    def __init__(self):

        self.repository = (
            KnowledgeScoreRepository()
        )

    # ==================================
    # Create
    # ==================================

    def create(
        self,
        score
    ):
        """
        建立 Knowledge Score。

        Args:

            score:
                KnowledgeScore

        Returns:

            KnowledgeScore
        """

        if score is None:

            return None

        return self.repository.insert(
            score
        )

    # ==================================
    # Get By Knowledge ID
    # ==================================

    def get_by_knowledge_id(
        self,
        knowledge_id
    ):
        """
        取得指定 Knowledge 的 Score。

        Args:

            knowledge_id:
                Knowledge Archive ID

        Returns:

            Knowledge Score
            或 None
        """

        return self.repository.get_by_knowledge_id(
            knowledge_id
        )

    # ==================================
    # Top Ranking
    # ==================================

    def top_ranking(
        self,
        limit=10
    ):
        """
        取得 Ranking Score 最高的 Knowledge。

        Args:

            limit:
                最大筆數

        Returns:

            Knowledge Score List
        """

        return self.repository.top_ranking(
            limit
        )

    # ==================================
    # Score Filter
    # ==================================

    def find_by_score(
        self,
        score
    ):
        """
        取得指定 Ranking Score 以上的 Knowledge。

        Args:

            score:
                最低 ranking_score

        Returns:

            Knowledge Score List
        """

        return self.repository.find_by_score(
            score
        )

    # ==================================
    # Update
    # ==================================

    def update(
        self,
        knowledge_id,
        score
    ):
        """
        更新指定 Knowledge 的 Score。

        Args:

            knowledge_id:
                Knowledge Archive ID

            score:
                KnowledgeScore

        Returns:

            bool

        """

        if score is None:

            return False

        return self.repository.update(
            knowledge_id,
            score
        )

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        knowledge_id
    ):
        """
        檢查指定 Knowledge 是否已有 Score。

        Returns:

            bool
        """

        return self.repository.exists(
            knowledge_id
        )
