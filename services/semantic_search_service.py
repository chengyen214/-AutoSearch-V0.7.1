"""
services/semantic_search_service.py

AutoSearch V4

P1.7 Step 4.3

Semantic Search Service


Flow:

Query

    |

    v

Embedding Service

    |

    v

Query Embedding

    |

    v

Knowledge Repository

    |

    v

Knowledge Embedding

    |

    v

Similarity

    |

    v

Semantic Ranking


Future:

    - OpenAI Embedding
    - Sentence Transformer
    - FAISS
    - ChromaDB
    - Milvus

"""


from ai.embedding_service import EmbeddingService

from database.knowledge_repository import (
    KnowledgeRepository
)

from models.knowledge import Knowledge

from utils.logger import logger


class SemanticSearchService:
    """
    Semantic Search Service

    V4 P1.7
    """

    def __init__(self):

        self.repository = KnowledgeRepository()

        self.embedding_service = EmbeddingService()

    # ==================================================
    # Semantic Search
    # ==================================================

    def search(
        self,
        query,
        top_k=10
    ):
        """
        Query

            |

            v

        Semantic Search

        return:

            List
        """

        if not query:

            return []

        # ==========================
        # Query Embedding
        # ==========================

        query_vector = (

            self.embedding_service.generate_embedding(

                query

            )

        )

        # ==========================
        # Get Knowledge
        # ==========================

        knowledge_list = (

            self.repository.search(

                ""

            )
            
            or []

        )               
        results = []

        # ==========================
        # Similarity Calculate
        # ==========================

        for knowledge in knowledge_list:

            # ----------------------------------
            # Repository 回傳 Dictionary
            # ----------------------------------

            if isinstance(

                knowledge,

                dict

            ):

                raw = knowledge

                knowledge = Knowledge(

                    article_id=raw.get(

                        "article_id"

                    ),

                    topic=raw.get(

                        "topic"

                    ),

                    entities=raw.get(

                        "entities"

                    ),

                    relations=raw.get(

                        "relations"

                    ),

                    knowledge_version=raw.get(

                        "knowledge_version",

                        "1.0"

                    ),

                    created_time=raw.get(

                        "created_time"

                    )

                )

                knowledge.id = raw.get(

                    "id"

                )

            # ----------------------------------
            # Build Embedding
            # ----------------------------------

            embedding = (

                self.embedding_service.build(

                    knowledge

                )

            )

            similarity = (

                self.embedding_service.similarity(

                    query_vector,

                    embedding.vector

                )

            )

            results.append(

                {

                    "knowledge": knowledge,

                    "embedding": embedding,

                    "semantic_score": similarity

                }

            )

        # ==========================
        # Ranking
        # ==========================

        results.sort(

            key=lambda x:

            x["semantic_score"],

            reverse=True

        )

        logger.info(

            f"Semantic search: {query}, count={len(results)}"

        )

        return results[:top_k]