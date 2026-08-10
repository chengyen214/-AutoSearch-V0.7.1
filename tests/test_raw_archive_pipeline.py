from pipeline.raw_archive_pipeline import RawArchivePipeline

from database.article_repository import ArticleRepository





def test_raw_archive():


    repo = ArticleRepository()


    article = repo.find_model_by_id(

        1

    )


    pipeline = RawArchivePipeline()



    result = pipeline.save(

        article,

        "storage/raw/article_1.html",

        "abc123hash",

        1024

    )


    print()

    print("================")

    print("Raw Document")

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