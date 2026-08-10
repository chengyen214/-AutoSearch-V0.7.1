"""
utils/check_pipeline_status.py

AutoSearch V4

Pipeline Verification Tool

確認:

Crawler
 |
Article
 |
AI Task
 |
AI Result
 |
Knowledge
 |
Score
 |
Search Index

"""

from database.connection import get_connection



def query(sql):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(sql)

    result = cursor.fetchall()

    cursor.close()

    conn.close()

    return result





def check_count():


    print()

    print(
        "========== COUNT =========="
    )


    tables = [

        "articles",

        "ai_tasks",

        "knowledge_archive",

        "knowledge_scores",

        "search_index"

    ]


    for table in tables:


        result = query(

            f"""

            SELECT COUNT(*) count

            FROM {table}

            """

        )


        print(

            f"{table}: {result[0]['count']}"

        )







def check_article_ai():


    print()

    print(

        "========== ARTICLE AI STATUS =========="

    )


    rows = query(

        """

        SELECT

            id,

            title,

            ai_status,

            ai_category,

            ai_model,

            ai_confidence

        FROM articles

        ORDER BY id DESC

        """

    )


    for row in rows:

        print(row)







def check_task_status():


    print()

    print(

        "========== AI TASK STATUS =========="

    )


    rows = query(

        """

        SELECT

            id,

            article_id,

            task_type,

            status,

            retry_count

        FROM ai_tasks

        ORDER BY id DESC

        """

    )


    for row in rows:

        print(row)








def check_knowledge():


    print()

    print(

        "========== KNOWLEDGE =========="

    )


    rows = query(

        """

        SELECT

            id,

            article_id,

            topic,

            entities

        FROM knowledge_archive

        ORDER BY id DESC

        """

    )


    for row in rows:

        print(row)







def check_score():


    print()

    print(

        "========== KNOWLEDGE SCORE =========="

    )


    rows = query(

        """

        SELECT

            id,

            knowledge_id,

            importance,

            confidence,

            ranking_score

        FROM knowledge_scores

        ORDER BY id DESC

        """

    )


    for row in rows:

        print(row)







def check_index():


    print()

    print(

        "========== SEARCH INDEX =========="

    )


    rows = query(

        """

        SELECT

            id,

            knowledge_id,

            topic,

            search_text

        FROM search_index

        ORDER BY id DESC

        """

    )


    for row in rows:

        print(row)








def main():


    print()

    print(

        "================================="

    )

    print(

        " AutoSearch V4 Pipeline Check"

    )

    print(

        "================================="

    )


    check_count()


    check_article_ai()


    check_task_status()


    check_knowledge()


    check_score()


    check_index()





if __name__ == "__main__":

    main()