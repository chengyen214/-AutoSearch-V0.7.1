"""
utils/check_database.py

AutoSearch V4

Database Health Check

檢查:

1. articles
2. ai_tasks
3. knowledge_archive
4. knowledge_scores
5. search_index

"""

from database.connection import get_connection

from utils.logger import logger



def show_table(
    cursor,
    table,
    limit=5
):


    print("\n")
    print("=" * 60)
    print(f"TABLE : {table}")
    print("=" * 60)



    try:


        cursor.execute(
            f"""
            SELECT *
            FROM {table}
            ORDER BY id DESC
            LIMIT %s
            """,
            (
                limit,
            )
        )


        rows = cursor.fetchall()



        if not rows:

            print("NO DATA")

            return



        for row in rows:

            print(row)



    except Exception as e:

        print(
            f"ERROR {table}: {e}"
        )





def count_table(
    cursor,
    table
):


    try:

        cursor.execute(

            f"""
            SELECT COUNT(*) AS count
            FROM {table}
            """

        )


        result = cursor.fetchone()


        print(
            f"{table}: {result['count']}"
        )


    except Exception as e:

        print(
            f"{table}: ERROR {e}"
        )






def main():


    print(
        "\n========== AutoSearch V4 Database Check =========="
    )



    conn = get_connection()


    if conn is None:

        print(
            "Database connection failed"
        )

        return



    cursor = conn.cursor(
        dictionary=True
    )



    print("\n[COUNT]")


    tables = [

        "articles",

        "ai_tasks",

        "knowledge_archive",

        "knowledge_scores",

        "search_index"

    ]



    for table in tables:

        count_table(
            cursor,
            table
        )





    for table in tables:

        show_table(
            cursor,
            table
        )




    cursor.close()

    conn.close()



    print(
        "\n========== Check Finished =========="
    )





if __name__ == "__main__":

    main()