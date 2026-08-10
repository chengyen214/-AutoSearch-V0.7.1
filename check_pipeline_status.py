"""
check_pipeline_status.py

AutoSearch V4

P2.2.6 Pipeline Verification


Check:

1. articles

2. ai_tasks

3. ai_analysis

4. knowledge_archive

5. knowledge_scores

6. search_index


"""

from database.connection import get_connection

from utils.logger import logger



def query_count(
    cursor,
    table
):


    try:


        cursor.execute(

            f"""
            SELECT COUNT(*)
            FROM {table}
            """

        )


        result = cursor.fetchone()


        return result[0]



    except Exception as e:


        logger.error(

            f"{table} check error: {e}"

        )


        return -1





def query_status(
    cursor,
    table,
    field
):


    try:


        cursor.execute(

            f"""
            SELECT 
                {field},
                COUNT(*)

            FROM {table}

            GROUP BY {field}
            """

        )


        return cursor.fetchall()



    except Exception as e:


        logger.error(e)


        return []







def main():


    logger.info(

        "========== Pipeline Status =========="

    )



    conn = None



    try:



        conn = get_connection()


        cursor = conn.cursor(
            dictionary=True
        )




        print()

        print("==============================")

        print(" Articles ")

        print("==============================")


        print(

            "Count:",

            query_count(

                cursor,

                "articles"

            )

        )







        print()

        print("==============================")

        print(" AI Tasks ")

        print("==============================")


        print(

            "Count:",

            query_count(

                cursor,

                "ai_tasks"

            )

        )



        print(

            "Status:"

        )


        for row in query_status(

            cursor,

            "ai_tasks",

            "status"

        ):


            print(row)









        print()

        print("==============================")

        print(" AI Analysis ")

        print("==============================")


        print(

            "Count:",

            query_count(

                cursor,

                "ai_analysis"

            )

        )









        print()

        print("==============================")

        print(" Knowledge Archive ")

        print("==============================")


        print(

            "Count:",

            query_count(

                cursor,

                "knowledge_archive"

            )

        )










        print()

        print("==============================")

        print(" Knowledge Scores ")

        print("==============================")


        print(

            "Count:",

            query_count(

                cursor,

                "knowledge_scores"

            )

        )









        print()

        print("==============================")

        print(" Search Index ")

        print("==============================")


        print(

            "Count:",

            query_count(

                cursor,

                "search_index"

            )

        )







        print()

        print("==============================")

        print(" Pipeline Result ")

        print("==============================")


        articles = query_count(

            cursor,

            "articles"

        )


        tasks = query_count(

            cursor,

            "ai_tasks"

        )


        knowledge = query_count(

            cursor,

            "knowledge_archive"

        )


        scores = query_count(

            cursor,

            "knowledge_scores"

        )



        if (

            articles > 0

            and

            tasks > 0

            and

            knowledge > 0

            and

            scores > 0

        ):


            print(

                "Pipeline Status : OK"

            )


        else:


            print(

                "Pipeline Status : INCOMPLETE"

            )







    except Exception as e:


        logger.exception(e)



    finally:



        if conn:


            conn.close()





if __name__ == "__main__":


    main()