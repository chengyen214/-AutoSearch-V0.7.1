"""
services/retrieval_service.py

AutoSearch V4

P2.6 Step 10

Search Ranking Integration

負責：

    1. Article 查詢
    2. Knowledge Retrieval
    3. Search Index Retrieval
    4. Knowledge Score Retrieval
    5. Search Ranking
    6. Final Score Sorting


Flow:

    Search Query
        |
        v
    Knowledge Archive
        |
        +---- Search Index
        |
        +---- Knowledge Score
        |
        v
    SearchRankingService
        |
        v
    final_score
        |
        v
    Ranked Results
"""


from types import SimpleNamespace


from database.article_repository import (
    ArticleRepository
)


from database.knowledge_repository import (
    KnowledgeRepository
)


from database.search_index_repository import (
    SearchIndexRepository
)


from database.knowledge_score_repository import (
    KnowledgeScoreRepository
)


from services.search_ranking_service import (
    SearchRankingService
)


class RetrievalService:
    """
    Retrieval Service

    P2.6 Step 10：

        Candidate Retrieval
            ↓
        Search Ranking
            ↓
        Final Search Score
    """


    def __init__(self):

        # ==================================
        # Repositories
        # ==================================

        self.article_repo = (
            ArticleRepository()
        )

        self.knowledge_repo = (
            KnowledgeRepository()
        )

        self.search_index_repo = (
            SearchIndexRepository()
        )

        self.knowledge_score_repo = (
            KnowledgeScoreRepository()
        )


        # ==================================
        # Ranking Service
        # ==================================

        self.ranking_service = (
            SearchRankingService()
        )


    # ==================================
    # Existing Article Retrieval
    # ==================================

    def get_all(self):

        return self.article_repo.find_all()


    def search_importance(
        self,
        level
    ):

        return self.article_repo.find_by_importance(
            level
        )


    def search_category(
        self,
        category
    ):

        return self.article_repo.find_by_category(
            category
        )


    def search_keyword(
        self,
        keyword
    ):

        return self.article_repo.find_by_ai_keyword(
            keyword
        )


    # ==================================
    # Build Ranking Context
    # ==================================

    def _build_ranking_context(
        self,
        knowledge,
        search_index,
        knowledge_score,
        article
    ):
        """
        建立 SearchRankingService 使用的
        Ranking Context。

        資料來源：

            SearchIndex
                ↓
            KnowledgeScore
                ↓
            Article.published
        """

        # ----------------------------------
        # Search Index Data
        # ----------------------------------

        context = {}

        if search_index is not None:

            context.update({

                "id":

                    getattr(
                        search_index,
                        "id",
                        None
                    ),

                "knowledge_id":

                    getattr(
                        search_index,
                        "knowledge_id",
                        None
                    ),

                "search_text":

                    getattr(
                        search_index,
                        "search_text",
                        ""
                    ),

                "keywords":

                    getattr(
                        search_index,
                        "keywords",
                        []
                    ),

                "entities":

                    getattr(
                        search_index,
                        "entities",
                        []
                    ),

                "topic":

                    getattr(
                        search_index,
                        "topic",
                        ""
                    ),

                "embedding_reference":

                    getattr(
                        search_index,
                        "embedding_reference",
                        None
                    ),

                "index_version":

                    getattr(
                        search_index,
                        "index_version",
                        "1.0"
                    ),

                "created_time":

                    getattr(
                        search_index,
                        "created_time",
                        None
                    )

            })


        # ----------------------------------
        # Default Values
        # ----------------------------------

        context.setdefault(
            "search_text",
            ""
        )

        context.setdefault(
            "entities",
            []
        )

        context.setdefault(
            "topic",
            ""
        )


        # ----------------------------------
        # Knowledge Score
        # ----------------------------------

        if knowledge_score:

            context["importance"] = (

                knowledge_score.get(
                    "importance",
                    0
                )

            )

            context["confidence"] = (

                knowledge_score.get(
                    "confidence",
                    0
                )

            )

            context["ranking_score"] = (

                knowledge_score.get(
                    "ranking_score",
                    0
                )

            )

        else:

            context["importance"] = 0

            context["confidence"] = 0

            context["ranking_score"] = 0


        # ----------------------------------
        # Article Published Time
        # ----------------------------------

        published = None

        if article:

            published = article.get(
                "published"
            )


        context["published"] = published


        return SimpleNamespace(
            **context
        )


    # ==================================
    # Ranked Search
    # P2.6 Step 10
    # ==================================

    def search_ranked(
        self,
        keyword,
        limit=10
    ):
        """
        執行 Knowledge Archive Ranked Search。

        Flow:

            Keyword
                ↓
            Knowledge Archive Search
                ↓
            Search Index
                ↓
            Knowledge Score
                ↓
            SearchRankingService
                ↓
            final_score
                ↓
            DESC Sorting

        Returns:

            list[dict]
        """

        # ----------------------------------
        # Validation
        # ----------------------------------

        if not keyword:

            return []


        if limit <= 0:

            return []


        # ----------------------------------
        # Candidate Retrieval
        # ----------------------------------

        knowledge_rows = (
            self.knowledge_repo.search(
                keyword
            )
        )


        results = []


        # ----------------------------------
        # Ranking Candidates
        # ----------------------------------

        for knowledge in knowledge_rows:

            knowledge_id = knowledge.get(
                "id"
            )


            article_id = knowledge.get(
                "article_id"
            )


            if knowledge_id is None:

                continue


            # ------------------------------
            # Search Index
            # ------------------------------

            search_index = (

                self.search_index_repo
                .get_by_knowledge_id(
                    knowledge_id
                )

            )


            # 沒有 Search Index
            # 無法進行完整 Ranking

            if search_index is None:

                continue


            # ------------------------------
            # Knowledge Score
            # ------------------------------

            knowledge_score = (

                self.knowledge_score_repo
                .get_by_knowledge_id(
                    knowledge_id
                )

            )


            # ------------------------------
            # Article
            # ------------------------------

            article = (

                self.knowledge_repo
                .get_with_article(
                    knowledge_id
                )

            )


            if article is None:

                continue


            # ------------------------------
            # Ranking Context
            # ------------------------------

            ranking_context = (

                self._build_ranking_context(

                    knowledge,

                    search_index,

                    knowledge_score,

                    article

                )

            )


            # ------------------------------
            # Calculate Search Score
            # ------------------------------

            search_score = (

                self.ranking_service
                .build_search_score(

                    keyword,

                    ranking_context

                )

            )


            # ------------------------------
            # Result
            # ------------------------------

            results.append({

                "knowledge_id":

                    knowledge_id,


                "article_id":

                    article_id,


                "title":

                    article.get(
                        "title",
                        ""
                    ),


                "url":

                    article.get(
                        "url",
                        ""
                    ),


                "source":

                    article.get(
                        "source",
                        ""
                    ),


                "published":

                    article.get(
                        "published"
                    ),


                "keyword":

                    article.get(
                        "keyword",
                        ""
                    ),


                "topic":

                    knowledge.get(
                        "topic"
                    ),


                "search_score":

                    search_score,


                "final_score":

                    search_score.final_score,


                "knowledge":

                    knowledge,


                "knowledge_score":

                    knowledge_score,


                "search_index":

                    search_index

            })


        # ----------------------------------
        # Final Ranking
        # ----------------------------------

        results.sort(

            key=lambda item: (
                item["final_score"]
            ),

            reverse=True

        )


        # ----------------------------------
        # Limit
        # ----------------------------------

        return results[:limit]
