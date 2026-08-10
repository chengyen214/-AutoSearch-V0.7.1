"""
database/knowledge_score_repository.py

AutoSearch V4

P1.5 Step 3

Knowledge Score Repository


功能:

1. 儲存 Knowledge Score

2. 查詢 Knowledge Score

3. Ranking Retrieval

4. Score Filter

5. 更新 Score


Table:

knowledge_scores


V4 Knowledge Intelligence Layer

"""


from database.connection import get_connection





class KnowledgeScoreRepository:



    """
    Knowledge Score Repository

    封裝 knowledge_scores table

    """




    # ==================================
    # Insert
    # ==================================


    def insert(

        self,

        score

    ):


        """
        新增 Knowledge Score

        Args:

            score:

                models.knowledge_score.KnowledgeScore

        """



        conn = get_connection()


        cursor = conn.cursor()



        sql = """

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

        """



        cursor.execute(

            sql,

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



        cursor.close()

        conn.close()



        return score






    # ==================================
    # Get By Knowledge ID
    # ==================================


    def get_by_knowledge_id(

        self,

        knowledge_id

    ):



        conn = get_connection()



        cursor = conn.cursor(

            dictionary=True

        )




        cursor.execute(

            """

            SELECT *

            FROM knowledge_scores

            WHERE knowledge_id=%s

            """,

            (

                knowledge_id,

            )

        )



        result = cursor.fetchone()



        cursor.close()

        conn.close()



        return result







    # ==================================
    # Top Ranking
    #
    # P1.5 Knowledge Ranking
    #
    # ==================================


    def top_ranking(

        self,

        limit=10

    ):


        """
        取得最高 Ranking Score

        """



        conn = get_connection()



        cursor = conn.cursor(

            dictionary=True

        )




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



        rows = cursor.fetchall()



        cursor.close()

        conn.close()



        return rows







    # ==================================
    # Score Filter
    #
    # ranking_score >= value
    #
    # ==================================


    def find_by_score(

        self,

        score

    ):


        """
        查詢指定分數以上 Knowledge

        """



        conn = get_connection()



        cursor = conn.cursor(

            dictionary=True

        )




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



        rows = cursor.fetchall()



        cursor.close()

        conn.close()



        return rows







    # ==================================
    # Update
    # ==================================


    def update(

        self,

        knowledge_id,

        score

    ):


        """
        更新 Knowledge Score

        """



        conn = get_connection()



        cursor = conn.cursor()




        sql = """

        UPDATE knowledge_scores

        SET

            importance=%s,

            confidence=%s,

            quality_score=%s,

            freshness_score=%s,

            ranking_score=%s


        WHERE knowledge_id=%s


        """




        cursor.execute(

            sql,

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
        判斷是否已有 Score

        """



        conn = get_connection()



        cursor = conn.cursor()




        cursor.execute(

            """

            SELECT id

            FROM knowledge_scores

            WHERE knowledge_id=%s

            """,

            (

                knowledge_id,

            )

        )




        result = cursor.fetchone()



        cursor.close()

        conn.close()



        return result is not None