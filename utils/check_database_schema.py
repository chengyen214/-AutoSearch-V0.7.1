"""
AutoSearch V4

Database Schema Inspector

用途:

查看目前 MySQL:

- Tables
- Columns
- Create SQL
- Index / Structure

"""

from database.connection import get_connection



def show_tables():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        "SHOW TABLES"
    )


    tables = cursor.fetchall()


    print(
        "\n========== TABLES ==========\n"
    )


    for table in tables:

        print(
            table[0]
        )


    cursor.close()
    conn.close()



def show_columns(table):

    conn = get_connection()

    cursor = conn.cursor(
        dictionary=True
    )


    print(
        f"\n========== {table} COLUMNS ==========\n"
    )


    cursor.execute(
        f"""
        SHOW COLUMNS FROM {table}
        """
    )


    rows = cursor.fetchall()


    for row in rows:

        print(row)


    cursor.close()
    conn.close()



def show_create(table):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        f"""
        SHOW CREATE TABLE {table}
        """
    )


    result = cursor.fetchone()


    print(
        "\n========== CREATE TABLE ==========\n"
    )


    if result:

        print(
            result[1]
        )


    cursor.close()
    conn.close()



def main():


    print(
        "========== AutoSearch V4 Schema Check =========="
    )


    show_tables()



    check_tables = [

        "articles",

        "ai_tasks",

        "knowledge_archive",

        "knowledge_scores",

        "search_index",

        "raw_documents"

    ]



    for table in check_tables:


        try:

            show_columns(
                table
            )


            show_create(
                table
            )


        except Exception as e:


            print(
                f"\nSkip {table}: {e}"
            )



    print(
        "\n========== Check Finished =========="
    )



if __name__ == "__main__":

    main()