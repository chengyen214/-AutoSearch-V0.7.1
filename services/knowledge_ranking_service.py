"""
services/knowledge_ranking_service.py

AutoSearch V4

P3.7

Knowledge Ranking Service


功能:

1. Ranking Score Calculation
2. Top Ranking Knowledge
3. Score Filter
4. Ranking Retrieval
5. Knowledge Score Retrieval
6. Score Update


Architecture:

API
 ↓
KnowledgeRankingService
 ↓
KnowledgeScoreRepository
 ↓
knowledge_scores


"""


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)


class KnowledgeRankingService:
    """
    Knowledge Ranking Service

    負責 Knowledge Ranking
    與 Ranking Score 計算。
    """

    # ==================================================
    # Initialization
    # ==================================================

    def __init__(
        self,
        repository=None
    ):

        self.repository = (

            repository

            if repository is not None

            else KnowledgeScoreRepository()

        )

    # ==================================================
    # Ranking Calculation
    #
    # P3.7.1
    # ==================================================

    def calculate_ranking(
        self,
        importance,
        confidence,
        quality_score,
        freshness_score
    ):
        """
        計算 Knowledge Ranking Score。

        Score 統一轉換成 0 ~ 10。

        權重:

            Importance      30%
            Confidence      20%
            Quality         25%
            Freshness       25%

        importance:
            0 ~ 10

        confidence:
            0.0 ~ 1.0

        quality_score:
            0 ~ 10

        freshness_score:
            0 ~ 10
        """

        importance_score = (
            float(importance)
        )

        confidence_score = (
            float(confidence) * 10
        )

        quality = (
            float(quality_score)
        )

        freshness = (
            float(freshness_score)
        )

        ranking_score = (

            importance_score * 0.30

            +

            confidence_score * 0.20

            +

            quality * 0.25

            +

            freshness * 0.25

        )

        return round(
            ranking_score,
            4
        )

    # ==================================================
    # Top Ranking
    #
    # P3.7.2
    # ==================================================

    def get_top_ranking(
        self,
        limit=10
    ):
        """
        取得最高 Ranking Score。
        """

        return self.repository.top_ranking(
            limit
        )

    # ==================================================
    # Score Filter
    #
    # P3.7.3
    # ==================================================

    def find_by_score(
        self,
        score
    ):
        """
        查詢指定 Ranking Score
        以上的 Knowledge。
        """

        return self.repository.find_by_score(
            score
        )

    # ==================================================
    # Get Score
    #
    # P3.7.4
    # ==================================================

    def get_score(
        self,
        knowledge_id
    ):
        """
        取得指定 Knowledge Score。
        """

        return self.repository.get_by_knowledge_id(
            knowledge_id
        )

    # ==================================================
    # Has Score
    #
    # P3.7.5
    # ==================================================

    def has_score(
        self,
        knowledge_id
    ):
        """
        判斷 Knowledge 是否已有 Score。
        """

        return self.repository.exists(
            knowledge_id
        )

    # ==================================================
    # Update Score
    #
    # P3.7.6
    # ==================================================

    def update_score(
        self,
        knowledge_id,
        score
    ):
        """
        更新 Knowledge Score。
        """

        self.repository.update(
            knowledge_id,
            score
        )

        return score

    # ==================================================
    # Ranking Retrieval
    #
    # P3.7.7
    # ==================================================

    def get_ranking(
        self,
        limit=10
    ):
        """
        Ranking Retrieval。
        """

        return self.get_top_ranking(
            limit
        )