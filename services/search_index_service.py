"""
services/search_index_service.py

AutoSearch V4

P2.2 Step 6.1

Search Index Service

P2.2.5 Step 4

Knowledge Auto Index

"""

from database.search_index_repository import (
    SearchIndexRepository
)

from models.search_index import (
    SearchIndex
)

from datetime import datetime



class SearchIndexService:



    def __init__(self):

        self.repository = SearchIndexRepository()






    # ==================================
    # Resolve Knowledge ID
    # ==================================


    def _get_knowledge_id(
        self,
        knowledge
    ):


        return (

            getattr(
                knowledge,
                "id",
                None
            )

            or

            getattr(
                knowledge,
                "knowledge_id",
                None
            )

        )






    # ==================================
    # Build Index
    #
    # P2.2.5 Step 4
    #
    # Knowledge -> Search Index
    #
    # ==================================


    def build_index(

        self,

        knowledge

    ):



        knowledge_id = self._get_knowledge_id(

            knowledge

        )



        search_text = (

            str(

                getattr(

                    knowledge,

                    "topic",

                    ""

                )

            )


            + " "


            + str(

                getattr(

                    knowledge,

                    "entities",

                    ""

                )

            )


            + " "


            + str(

                getattr(

                    knowledge,

                    "relations",

                    ""

                )

            )

        )




        index = SearchIndex(



            id=None,



            knowledge_id=knowledge_id,



            search_text=search_text,



            keywords=(

                str(

                    getattr(

                        knowledge,

                        "entities",

                        ""

                    )

                )

            ),



            entities=(

                getattr(

                    knowledge,

                    "entities",

                    ""

                )

                or ""

            ),



            topic=(

                getattr(

                    knowledge,

                    "topic",

                    ""

                )

                or ""

            ),



            embedding_reference=(

                getattr(

                    knowledge,

                    "embedding_id",

                    None

                )

            ),



            index_version="1.0",



            created_time=datetime.now()

        )




        return self.repository.create(

            index

        )









    # ==================================
    # Get Index
    # ==================================


    def get_index(

        self,

        index_id

    ):


        return self.repository.get_by_id(

            index_id

        )









    # ==================================
    # Get Knowledge Index
    # ==================================


    def get_knowledge_index(

        self,

        knowledge_id

    ):


        return self.repository.get_by_knowledge_id(

            knowledge_id

        )









    # ==================================
    # Keyword Search
    # ==================================


    def keyword_search(

        self,

        keyword

    ):


        if not keyword:

            return []


        return self.repository.search_keyword(

            keyword

        )









    # ==================================
    # Entity Search
    # ==================================


    def entity_search(

        self,

        entity

    ):


        if not entity:

            return []


        return self.repository.search_entity(

            entity

        )









    # ==================================
    # Rebuild Index
    #
    # Update Existing
    #
    # ==================================


    def rebuild_index(

        self,

        knowledge

    ):



        knowledge_id = self._get_knowledge_id(

            knowledge

        )



        existing = self.repository.get_by_knowledge_id(

            knowledge_id

        )





        search_text = (

            str(

                getattr(

                    knowledge,

                    "topic",

                    ""

                )

            )

            + " "

            + str(

                getattr(

                    knowledge,

                    "entities",

                    ""

                )

            )

            + " "

            + str(

                getattr(

                    knowledge,

                    "relations",

                    ""

                )

            )

        )






        if existing:



            existing.search_text = search_text



            existing.keywords = (

                str(

                    getattr(

                        knowledge,

                        "entities",

                        ""

                    )

                )

            )



            existing.entities = (

                getattr(

                    knowledge,

                    "entities",

                    ""

                )

                or ""

            )



            existing.topic = (

                getattr(

                    knowledge,

                    "topic",

                    ""

                )

                or ""

            )



            return self.repository.update(

                existing

            )







        return self.build_index(

            knowledge

        )