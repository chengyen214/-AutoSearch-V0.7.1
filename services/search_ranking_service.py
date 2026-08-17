"""
services/search_ranking_service.py

AutoSearch V4

P2.6 Step 8

Search Ranking Service

Purpose:

    Coordinate all search ranking score calculators.

Current Step:

    P2.6 Step 8 — Ranking Score

Responsibilities:

    1. Keyword Score
    2. Entity Score
    3. Topic Score
    4. Importance Score
    5. Confidence Score
    6. Freshness Score
    7. Ranking Score
    8. Final Search Score
"""


from models.knowledge_search_score import (
    KnowledgeSearchScore
)


from services.ranking.keyword_score import (
    KeywordScoreCalculator
)


from services.ranking.entity_score import (
    EntityScoreCalculator
)


from services.ranking.topic_score import (
    TopicScoreCalculator
)


from services.ranking.importance_score import (
    ImportanceScoreCalculator
)


from services.ranking.confidence_score import (
    ConfidenceScoreCalculator
)


from services.ranking.freshness_score import (
    FreshnessScoreCalculator
)


from services.ranking.ranking_score import (
    RankingScoreCalculator
)


class SearchRankingService:
    """
    Search Result Ranking Service.

    負責統一協調各種 Score Calculator。

    P2.6:

        Step 2 — Keyword Score
        Step 3 — Entity Score
        Step 4 — Topic Score
        Step 5 — Importance Score
        Step 6 — Confidence Score
        Step 7 — Freshness Score
        Step 8 — Ranking Score
    """


    def __init__(self):

        # ==================================
        # Keyword
        # ==================================

        self.keyword_calculator = (

            KeywordScoreCalculator()

        )


        # ==================================
        # Entity
        # ==================================

        self.entity_calculator = (

            EntityScoreCalculator()

        )


        # ==================================
        # Topic
        # ==================================

        self.topic_calculator = (

            TopicScoreCalculator()

        )


        # ==================================
        # Importance
        # ==================================

        self.importance_calculator = (

            ImportanceScoreCalculator()

        )


        # ==================================
        # Confidence
        # ==================================

        self.confidence_calculator = (

            ConfidenceScoreCalculator()

        )


        # ==================================
        # Freshness
        # ==================================

        self.freshness_calculator = (

            FreshnessScoreCalculator()

        )


        # ==================================
        # Ranking
        # ==================================

        self.ranking_calculator = (

            RankingScoreCalculator()

        )


    # ==================================
    # Keyword Score
    # ==================================

    def calculate_keyword_score(
        self,
        query,
        search_index
    ):
        """
        計算 Keyword Score。
        """

        return self.keyword_calculator.calculate(

            query,

            search_index

        )


    def get_keyword_score(
        self,
        query,
        search_index
    ):
        """
        取得 Keyword Score。
        """

        return self.calculate_keyword_score(

            query,

            search_index

        )


    # ==================================
    # Entity Score
    # ==================================

    def calculate_entity_score(
        self,
        query,
        search_index
    ):
        """
        計算 Entity Score。
        """

        return self.entity_calculator.calculate(

            query,

            search_index

        )


    def get_entity_score(
        self,
        query,
        search_index
    ):
        """
        取得 Entity Score。
        """

        return self.calculate_entity_score(

            query,

            search_index

        )


    # ==================================
    # Topic Score
    # ==================================

    def calculate_topic_score(
        self,
        query,
        search_index
    ):
        """
        計算 Topic Score。
        """

        return self.topic_calculator.calculate(

            query,

            search_index

        )


    def get_topic_score(
        self,
        query,
        search_index
    ):
        """
        取得 Topic Score。
        """

        return self.calculate_topic_score(

            query,

            search_index

        )


    # ==================================
    # Importance Score
    # ==================================

    def calculate_importance_score(
        self,
        search_index
    ):
        """
        計算 Importance Score。
        """

        return self.importance_calculator.calculate(

            search_index

        )


    def get_importance_score(
        self,
        search_index
    ):
        """
        取得 Importance Score。
        """

        return self.calculate_importance_score(

            search_index

        )


    # ==================================
    # Confidence Score
    # ==================================

    def calculate_confidence_score(
        self,
        search_index
    ):
        """
        計算 Confidence Score。
        """

        return self.confidence_calculator.calculate(

            search_index

        )


    def get_confidence_score(
        self,
        search_index
    ):
        """
        取得 Confidence Score。
        """

        return self.calculate_confidence_score(

            search_index

        )


    # ==================================
    # Freshness Score
    # ==================================

    def calculate_freshness_score(
        self,
        search_index
    ):
        """
        計算 Freshness Score。
        """

        return self.freshness_calculator.calculate(

            search_index

        )


    def get_freshness_score(
        self,
        search_index
    ):
        """
        取得 Freshness Score。
        """

        return self.calculate_freshness_score(

            search_index

        )


    # ==================================
    # Ranking Score
    # ==================================

    def calculate_ranking_score(
        self,
        search_index
    ):
        """
        計算 Ranking Score。
        """

        return self.ranking_calculator.calculate(

            search_index

        )


    def get_ranking_score(
        self,
        search_index
    ):
        """
        取得 Ranking Score。
        """

        return self.calculate_ranking_score(

            search_index

        )


    # ==================================
    # Build Search Score
    # ==================================

    def build_search_score(
        self,
        query,
        search_index
    ):
        """
        建立 KnowledgeSearchScore。

        P2.6 Step 8:

            Keyword Score
            Entity Score
            Topic Score
            Importance Score
            Confidence Score
            Freshness Score
            Ranking Score

        Final Search Score:

            由 KnowledgeSearchScore
            統一計算。
        """


        # ==================================
        # Keyword
        # ==================================

        keyword_score = (

            self.calculate_keyword_score(

                query,

                search_index

            )

        )


        # ==================================
        # Entity
        # ==================================

        entity_score = (

            self.calculate_entity_score(

                query,

                search_index

            )

        )


        # ==================================
        # Topic
        # ==================================

        topic_score = (

            self.calculate_topic_score(

                query,

                search_index

            )

        )


        # ==================================
        # Importance
        # ==================================

        importance_score = (

            self.calculate_importance_score(

                search_index

            )

        )


        # ==================================
        # Confidence
        # ==================================

        confidence_score = (

            self.calculate_confidence_score(

                search_index

            )

        )


        # ==================================
        # Freshness
        # ==================================

        freshness_score = (

            self.calculate_freshness_score(

                search_index

            )

        )


        # ==================================
        # Ranking
        # ==================================

        ranking_score = (

            self.calculate_ranking_score(

                search_index

            )

        )


        # ==================================
        # Build Result
        # ==================================

        return KnowledgeSearchScore(

            keyword_score=keyword_score,

            entity_score=entity_score,

            topic_score=topic_score,

            importance_score=importance_score,

            confidence_score=confidence_score,

            freshness_score=freshness_score,

            ranking_score=ranking_score

        )
