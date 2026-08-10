"""
pipeline/raw_archive_pipeline.py

AutoSearch V4

P1.3 Step 3.1

Raw Archive Pipeline


功能:

Article
   |
   v
RawDocument
   |
   v
raw_documents


"""


from models.raw_document import RawDocument

from database.raw_document_repository import (
    RawDocumentRepository
)

from utils.logger import logger





class RawArchivePipeline:



    def __init__(self):


        self.repository = RawDocumentRepository()





    # ==================================
    # Save Raw Archive
    # ==================================


    def save(

        self,

        article,

        storage_path,

        file_hash,

        file_size

    ):


        """
        建立 Raw Document Archive

        """


        # 防止重複


        if self.repository.exists(

            article.id

        ):


            logger.info(

                f"Raw archive exists: article_id={article.id}"

            )


            return self.repository.get_by_article_id(

                article.id

            )





        raw_document = RawDocument(


            article_id=article.id,


            original_url=article.url,


            storage_path=storage_path,


            file_hash=file_hash,


            file_size=file_size,


            mime_type="text/html"

        )





        result = self.repository.save(

            raw_document

        )





        logger.info(

            f"Raw archive saved: article_id={article.id}"

        )



        return result