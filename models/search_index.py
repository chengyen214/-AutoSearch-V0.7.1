"""
models/search_index.py

AutoSearch V4

P2.2

Search Index Model


Purpose:

Knowledge

    |

    v

Search Index


For:

- Keyword Search
- Hybrid Search
- Full Text Search
- Index Optimization

"""


from datetime import datetime





class SearchIndex:


    def __init__(

        self,

        id=None,

        knowledge_id=None,

        search_text="",

        keywords="",

        entities="",

        topic="",

        embedding_reference=None,

        index_version="1.0",

        created_time=None

    ):


        self.id = id


        self.knowledge_id = knowledge_id


        # searchable content

        self.search_text = search_text



        # keyword cache

        self.keywords = keywords



        # entity cache

        self.entities = entities



        # knowledge topic

        self.topic = topic



        # link to embedding

        self.embedding_reference = (
            embedding_reference
        )



        # index schema version

        self.index_version = (
            index_version
        )



        self.created_time = (

            created_time

            if created_time

            else datetime.now()

        )







    # ==================================
    # Convert Dictionary
    # ==================================


    def to_dict(self):


        return {


            "id":

                self.id,


            "knowledge_id":

                self.knowledge_id,


            "search_text":

                self.search_text,


            "keywords":

                self.keywords,


            "entities":

                self.entities,


            "topic":

                self.topic,


            "embedding_reference":

                self.embedding_reference,


            "index_version":

                self.index_version,


            "created_time":

                self.created_time


        }






    # ==================================
    # Create From Dictionary
    # ==================================


    @classmethod

    def from_dict(

        cls,

        data

    ):


        return cls(

            id=data.get(

                "id"

            ),


            knowledge_id=data.get(

                "knowledge_id"

            ),


            search_text=data.get(

                "search_text",

                ""

            ),


            keywords=data.get(

                "keywords",

                ""

            ),


            entities=data.get(

                "entities",

                ""

            ),


            topic=data.get(

                "topic",

                ""

            ),


            embedding_reference=data.get(

                "embedding_reference"

            ),


            index_version=data.get(

                "index_version",

                "1.0"

            ),


            created_time=data.get(

                "created_time"

            )

        )







    def __repr__(self):


        return (

            f"<SearchIndex "

            f"id={self.id} "

            f"knowledge_id={self.knowledge_id} "

            f"topic={self.topic}>"

        )