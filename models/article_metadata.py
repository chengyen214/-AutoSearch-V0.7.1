"""
models/article_metadata.py

AutoSearch V4

Article Metadata Model


用途:

    保存文章額外 Metadata


Database:

    article_metadata


V4 Phase 1.1


"""


from datetime import datetime





class ArticleMetadata:




    def __init__(

        self,


        article_id=None,


        author=None,


        category=None,


        language=None,


        source_type=None,


        tags=None,


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
        # Metadata
        # ==========================


        self.author = author



        self.category = category



        self.language = language



        self.source_type = source_type



        self.tags = tags



        # ==========================
        # Time
        # ==========================


        self.created_time = (

            created_time

            if created_time

            else datetime.now()

        )




    # ==================================
    # Metadata Property
    # ==================================



    @property
    def has_tags(self):


        return bool(

            self.tags

        )





    @property
    def tag_list(self):


        if isinstance(

            self.tags,

            list

        ):


            return self.tags



        if self.tags:


            return self.tags.split(",")



        return []





    # ==================================
    # Dictionary
    # ==================================



    def to_dict(self):


        return {


            "id":

            self.id,



            "article_id":

            self.article_id,



            "author":

            self.author,



            "category":

            self.category,



            "language":

            self.language,



            "source_type":

            self.source_type,



            "tags":

            self.tags,



            "created_time":

            self.created_time


        }





    def __repr__(self):


        return (


            f"ArticleMetadata("

            f"article_id={self.article_id}, "

            f"category={self.category}"

            ")"


        )