"""
test_archive_storage.py

AutoSearch V4

P1.1 Step 4.1 Test

"""


from storage.archive_storage import save_html






def test_archive_storage():


    html = """

    <html>

    <body>

    AutoSearch V4 Archive Test

    </body>

    </html>

    """




    result = save_html(

        "v4_test_001",

        html

    )





    print(

        "Path:",

        result["storage_path"]

    )



    print(

        "Hash:",

        result["file_hash"]

    )



    print(

        "Size:",

        result["file_size"]

    )





    assert result["file_size"] > 0





    print(

        "✅ Archive Storage OK"

    )







if __name__ == "__main__":

    test_archive_storage()