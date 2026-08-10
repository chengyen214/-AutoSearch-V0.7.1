"""
models/knowledge_embedding.py

AutoSearch V4

P1.7 Step 4

Knowledge Embedding Model


用途:

    保存 Knowledge 的向量表示 (Embedding)

流程:

Knowledge
      |
      v
Embedding Service
      |
      v
Knowledge Embedding
      |
      v
Semantic Search


Future:

    - OpenAI Embedding
    - Sentence Transformers
    - FAISS
    - ChromaDB
    - Milvus

"""


from datetime import datetime


class KnowledgeEmbedding:
    """
    Knowledge Embedding Model
    """

    def __init__(
        self,
        knowledge_id=None,
        vector=None,
        embedding_model="RuleEmbedding-V1",
        embedding_dimension=0,
        created_time=None
    ):

        # ==========================
        # Database ID
        # ==========================

        self.id = None

        # ==========================
        # Knowledge Relation
        # ==========================

        self.knowledge_id = knowledge_id

        # ==========================
        # Embedding
        # ==========================

        self.vector = vector if vector is not None else []

        self.embedding_model = embedding_model

        self.embedding_dimension = (
            embedding_dimension
            if embedding_dimension > 0
            else len(self.vector)
        )

        # ==========================
        # Time
        # ==========================

        self.created_time = (
            created_time
            if created_time
            else datetime.now()
        )

    # ==================================
    # Property
    # ==================================

    @property
    def has_vector(self):
        """
        是否已有 Embedding
        """

        return len(self.vector) > 0

    @property
    def dimension(self):
        """
        Vector 維度
        """

        return len(self.vector)

    # ==================================
    # Dictionary
    # ==================================

    def to_dict(self):

        return {

            "id": self.id,

            "knowledge_id": self.knowledge_id,

            "vector": self.vector,

            "embedding_model": self.embedding_model,

            "embedding_dimension": self.embedding_dimension,

            "created_time": self.created_time

        }

    # ==================================
    # From Dictionary
    # ==================================

    @classmethod
    def from_dict(cls, data):

        obj = cls(

            knowledge_id=data.get("knowledge_id"),

            vector=data.get("vector", []),

            embedding_model=data.get(
                "embedding_model",
                "RuleEmbedding-V1"
            ),

            embedding_dimension=data.get(
                "embedding_dimension",
                0
            ),

            created_time=data.get(
                "created_time"
            )

        )

        obj.id = data.get("id")

        return obj

    # ==================================
    # Display
    # ==================================

    def __repr__(self):

        return (

            "KnowledgeEmbedding("

            f"knowledge_id={self.knowledge_id}, "

            f"dimension={self.dimension}, "

            f"model={self.embedding_model}"

            ")"

        )