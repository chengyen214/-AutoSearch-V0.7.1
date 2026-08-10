"""
ai/embedding_service.py

AutoSearch V4

P1.7 Step 4.2

Embedding Service


功能:

1. Text -> Embedding Vector

2. Semantic Feature Extraction

3. Future OpenAI / BGE Interface


Current:

Rule Based Embedding


Future:

OpenAI Embedding API

Sentence Transformer

BGE

E5

FAISS

ChromaDB

"""


from models.knowledge_embedding import KnowledgeEmbedding


class EmbeddingService:
    """
    Rule Based Embedding Service

    V4 P1.7
    """

    def __init__(self):

        self.model = "RuleEmbedding-V1"

        # ==================================
        # Embedding Vocabulary
        # ==================================

        self.features = [

            "台積電",
            "TSMC",

            "2nm",
            "3nm",

            "CoWoS",
            "HBM",

            "AI",
            "AI Chip",

            "IC",
            "半導體",

            "晶圓",
            "先進製程"

        ]

    # ==================================
    # Generate Embedding
    # ==================================

    def generate_embedding(
        self,
        text
    ):
        """
        Text

            |

            v

        Embedding Vector
        """

        if not text:

            return []

        text = text.lower()

        vector = []

        for feature in self.features:

            if feature.lower() in text:

                vector.append(1.0)

            else:

                vector.append(0.0)

        return vector

    # ==================================
    # Build Knowledge Embedding
    # ==================================

    def build(
        self,
        knowledge
    ):
        """
        Knowledge

            |

            v

        KnowledgeEmbedding
        """

        text = " ".join([

            knowledge.topic or "",

            " ".join(knowledge.entity_list),

            " ".join(knowledge.relation_list)

        ])

        vector = self.generate_embedding(

            text

        )

        embedding = KnowledgeEmbedding(

            knowledge_id=knowledge.id,

            vector=vector,

            embedding_model=self.model

        )

        return embedding

    # ==================================
    # Similarity
    # ==================================

    def similarity(
        self,
        vector1,
        vector2
    ):
        """
        Cosine-like Similarity

        (Rule Based)
        """

        if not vector1 or not vector2:

            return 0.0

        same = 0

        total = max(

            len(vector1),

            len(vector2)

        )

        for a, b in zip(vector1, vector2):

            if a == b == 1:

                same += 1

        return round(

            same / total,

            3

        )