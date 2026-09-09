from models.article_metadata import ArticleMetadata




def test_metadata():


    metadata = ArticleMetadata(

        article_id=1,

        author="AI News",

        category="Semiconductor",

        language="zh-TW",

        source_type="News",

        tags=[

            "TSMC",

            "2nm"

        ]

    )



    assert metadata.article_id == 1


    assert metadata.category == "Semiconductor"


    assert metadata.has_tags is True


    assert len(metadata.tag_list) == 2



    print(

        "ArticleMetadata Model OK"

    )




if __name__ == "__main__":

    test_metadata()