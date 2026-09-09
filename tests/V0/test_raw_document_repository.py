"""
Test RawDocumentRepository

AutoSearch V4
P1.1 Step 3.1
"""


from models.raw_document import RawDocument

from database.raw_document_repository import RawDocumentRepository





def test_raw_document_repository():



    repo = RawDocumentRepository()



    raw = RawDocument(

        article_id=8,

        storage_path="storage/archive/raw/html/test.html",

        file_hash="abc123",

        file_size=1024,

        mime_type="text/html"

    )




    result = repo.insert(raw)




    print(

        "RawDocument ID:",

        result.id

    )




    assert result.id is not None



    print(

        "✅ RawDocumentRepository OK"

    )





if __name__ == "__main__":

    test_raw_document_repository()