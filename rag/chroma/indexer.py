"""
rag/chroma/indexer.py

AutoSearch V7

RAG-4.4

ChromaDB Indexer

功能：

    將 RAG-3 產生的：

        Document
        Embedding
        Metadata

    寫入 ChromaDB Collection。

同時負責：

    1. ChromaDB Document Index
    2. Chroma Record ID Mapping
    3. Metadata Mapping
    4. Single Mapping Index
    5. Multiple Mapping Index
    6. Upsert
    7. Read Record
    8. Index Count

資料流程：

    RAG-3 EmbeddingPipeline
            ↓
    {
        "document": Document,
        "embedding": list[float]
    }
            ↓
    ChromaIndexer
            ↓
    ┌──────────────────────────────┐
    │ Chroma Record                │
    │                              │
    │ id                           │
    │ document                     │
    │ embedding                    │
    │ metadata                     │
    └──────────────────────────────┘
            ↓
    ChromaDB Collection


Record ID 格式：

    {document_id}::chunk_{chunk_index}

例如：

    abc123::chunk_0
    abc123::chunk_1
    abc123::chunk_2


Metadata Mapping：

    LangChain Document.metadata
                ↓
         ChromaDB metadata


正式 Metadata：

    1. document_id
    2. title
    3. url
    4. keyword
    5. source
    6. crawl_time
    7. ai_summary
    8. ai_category
    9. ai_keywords
    10. ai_importance
    11. ai_confidence


本檔案不負責：

    1. MySQL
    2. MCP
    3. Document Preparation
    4. Chunking
    5. Embedding Generation
    6. Qwen Model
    7. Retriever
    8. Full Indexing Pipeline
    9. Incremental Pipeline


RAG-4.4 與 RAG-4.5：

    原本：

        RAG-4.4 Index Document
        RAG-4.5 ID / Metadata Mapping

    現在合併成：

        RAG-4.4 ChromaDB Indexer

    所有 Index + ID + Metadata Mapping
    都在本檔案完成。
"""


from langchain_core.documents import (
    Document
)

from rag.chroma.collection import (
    ChromaCollection
)


