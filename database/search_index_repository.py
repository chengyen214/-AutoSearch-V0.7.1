"""
database/search_index_repository.py

AutoSearch V4

P2.2 Step 4

Search Index Repository

Purpose:

Manage Search Index Storage

Flow:

Knowledge Archive
    |
    v
Search Index
    |
    v
Hybrid Search Engine
"""


from models.search_index import SearchIndex

from database.connection import get_connection

import json



class SearchIndexRepository:


    # ==================================
    # JSON Helper
    # ==================================

    def _to_json(
        self,
        value
    ):

        if value is None:
            return "[]"


        if isinstance(
            value,
            str
        ):
            return value


        return json.dumps(
            value,
            ensure_ascii=False
        )



    def _from_json(
        self,
        value
    ):

        if value is None:
            return []


        if isinstance(
            value,
            list
        ):
            return value


        try:

            return json.loads(
                value
            )

        except Exception:

            return []



    # ==================================
    # Create
    # ==================================

    def create(

        self,

        index: SearchIndex

    ):


        conn = get_connection()

        cursor = conn.cursor()


        try:


            cursor.execute(

                """

                INSERT INTO search_index

                (

                    knowledge_id,

                    search_text,

                    keywords,

                    entities,

                    topic,

                    embedding_reference,

                    index_version,

                    created_time

                )

                VALUES

                (

                    %s,%s,%s,%s,%s,%s,%s,%s

                )

                """,

                (

                    index.knowledge_id,

                    index.search_text,


                    self._to_json(
                        index.keywords
                    ),


                    self._to_json(
                        index.entities
                    ),


                    index.topic,


                    index.embedding_reference,

                    index.index_version,

                    index.created_time

                )

            )


            conn.commit()



            index.id = cursor.lastrowid



            return index



        finally:


            cursor.close()

            conn.close()







    # ==================================
    # Get By ID
    # ==================================

    def get_by_id(

        self,

        index_id

    ):


        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        try:


            cursor.execute(

                """

                SELECT *

                FROM search_index

                WHERE id=%s

                """,

                (
                    index_id,
                )

            )


            row = cursor.fetchone()



            if not row:

                return None



            row["keywords"] = self._from_json(
                row.get("keywords")
            )


            row["entities"] = self._from_json(
                row.get("entities")
            )



            return SearchIndex.from_dict(
                row
            )



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


        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        try:


            cursor.execute(

                """

                SELECT *

                FROM search_index

                WHERE knowledge_id=%s

                """,

                (
                    knowledge_id,
                )

            )


            row = cursor.fetchone()



            if not row:

                return None



            row["keywords"] = self._from_json(
                row.get("keywords")
            )


            row["entities"] = self._from_json(
                row.get("entities")
            )



            return SearchIndex.from_dict(
                row
            )



        finally:


            cursor.close()

            conn.close()







    # ==================================
    # Keyword Search
    # ==================================

    def search_keyword(

        self,

        keyword

    ):


        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        try:


            cursor.execute(

                """

                SELECT *

                FROM search_index

                WHERE

                    search_text LIKE %s

                OR

                    keywords LIKE %s

                """,

                (

                    f"%{keyword}%",

                    f"%{keyword}%"

                )

            )


            rows = cursor.fetchall()



            for row in rows:

                row["keywords"] = self._from_json(
                    row.get("keywords")
                )

                row["entities"] = self._from_json(
                    row.get("entities")
                )



            return [

                SearchIndex.from_dict(row)

                for row in rows

            ]



        finally:


            cursor.close()

            conn.close()







    # ==================================
    # Entity Search
    # ==================================

    def search_entity(

        self,

        entity

    ):


        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        try:


            cursor.execute(

                """

                SELECT *

                FROM search_index

                WHERE entities LIKE %s

                """,

                (

                    f"%{entity}%",

                )

            )


            rows = cursor.fetchall()



            for row in rows:

                row["keywords"] = self._from_json(
                    row.get("keywords")
                )

                row["entities"] = self._from_json(
                    row.get("entities")
                )



            return [

                SearchIndex.from_dict(row)

                for row in rows

            ]



        finally:


            cursor.close()

            conn.close()







    # ==================================
    # Get All
    # ==================================

    def get_all(

        self

    ):


        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        try:


            cursor.execute(

                """

                SELECT *

                FROM search_index

                ORDER BY id DESC

                """

            )


            rows = cursor.fetchall()



            for row in rows:

                row["keywords"] = self._from_json(
                    row.get("keywords")
                )

                row["entities"] = self._from_json(
                    row.get("entities")
                )



            return [

                SearchIndex.from_dict(row)

                for row in rows

            ]



        finally:


            cursor.close()

            conn.close()







    # ==================================
    # Update
    # ==================================

    def update(

        self,

        index: SearchIndex

    ):


        conn = get_connection()

        cursor = conn.cursor()



        try:


            cursor.execute(

                """

                UPDATE search_index

                SET

                    search_text=%s,

                    keywords=%s,

                    entities=%s,

                    topic=%s,

                    embedding_reference=%s,

                    index_version=%s


                WHERE id=%s


                """,

                (

                    index.search_text,


                    self._to_json(
                        index.keywords
                    ),


                    self._to_json(
                        index.entities
                    ),


                    index.topic,


                    index.embedding_reference,

                    index.index_version,

                    index.id

                )

            )



            conn.commit()



            return index



        finally:


            cursor.close()

            conn.close()







    # ==================================
    # Delete
    # ==================================

    def delete(

        self,

        index_id

    ):


        conn = get_connection()

        cursor = conn.cursor()



        try:


            cursor.execute(

                """

                DELETE FROM search_index

                WHERE id=%s

                """,

                (

                    index_id,

                )

            )


            conn.commit()



            return True



        finally:


            cursor.close()

            conn.close()