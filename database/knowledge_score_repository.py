"""
database/knowledge_score_repository.py

AutoSearch V4

P1.5 Step 3

Knowledge Score Repository


功能：

1. 儲存 Knowledge Score
2. 查詢 Knowledge Score
3. Ranking Retrieval
4. Score Filter
5. 更新 Score
6. 檢查 Score 是否存在


Table：

knowledge_scores


V4 Knowledge Intelligence Layer
"""


from database.connection import get_connection


class KnowledgeScoreRepository:
    """
    Knowledge Score Repository

    封裝：

        knowledge_scores table

    負責：

        - Knowledge Score CRUD
        - Ranking Retrieval
        - Score Filter
    """

    # ==================================
    # Insert
    # ==================================

    def insert(
        self,
        score
    ):
        """
        新增 Knowledge Score。

        Args:
            score:
                models.knowledge_score.KnowledgeScore

        Returns:
            KnowledgeScore
        """

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO knowledge_scores
                (
                    knowledge_id,
                    importance,
                    confidence,
                    quality_score,
                    freshness_score,
                    ranking_score
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    score.knowledge_id,
                    score.importance,
                    score.confidence,
                    score.quality_score,
                    score.freshness_score,
                    score.ranking_score
                )
            )

            conn.commit()

            score.id = cursor.lastrowid

            return score

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get By Knowledge ID
    # ==================================

    def get_by_knowledge_id(
        self,
        knowledge_id
    ):
        """
        依 Knowledge ID 取得最新 Knowledge Score。

        Args:
            knowledge_id:
                Knowledge Archive ID

        Returns:
            dict | None
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_scores
                WHERE knowledge_id=%s
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    knowledge_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Find Top
    # ==================================

    def find_top(
        self,
        limit=10
    ):
        """
        取得 Ranking Score 最高的 Knowledge。

        Args:
            limit:
                回傳筆數。

        Returns:
            list[dict]
        """

        return self.top_ranking(
            limit
        )

    # ==================================
    # Top Ranking
    # ==================================

    def top_ranking(
        self,
        limit=10
    ):
        """
        取得最高 Ranking Score。

        Args:
            limit:
                回傳筆數。

        Returns:
            list[dict]
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_scores
                ORDER BY ranking_score DESC
                LIMIT %s
                """,
                (
                    limit,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Score Filter
    # ==================================

    def find_by_score(
        self,
        score
    ):
        """
        查詢指定 Ranking Score 以上的 Knowledge。

        Args:
            score:
                最低 Ranking Score

        Returns:
            list[dict]
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_scores
                WHERE ranking_score >= %s
                ORDER BY ranking_score DESC
                """,
                (
                    score,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Update
    # ==================================

    def update(
        self,
        knowledge_id,
        score
    ):
        """
        更新 Knowledge Score。

        Args:
            knowledge_id:
                Knowledge Archive ID

            score:
                KnowledgeScore Model

        Returns:
            bool
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE knowledge_scores
                SET
                    importance=%s,
                    confidence=%s,
                    quality_score=%s,
                    freshness_score=%s,
                    ranking_score=%s
                WHERE knowledge_id=%s
                """,
                (
                    score.importance,
                    score.confidence,
                    score.quality_score,
                    score.freshness_score,
                    score.ranking_score,
                    knowledge_id
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        knowledge_id
    ):
        """
        判斷 Knowledge 是否已有 Score。

        Args:
            knowledge_id:
                Knowledge Archive ID

        Returns:
            bool
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM knowledge_scores
                WHERE knowledge_id=%s
                LIMIT 1
                """,
                (
                    knowledge_id,
                )
            )

            result = cursor.fetchone()

            return result is not None

        finally:

            cursor.close()
            conn.close()