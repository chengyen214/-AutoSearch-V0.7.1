"""
article_metadata_repository.py

AutoSearch V4

Article Metadata Repository


功能:

1. 新增文章 Metadata
2. 查詢文章 Metadata
3. 檢查 Metadata 是否存在
4. 更新 Metadata


資料表:

article_metadata


V4 Knowledge Archive Foundation

"""



from database.connection import get_connection






class ArticleMetadataRepository:




    """
    Article Metadata Repository

    封裝 article_metadata table

    """





    # ==================================
    # 新增 Metadata
    # ==================================

    def insert(self, metadata):


        """
        新增文章 Metadata


        Args:

            metadata:

                models.article_metadata.ArticleMetadata


        Returns:

            ArticleMetadata

        """



        conn = get_connection()



        cursor = conn.cursor()





        sql = """

        INSERT INTO article_metadata

        (

            article_id,

            author,

            category,

            language,

            source_type,

            tags

        )

        VALUES

        (

            %s,

            %s,

            %s,

            %s,

            %s,

            %s

        )

        """





        cursor.execute(

            sql,

            (

                metadata.article_id,

                metadata.author,

                metadata.category,

                metadata.language,

                metadata.source_type,

                metadata.tags

            )

        )





        conn.commit()





        metadata.id = cursor.lastrowid





        cursor.close()

        conn.close()





        return metadata









    # ==================================
    # 查詢 Metadata
    # ==================================

    def get_by_article_id(

        self,

        article_id

    ):


        """
        根據 Article ID

        取得 Metadata

        """



        conn = get_connection()



        cursor = conn.cursor(

            dictionary=True

        )





        sql = """

        SELECT *

        FROM article_metadata

        WHERE article_id=%s

        """





        cursor.execute(

            sql,

            (

                article_id,

            )

        )





        result = cursor.fetchone()





        cursor.close()

        conn.close()





        return result









    # ==================================
    # 檢查 Metadata
    # ==================================

    def exists(

        self,

        article_id

    ):


        """
        判斷是否已有 Metadata

        """



        conn = get_connection()



        cursor = conn.cursor()





        sql = """

        SELECT id

        FROM article_metadata

        WHERE article_id=%s

        """





        cursor.execute(

            sql,

            (

                article_id,

            )

        )





        result = cursor.fetchone()





        cursor.close()

        conn.close()





        return result is not None









    # ==================================
    # 更新 Metadata
    # ==================================

    def update(

        self,

        article_id,

        metadata

    ):


        """
        更新文章 Metadata

        """



        conn = get_connection()



        cursor = conn.cursor()





        sql = """

        UPDATE article_metadata

        SET

            author=%s,

            category=%s,

            language=%s,

            source_type=%s,

            tags=%s


        WHERE article_id=%s

        """





        cursor.execute(

            sql,

            (

                metadata.author,

                metadata.category,

                metadata.language,

                metadata.source_type,

                metadata.tags,

                article_id

            )

        )





        conn.commit()





        cursor.close()

        conn.close()