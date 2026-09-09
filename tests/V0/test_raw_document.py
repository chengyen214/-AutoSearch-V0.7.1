from models.raw_document import RawDocument



def test_raw_document():


    raw = RawDocument(

        article_id=1,

        original_url="https://example.com/article",

        storage_path="storage/archive/raw/html/test.html",

        file_hash="abc123"

    )


    assert raw.article_id == 1


    assert raw.is_html is True


    assert raw.filename == "test.html"



    print(

        "RawDocument Model OK"

    )





if __name__ == "__main__":

    test_raw_document()