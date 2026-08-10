from database.article_repository import ArticleRepository

from pipeline.metadata_pipeline import MetadataPipeline





def test_metadata_pipeline():


    repo = ArticleRepository()


    article = repo.find_model_by_id(

        1

    )



    pipeline = MetadataPipeline()



    result = pipeline.create(

        article

    )



    print()

    print("================")

    print("Metadata")

    print("================")

    print(

        "ID:",

        result.id

    )

    print(

        "Article:",

        result.article_id

    )



    assert result.id is not None