"""
models/raw_document.py

AutoSearch V4

Raw Document Model


用途:

    保存原始 HTML Archive 資訊


Database:

    raw_documents


V4 Phase 1.1


"""



from datetime import datetime





class RawDocument:




    def __init__(

        self,


        article_id=None,


        original_url="",


        storage_path="",


        file_hash="",


        file_size=0,


        mime_type="text/html",


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
        # Original Source
        # ==========================


        self.original_url = original_url



        # ==========================
        # Archive Storage
        # ==========================


        self.storage_path = storage_path



        # ==========================
        # File Information
        # ==========================


        self.file_hash = file_hash



        self.file_size = file_size



        self.mime_type = mime_type



        # ==========================
        # Time
        # ==========================


        self.created_time = (

            created_time

            if created_time

            else datetime.now()

        )




    # ==================================
    # Archive Property
    # ==================================



    @property
    def filename(self):


        if self.storage_path:


            return self.storage_path.split("/")[-1]


        return ""





    @property
    def is_html(self):


        return (

            self.mime_type

            ==

            "text/html"

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



            "original_url":

            self.original_url,



            "storage_path":

            self.storage_path,



            "file_hash":

            self.file_hash,



            "file_size":

            self.file_size,



            "mime_type":

            self.mime_type,



            "created_time":

            self.created_time


        }





    def __repr__(self):


        return (


            f"RawDocument("

            f"article_id={self.article_id}, "

            f"path={self.storage_path}"

            ")"


        )