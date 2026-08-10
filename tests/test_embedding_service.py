"""
tests/test_embedding_service.py

AutoSearch V4

P1.7 Step 4.2

Embedding Service Test

"""


from ai.embedding_service import EmbeddingService
from models.knowledge import Knowledge


# ==================================================
# Generate Embedding
# ==================================================


def test_generate_embedding():

    service = EmbeddingService()

    text = """
    台積電2nm先進製程，
    CoWoS需求提升，
    AI Chip市場持續成長。
    """

    vector = service.generate_embedding(

        text

    )

    print()

    print("================")
    print("Generate Embedding")
    print("================")

    print(vector)

    assert len(vector) == len(

        service.features

    )

    assert sum(vector) > 0


# ==================================================
# Build Knowledge Embedding
# ==================================================


def test_build_embedding():

    service = EmbeddingService()

    knowledge = Knowledge(

        article_id=1,

        topic="Semiconductor",

        entities=[

            "台積電",

            "2nm",

            "CoWoS",

            "AI"

        ],

        relations=[

            "台積電先進製程與AI需求成長"

        ]

    )

    knowledge.id = 1

    embedding = service.build(

        knowledge

    )

    print()

    print("================")
    print("Knowledge Embedding")
    print("================")

    print(

        embedding.to_dict()

    )

    assert embedding.knowledge_id == 1

    assert embedding.has_vector

    assert embedding.dimension == len(

        service.features

    )

    assert embedding.embedding_model == "RuleEmbedding-V1"


# ==================================================
# Similarity
# ==================================================


def test_similarity():

    service = EmbeddingService()

    vector1 = [

        1, 1, 1, 0,

        1, 0, 1, 0,

        0, 0, 0, 0

    ]

    vector2 = [

        1, 0, 1, 0,

        1, 0, 1, 0,

        0, 0, 0, 0

    ]

    score = service.similarity(

        vector1,

        vector2

    )

    print()

    print("================")
    print("Similarity")
    print("================")

    print(score)

    assert score > 0

    assert score <= 1


# ==================================================
# Empty Text
# ==================================================


def test_empty_embedding():

    service = EmbeddingService()

    vector = service.generate_embedding(

        ""

    )

    print()

    print("================")
    print("Empty Embedding")
    print("================")

    print(vector)

    assert vector == []