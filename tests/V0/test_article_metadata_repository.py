"""
Test ArticleMetadataRepository

AutoSearch V4
P1.1 Step 3.2

"""


from models.article_metadata import ArticleMetadata

from database.article_metadata_repository import ArticleMetadataRepository





def test_article_metadata_repository():



    repo = ArticleMetadataRepository()



    metadata = ArticleMetadata(

        article_id=8,

        author="TEST",

        category="Semiconductor",

        language="zh-TW",

        source_type="News",

        tags="AI,Chip"

    )





    result = repo.insert(metadata)





    print(

        "Metadata ID:",

        result.id

    )





    assert result.id is not None





    print(

        "✅ ArticleMetadataRepository OK"

    )






if __name__ == "__main__":


    test_article_metadata_repository()