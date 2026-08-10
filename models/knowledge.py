"""
models/knowledge.py

AutoSearch V4

Knowledge Archive Model

用途:

保存 AI 萃取後的知識關係

Database:

knowledge_archive

V4 Phase 1.1
"""

from datetime import datetime


class Knowledge:
    """
    Knowledge Archive Entity

    AI Analysis Result
            |
            v
    Knowledge Archive

    """


    def __init__(
        self,
        article_id=None,
        topic=None,
        entities=None,
        relations=None,
        knowledge_version="1.0",
        created_time=None
    ):


        # ==========================
        # Database ID
        # ==========================

        self.id = None



        # ==========================
        # Article Relation
        # ==========================

        self.article_id = article_id



        # ==========================
        # Knowledge Data
        # ==========================

        self.topic = topic


        # 避免 None 導致 split / join 錯誤

        self.entities = (

            entities

            if entities

            else []

        )


        self.relations = (

            relations

            if relations

            else []

        )


        self.knowledge_version = knowledge_version



        # ==========================
        # Time
        # ==========================

        self.created_time = (

            created_time

            if created_time

            else datetime.now()

        )



    # ==================================
    # Knowledge Property
    # ==================================


    @property
    def entity_list(self):


        if isinstance(

            self.entities,

            list

        ):

            return self.entities



        if self.entities:


            return self.entities.split(",")



        return []





    @property
    def relation_list(self):


        if isinstance(

            self.relations,

            list

        ):

            return self.relations



        if self.relations:


            return self.relations.split(",")



        return []





    # ==================================
    # Database Text Format
    #
    # MySQL TEXT
    #
    # ==================================


    @property
    def entities_text(self):


        if isinstance(

            self.entities,

            list

        ):


            return ",".join(

                self.entities

            )


        return self.entities





    @property
    def relations_text(self):


        if isinstance(

            self.relations,

            list

        ):


            return ",".join(

                self.relations

            )


        return self.relations





    @property
    def has_knowledge(self):


        return bool(

            self.topic

            or

            self.entities

            or

            self.relations

        )





    # ==================================
    # Dictionary
    # ==================================


    def to_dict(self):


        return {


            "id":

                self.id,



            "article_id":

                self.article_id,



            "topic":

                self.topic,



            "entities":

                self.entities,



            "relations":

                self.relations,



            "knowledge_version":

                self.knowledge_version,



            "created_time":

                self.created_time


        }





    def __repr__(self):


        return (

            f"Knowledge("

            f"article_id={self.article_id}, "

            f"topic={self.topic}"

            ")"

        )