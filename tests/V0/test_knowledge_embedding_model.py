"""
tests/test_knowledge_embedding_model.py

AutoSearch V4

P1.7 Step 4

Knowledge Embedding Model Test

"""


from models.knowledge_embedding import KnowledgeEmbedding


# ==================================================
# Test Create Model
# ==================================================


def test_knowledge_embedding_model():

    embedding = KnowledgeEmbedding(

        knowledge_id=1,

        vector=[

            0.82,

            0.61,

            0.93,

            0.74

        ],

        embedding_model="RuleEmbedding-V1"

    )

    print()

    print("================")
    print("Knowledge Embedding")
    print("================")

    print(

        embedding.to_dict()

    )

    assert embedding.knowledge_id == 1

    assert embedding.dimension == 4

    assert embedding.has_vector

    assert embedding.embedding_model == "RuleEmbedding-V1"


# ==================================================
# Test Dictionary
# ==================================================


def test_embedding_from_dict():

    data = {

        "id": 1,

        "knowledge_id": 10,

        "vector": [

            0.10,

            0.25,

            0.75

        ],

        "embedding_model": "RuleEmbedding-V1",

        "embedding_dimension": 3

    }

    embedding = KnowledgeEmbedding.from_dict(

        data

    )

    print()

    print("================")
    print("Embedding From Dict")
    print("================")

    print(

        embedding.to_dict()

    )

    assert embedding.id == 1

    assert embedding.knowledge_id == 10

    assert embedding.dimension == 3

    assert embedding.vector == [

        0.10,

        0.25,

        0.75

    ]

    assert embedding.embedding_model == "RuleEmbedding-V1"


# ==================================================
# Test Empty Vector
# ==================================================


def test_empty_embedding():

    embedding = KnowledgeEmbedding()

    print()

    print("================")
    print("Empty Embedding")
    print("================")

    print(

        embedding.to_dict()

    )

    assert embedding.dimension == 0

    assert embedding.has_vector is False

    assert embedding.vector == []


# ==================================================
# Test Display
# ==================================================


def test_embedding_repr():

    embedding = KnowledgeEmbedding(

        knowledge_id=5,

        vector=[

            0.2,

            0.4,

            0.6

        ]

    )

    print()

    print("================")
    print("Embedding Repr")
    print("================")

    print(

        embedding

    )

    assert "KnowledgeEmbedding" in repr(

        embedding

    )

    assert "knowledge_id=5" in repr(

        embedding

    )