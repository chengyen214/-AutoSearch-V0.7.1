"""
tests/test_search_index_model.py

AutoSearch V4

P2.2 Step 2

Search Index Model Test

"""


from models.search_index import (
    SearchIndex
)





# ==================================
# Create Model
# ==================================


def test_search_index_model():


    index = SearchIndex(


        id=1,


        knowledge_id=1,


        search_text=(

            "Semiconductor AI 2nm CoWoS"

        ),


        keywords=(

            "AI,2nm,CoWoS"

        ),


        entities=(

            "台積電,CoWoS"

        ),


        topic=(

            "Semiconductor"

        )

    )



    assert index.id == 1


    assert index.knowledge_id == 1


    assert (

        "CoWoS"

        in index.search_text

    )


    assert (

        index.topic

        ==

        "Semiconductor"

    )







# ==================================
# to_dict
# ==================================


def test_search_index_to_dict():


    index = SearchIndex(


        id=1,


        knowledge_id=1,


        search_text="AI CoWoS"

    )



    data = index.to_dict()



    assert data["id"] == 1


    assert data["knowledge_id"] == 1


    assert (

        data["search_text"]

        ==

        "AI CoWoS"

    )








# ==================================
# from_dict
# ==================================


def test_search_index_from_dict():


    data = {


        "id": 1,


        "knowledge_id": 1,


        "search_text":

            "AI semiconductor",


        "keywords":

            "AI",


        "topic":

            "Semiconductor"


    }



    index = SearchIndex.from_dict(

        data

    )



    assert index.id == 1


    assert index.knowledge_id == 1


    assert (

        index.topic

        ==

        "Semiconductor"

    )







# ==================================
# Empty Index
# ==================================


def test_empty_search_index():


    index = SearchIndex()



    assert index.id is None


    assert index.knowledge_id is None


    assert index.search_text == ""


    assert index.index_version == "1.0"







# ==================================
# repr
# ==================================


def test_search_index_repr():


    index = SearchIndex(


        id=1,


        knowledge_id=10,


        topic="AI"

    )



    result = repr(index)



    assert "SearchIndex" in result


    assert "knowledge_id=10" in result