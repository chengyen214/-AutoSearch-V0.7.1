"""
metadata_pipeline.py

AutoSearch V4

P1.3 Step 3.2

Article Metadata Pipeline


流程:

Article
    |
    v
MetadataPipeline
    |
    v
ArticleMetadata
    |
    v
ArticleMetadataRepository


"""


from models.article_metadata import ArticleMetadata

from database.article_metadata_repository import (
    ArticleMetadataRepository
)

from utils.logger import logger





class MetadataPipeline:



    def __init__(self):


        self.repository = (
            ArticleMetadataRepository()
        )





    def create(

        self,

        article

    ):


        """
        建立 Article Metadata

        """



        if article.id is None:


            raise Exception(
                "Article ID required"
            )





        # ==========================
        # 避免重複
        # ==========================


        if self.repository.exists(

            article.id

        ):


            logger.info(

                f"Metadata exists: article_id={article.id}"

            )


            return self.repository.get_by_article_id(

                article.id

            )







        metadata = ArticleMetadata(


            article_id=article.id,


            author="",


            category=getattr(

                article,

                "category",

                ""

            ),


            language="zh-TW",


            source_type="news",


            tags=""

        )





        result = self.repository.insert(

            metadata

        )





        logger.info(

            f"Metadata created: article_id={article.id}"

        )



        return result