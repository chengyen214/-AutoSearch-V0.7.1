"""
database/migrate.py

AutoSearch V3

Database Migration

功能:

    執行 database/schema.sql

支援:

    V2.5 Article Database

    V3 AI Analysis Database

    P4.4.1 AI Metadata

"""


from database.connection import get_connection

from utils.logger import logger





def migrate():


    conn = get_connection()



    if conn is None:

        raise Exception(
            "Database connection failed."
        )



    cursor = conn.cursor()



    try:



        with open(

            "database/schema.sql",

            "r",

            encoding="utf-8"

        ) as f:


            sql = f.read()





        statements = sql.split(";")





        for statement in statements:


            statement = statement.strip()



            if statement:



                cursor.execute(

                    statement

                )




        conn.commit()



        logger.info(

            "Database schema migration complete"

        )



        print(

            "✅ Database schema created."

        )




    except Exception as e:



        conn.rollback()



        logger.error(

            f"Migration failed: {e}"

        )


        raise




    finally:



        cursor.close()

        conn.close()







if __name__ == "__main__":


    migrate()