class ChromaIndexer:
    """
    RAG-4.4 ChromaDB Indexer。

    負責：

        RAG-3 Mapping
              ↓
        ChromaDB Record

    同時負責：

        ID Mapping
        Metadata Mapping
    """

    # ==================================================
    # Metadata Schema
    # ==================================================

    METADATA_FIELDS = (
        "document_id",
        "title",
        "url",
        "keyword",
        "source",
        "crawl_time",
        "ai_summary",
        "ai_category",
        "ai_keywords",
        "ai_importance",
        "ai_confidence",
    )

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        chroma_collection=None
    ):
        """
        初始化 ChromaIndexer。

        Parameters:
            chroma_collection:
                RAG-4.3 ChromaCollection。

                若未提供，
                自動建立 ChromaCollection。
        """

        self.chroma_collection = (
            chroma_collection
            if chroma_collection is not None
            else ChromaCollection()
        )

        self.collection = (
            self.chroma_collection
            .get_collection()
        )

    # ==================================================
    # Validate RAG-3 Mapping
    # ==================================================

    @classmethod
    def _validate_mapping(
        cls,
        mapping
    ):
        """
        驗證 RAG-3 Embedding Mapping。

        Mapping：

            {
                "document": Document,
                "embedding": list[float]
            }
        """

        if mapping is None:
            raise ValueError(
                "Mapping cannot be None."
            )

        if not isinstance(
            mapping,
            dict
        ):
            raise TypeError(
                "Mapping must be a dict."
            )

        if "document" not in mapping:
            raise ValueError(
                "Mapping is missing 'document'."
            )

        if "embedding" not in mapping:
            raise ValueError(
                "Mapping is missing 'embedding'."
            )

        document = mapping[
            "document"
        ]

        embedding = mapping[
            "embedding"
        ]

        if not isinstance(
            document,
            Document
        ):
            raise TypeError(
                "Mapping document must be a "
                "LangChain Document."
            )

        if not isinstance(
            document.page_content,
            str
        ):
            raise TypeError(
                "Document.page_content must be a str."
            )

        if not document.page_content.strip():
            raise ValueError(
                "Mapping document content "
                "cannot be empty."
            )

        if not isinstance(
            embedding,
            list
        ):
            raise TypeError(
                "Mapping embedding must be a list."
            )

        if not embedding:
            raise ValueError(
                "Mapping embedding cannot be empty."
            )

        return True

    # ==================================================
    # Validate Multiple Mappings
    # ==================================================

    @classmethod
    def _validate_mappings(
        cls,
        mappings
    ):
        """
        驗證多個 RAG-3 Mappings。
        """

        if mappings is None:
            raise ValueError(
                "Mappings cannot be None."
            )

        if not isinstance(
            mappings,
            list
        ):
            raise TypeError(
                "Mappings must be a list."
            )

        if not mappings:
            raise ValueError(
                "Mappings cannot be empty."
            )

        for index, mapping in enumerate(
            mappings
        ):

            try:

                cls._validate_mapping(
                    mapping
                )

            except (
                TypeError,
                ValueError
            ) as error:

                raise type(error)(
                    f"Mapping {index} validation failed: "
                    f"{error}"
                ) from error

        return True

    # ==================================================
    # Create Record ID
    # ==================================================

    @classmethod
    def create_record_id(
        cls,
        document,
        chunk_index=0
    ):
        """
        建立 ChromaDB Record ID。

        格式：

            {document_id}::chunk_{index}

        例如：

            abc123::chunk_0
            abc123::chunk_1
        """

        if not isinstance(
            document,
            Document
        ):
            raise TypeError(
                "Document must be a LangChain Document."
            )

        document_id = (
            document.metadata.get(
                "document_id"
            )
        )

        if document_id is None:
            raise ValueError(
                "Document metadata must contain "
                "'document_id'."
            )

        document_id = str(
            document_id
        ).strip()

        if not document_id:
            raise ValueError(
                "Document ID cannot be empty."
            )

        if not isinstance(
            chunk_index,
            int
        ):
            raise TypeError(
                "Chunk index must be an int."
            )

        if chunk_index < 0:
            raise ValueError(
                "Chunk index cannot be negative."
            )

        return (
            f"{document_id}::chunk_{chunk_index}"
        )

    # ==================================================
    # Parse Record ID
    # ==================================================

    @staticmethod
    def parse_record_id(
        record_id
    ):
        """
        解析 Chroma Record ID。

        Returns:

            {
                "document_id": "...",
                "chunk_index": 0
            }
        """

        if record_id is None:
            raise ValueError(
                "Record ID cannot be None."
            )

        record_id = str(
            record_id
        ).strip()

        if not record_id:
            raise ValueError(
                "Record ID cannot be empty."
            )

        separator = "::chunk_"

        if separator not in record_id:
            raise ValueError(
                "Invalid Chroma Record ID format."
            )

        document_id, chunk_index_text = (
            record_id.rsplit(
                separator,
                1
            )
        )

        if not document_id:
            raise ValueError(
                "Record ID contains empty document ID."
            )

        try:

            chunk_index = int(
                chunk_index_text
            )

        except ValueError as error:

            raise ValueError(
                "Record ID contains invalid chunk index."
            ) from error

        if chunk_index < 0:
            raise ValueError(
                "Chunk index cannot be negative."
            )

        return {
            "document_id": document_id,
            "chunk_index": chunk_index,
        }

    # ==================================================
    # Metadata Mapping
    # ==================================================

    @classmethod
    def to_chroma_metadata(
        cls,
        metadata
    ):
        """
        將 LangChain Document Metadata
        轉換成 ChromaDB Metadata。

        ChromaDB 不接受 None，
        因此 None 統一轉成空字串。

        其他 scalar 型別直接保留。

        Returns:

            dict
        """

        if metadata is None:
            raise ValueError(
                "Metadata cannot be None."
            )

        if not isinstance(
            metadata,
            dict
        ):
            raise TypeError(
                "Metadata must be a dict."
            )

        normalized = {}

        for field in cls.METADATA_FIELDS:

            value = metadata.get(
                field
            )

            if value is None:

                normalized[
                    field
                ] = ""

            elif isinstance(
                value,
                (str, int, float, bool)
            ):

                normalized[
                    field
                ] = value

            else:

                normalized[
                    field
                ] = str(
                    value
                )

        return normalized

    # ==================================================
    # Metadata Validation
    # ==================================================

    @classmethod
    def validate_metadata(
        cls,
        metadata
    ):
        """
        驗證 Metadata Schema。
        """

        if metadata is None:
            raise ValueError(
                "Metadata cannot be None."
            )

        if not isinstance(
            metadata,
            dict
        ):
            raise TypeError(
                "Metadata must be a dict."
            )

        actual_fields = set(
            metadata.keys()
        )

        expected_fields = set(
            cls.METADATA_FIELDS
        )

        if actual_fields != expected_fields:

            raise ValueError(
                "Metadata fields mismatch: "
                f"expected={expected_fields}, "
                f"got={actual_fields}"
            )

        return True

    # ==================================================
    # Build Chroma Mapping
    # ==================================================

    @classmethod
    def map_document(
        cls,
        document,
        chunk_index=0
    ):
        """
        建立 Document → Chroma Mapping。

        Returns:

            {
                "id": "...",
                "document_id": "...",
                "chunk_index": 0,
                "metadata": {...}
            }
        """

        if not isinstance(
            document,
            Document
        ):
            raise TypeError(
                "Document must be a LangChain Document."
            )

        record_id = (
            cls.create_record_id(
                document,
                chunk_index
            )
        )

        metadata = (
            cls.to_chroma_metadata(
                document.metadata
            )
        )

        return {
            "id": record_id,

            "document_id": (
                str(
                    document.metadata[
                        "document_id"
                    ]
                ).strip()
            ),

            "chunk_index": chunk_index,

            "metadata": metadata,
        }

    # ==================================================
    # Build Multiple Chroma Mappings
    # ==================================================

    @classmethod
    def map_documents(
        cls,
        documents
    ):
        """
        建立多個 Documents 的
        Chroma ID / Metadata Mapping。
        """

        if documents is None:
            raise ValueError(
                "Documents cannot be None."
            )

        if not isinstance(
            documents,
            list
        ):
            raise TypeError(
                "Documents must be a list."
            )

        if not documents:
            raise ValueError(
                "Documents cannot be empty."
            )

        mappings = []

        for index, document in enumerate(
            documents
        ):

            mappings.append(
                cls.map_document(
                    document,
                    index
                )
            )

        return mappings

    # ==================================================
    # Validate Mapping
    # ==================================================

    @classmethod
    def validate_mapping(
        cls,
        mapping
    ):
        """
        驗證 Chroma ID / Metadata Mapping。
        """

        if mapping is None:
            raise ValueError(
                "Mapping cannot be None."
            )

        if not isinstance(
            mapping,
            dict
        ):
            raise TypeError(
                "Mapping must be a dict."
            )

        required_fields = {
            "id",
            "document_id",
            "chunk_index",
            "metadata",
        }

        if set(
            mapping.keys()
        ) != required_fields:

            raise ValueError(
                "Mapping fields mismatch."
            )

        parsed = cls.parse_record_id(
            mapping["id"]
        )

        if (
            parsed["document_id"]
            != str(
                mapping["document_id"]
            ).strip()
        ):
            raise ValueError(
                "Record ID document_id "
                "does not match mapping."
            )

        if (
            parsed["chunk_index"]
            != mapping["chunk_index"]
        ):
            raise ValueError(
                "Record ID chunk_index "
                "does not match mapping."
            )

        if not isinstance(
            mapping["chunk_index"],
            int
        ):
            raise TypeError(
                "Chunk index must be an int."
            )

        if mapping["chunk_index"] < 0:
            raise ValueError(
                "Chunk index cannot be negative."
            )

        cls.validate_metadata(
            mapping["metadata"]
        )

        return True

    # ==================================================
    # Validate Multiple Mappings
    # ==================================================

    @classmethod
    def validate_mappings(
        cls,
        mappings
    ):
        """
        驗證多個 Chroma Mappings。
        """

        if mappings is None:
            raise ValueError(
                "Mappings cannot be None."
            )

        if not isinstance(
            mappings,
            list
        ):
            raise TypeError(
                "Mappings must be a list."
            )

        if not mappings:
            raise ValueError(
                "Mappings cannot be empty."
            )

        for index, mapping in enumerate(
            mappings
        ):

            try:

                cls.validate_mapping(
                    mapping
                )

            except (
                TypeError,
                ValueError
            ) as error:

                raise type(error)(
                    f"Mapping {index} validation failed: "
                    f"{error}"
                ) from error

        return True

    # ==================================================
    # Normalize RAG-3 Mapping
    # ==================================================

    @classmethod
    def _normalize_rag3_mapping(
        cls,
        mapping,
        chunk_index=0
    ):
        """
        將 RAG-3 Mapping
        轉換成 ChromaDB Index Record。

        Returns:

            {
                "id": "...",
                "document": Document,
                "embedding": [...],
                "metadata": {...}
            }
        """

        cls._validate_mapping(
            mapping
        )

        document = mapping[
            "document"
        ]

        embedding = mapping[
            "embedding"
        ]

        chroma_mapping = (
            cls.map_document(
                document,
                chunk_index
            )
        )

        return {
            "id": chroma_mapping[
                "id"
            ],

            "document": document,

            "embedding": embedding,

            "metadata": chroma_mapping[
                "metadata"
            ],
        }

    # ==================================================
    # Index Single Mapping
    # ==================================================

    def index_mapping(
        self,
        mapping,
        chunk_index=0
    ):
        """
        將單一 RAG-3 Mapping
        寫入 ChromaDB。

        Returns:
            str
                ChromaDB Record ID
        """

        normalized = (
            self._normalize_rag3_mapping(
                mapping,
                chunk_index
            )
        )

        self.collection.upsert(
            ids=[
                normalized["id"]
            ],

            documents=[
                normalized[
                    "document"
                ].page_content
            ],

            embeddings=[
                normalized[
                    "embedding"
                ]
            ],

            metadatas=[
                normalized[
                    "metadata"
                ]
            ]
        )

        return normalized[
            "id"
        ]

    # ==================================================
    # Index Multiple Mappings
    # ==================================================

    def index_mappings(
        self,
        mappings
    ):
        """
        將多個 RAG-3 Mappings
        批次寫入 ChromaDB。

        Returns:
            list[str]
                ChromaDB Record IDs
        """

        self._validate_mappings(
            mappings
        )

        ids = []
        documents = []
        embeddings = []
        metadatas = []

        for index, mapping in enumerate(
            mappings
        ):

            normalized = (
                self._normalize_rag3_mapping(
                    mapping,
                    index
                )
            )

            ids.append(
                normalized[
                    "id"
                ]
            )

            documents.append(
                normalized[
                    "document"
                ].page_content
            )

            embeddings.append(
                normalized[
                    "embedding"
                ]
            )

            metadatas.append(
                normalized[
                    "metadata"
                ]
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return ids

    # ==================================================
    # Get Record
    # ==================================================

    def get_record(
        self,
        record_id
    ):
        """
        取得指定 ChromaDB Record。
        """

        if record_id is None:
            raise ValueError(
                "Record ID cannot be None."
            )

        record_id = str(
            record_id
        ).strip()

        if not record_id:
            raise ValueError(
                "Record ID cannot be empty."
            )

        return self.collection.get(
            ids=[
                record_id
            ],

            include=[
                "documents",
                "metadatas",
                "embeddings",
            ]
        )

    # ==================================================
    # Get Count
    # ==================================================

    def count(self):
        """
        取得目前 Collection Record Count。
        """

        return self.collection.count()

    # ==================================================
    # Get Collection
    # ==================================================

    def get_collection(self):
        """
        取得 ChromaDB Collection。
        """

        return self.collection


__all__ = [
    "ChromaIndexer"
]