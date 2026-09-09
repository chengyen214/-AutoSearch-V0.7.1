"""
rag/chroma_pipeline.py

AutoSearch V7

ChromaDB Index Pipeline


更改上限搜: BATCH_SIZE = 
用途：

    負責管理 MySQL Article
    進入 RAGPipeline
    並完成 ChromaDB Index。

執行模式：

    python -m rag.chroma_pipeline

    每次執行：

        1. 取得 MySQL Articles
        2. 找出尚未建立 ChromaDB Index 的 Article
        3. 一次只處理 10 筆
        4. 完成 RAG-1 → RAG-2 → RAG-3 → RAG-4
        5. 顯示本次處理結果
        6. 顯示剩餘未處理 Article 數量

架構：

    MySQL Articles
            ↓
    ChromaPipeline
            ↓
    找出未 Index Article
            ↓
    取前 10 筆
            ↓
    RAGPipeline
            ↓
    RAG-1 Document Preparation
            ↓
    RAG-2 Chunking
            ↓
    RAG-3 Embedding
            ↓
    RAG-4 ChromaDB Index
            ↓
        ChromaDB

本檔案負責：

    1. 取得 MySQL Articles
    2. 取得 Document ID
    3. 找出尚未 Index Article
    4. 每次處理固定數量 Article
    5. Full Index
    6. Incremental Index
    7. 顯示剩餘未處理數量
    8. 統計 Index 結果

本檔案不負責：

    1. Crawler
    2. Parser
    3. Article Persistence
    4. RAG-1 implementation
    5. RAG-2 implementation
    6. RAG-3 implementation
    7. RAG-4 implementation
    8. ChromaDB Client implementation
    9. ChromaDB Collection implementation
    10. ChromaDB Indexer implementation
    11. Retriever
    12. Context Builder
    13. LLM

重要原則：

    Crawler 與 ChromaDB 分離。

    Crawler：

        Crawler
            ↓
        Parser
            ↓
        MySQL
            ↓
        結束

    ChromaDB Index：

        python -m rag.chroma_pipeline
            ↓
        MySQL
            ↓
        找出未 Index Article
            ↓
        每次只處理 10 筆
            ↓
        RAGPipeline
            ↓
        RAG-1 → RAG-2 → RAG-3 → RAG-4
            ↓
        ChromaDB
"""


# ============================================================
# Imports
# ============================================================

from rag.rag_pipeline import (
    RAGPipeline
)

from database.article_repository import (
    ArticleRepository
)


# ============================================================
# Chroma Pipeline
# ============================================================

class ChromaPipeline:
    """
    AutoSearch V7 ChromaDB Index Pipeline。

    本類別是：

        MySQL → RAGPipeline

    的批次管理層。

    注意：

        每次執行只處理一批 Article。

        預設：

            BATCH_SIZE = 10
    """

    # ========================================================
    # Constants
    # ========================================================

    BATCH_SIZE = 10

    # ========================================================
    # Initialize
    # ========================================================

    def __init__(
        self,
        article_repository=None,
        rag_pipeline=None
    ):
        """
        初始化 Chroma Pipeline。

        Parameters:
            article_repository:
                現有 MySQL ArticleRepository。

            rag_pipeline:
                現有 RAGPipeline。

        支援 Dependency Injection。
        """

        # ----------------------------------------------------
        # Article Repository
        # ----------------------------------------------------

        self.article_repository = (
            article_repository
            if article_repository is not None
            else ArticleRepository()
        )

        # ----------------------------------------------------
        # RAG Pipeline
        #
        # 負責：
        #
        # RAG-1
        # RAG-2
        # RAG-3
        # RAG-4
        # ----------------------------------------------------

        self.rag_pipeline = (
            rag_pipeline
            if rag_pipeline is not None
            else RAGPipeline()
        )

    # ========================================================
    # Get Articles
    # ========================================================

    def get_articles(self):
        """
        從 MySQL 取得全部 Article。

        使用既有：

            ArticleRepository.find_all()

        注意：

            這裡不限制 10 筆。

            Batch Size 由本 Pipeline 控制。
        """

        articles = (
            self.article_repository
            .find_all()
        )

        if articles is None:
            return []

        if not isinstance(
            articles,
            list
        ):
            raise TypeError(
                "ArticleRepository.find_all() "
                "must return a list."
            )

        return articles

    # ========================================================
    # Get Document ID
    # ========================================================

    @staticmethod
    def get_document_id(
        article
    ):
        """
        從 Article dict / object
        取得 document_id。
        """

        if article is None:
            return None

        # ----------------------------------------------------
        # Dictionary
        # ----------------------------------------------------

        if isinstance(
            article,
            dict
        ):

            document_id = article.get(
                "document_id"
            )

        # ----------------------------------------------------
        # Object
        # ----------------------------------------------------

        else:

            document_id = getattr(
                article,
                "document_id",
                None
            )

        if document_id is None:
            return None

        document_id = str(
            document_id
        ).strip()

        if not document_id:
            return None

        return document_id

    # ========================================================
    # Get Chroma Indexer
    # ========================================================

    def get_chroma_indexer(self):
        """
        取得 RAGPipeline 使用的
        ChromaIndexer。

        ChromaIndexer 已經由：

            RAGPipeline

        建立。

        ChromaPipeline 不重新建立。
        """

        chroma_indexer = getattr(
            self.rag_pipeline,
            "chroma_indexer",
            None
        )

        if chroma_indexer is None:
            raise AttributeError(
                "RAGPipeline does not provide "
                "chroma_indexer."
            )

        return chroma_indexer

    # ========================================================
    # Get Indexed Document IDs
    # ========================================================

    def get_indexed_document_ids(self):
        """
        取得目前 ChromaDB 已經存在的
        document_id。

        Chroma Record：

            document_id::chunk_0
            document_id::chunk_1

        透過 Metadata：

            document_id

        判斷一篇 Article
        是否已有 Index。
        """

        chroma_indexer = (
            self.get_chroma_indexer()
        )

        collection = (
            chroma_indexer
            .get_collection()
        )

        result = collection.get(
            include=[
                "metadatas"
            ]
        )

        metadatas = (
            result.get(
                "metadatas"
            )
        )

        if not metadatas:
            return set()

        document_ids = set()

        for metadata in metadatas:

            if not isinstance(
                metadata,
                dict
            ):
                continue

            document_id = (
                metadata.get(
                    "document_id"
                )
            )

            if document_id is None:
                continue

            document_id = str(
                document_id
            ).strip()

            if document_id:
                document_ids.add(
                    document_id
                )

        return document_ids

    # ========================================================
    # Get Pending Articles
    # ========================================================

    def get_pending_articles(self):
        """
        取得尚未建立 ChromaDB Index 的 Article。

        回傳：

            list

        只保留：

            1. 有效 document_id
            2. 尚未存在於 ChromaDB

        注意：

            這裡不進行 Index。
        """

        articles = (
            self.get_articles()
        )

        indexed_document_ids = (
            self.get_indexed_document_ids()
        )

        pending_articles = []

        seen_document_ids = set()

        for article in articles:

            document_id = (
                self.get_document_id(
                    article
                )
            )

            # ------------------------------------------------
            # Missing Document ID
            # ------------------------------------------------

            if not document_id:
                continue

            # ------------------------------------------------
            # Already Indexed
            # ------------------------------------------------

            if (
                document_id
                in indexed_document_ids
            ):
                continue

            # ------------------------------------------------
            # Duplicate Article
            # ------------------------------------------------

            if (
                document_id
                in seen_document_ids
            ):
                continue

            seen_document_ids.add(
                document_id
            )

            pending_articles.append(
                article
            )

        return pending_articles

    # ========================================================
    # Index Article
    # ========================================================

    def index_article(
        self,
        document_id
    ):
        """
        Index 單一 Article。

        實際 RAG 流程：

            document_id
                ↓
            RAGPipeline
                ↓
            RAG-1
                ↓
            RAG-2
                ↓
            RAG-3
                ↓
            RAG-4
                ↓
            ChromaDB
        """

        if document_id is None:
            raise ValueError(
                "Document ID cannot be None."
            )

        document_id = str(
            document_id
        ).strip()

        if not document_id:
            raise ValueError(
                "Document ID cannot be empty."
            )

        result = (
            self.rag_pipeline
            .process_by_document_id(
                document_id
            )
        )

        if result is None:
            raise ValueError(
                "RAGPipeline returned None."
            )

        if not isinstance(
            result,
            dict
        ):
            raise TypeError(
                "RAGPipeline result "
                "must be a dict."
            )

        # ----------------------------------------------------
        # Required RAG-4 Result
        # ----------------------------------------------------

        record_ids = (
            result.get(
                "record_ids"
            )
        )

        indexed_count = (
            result.get(
                "indexed_count"
            )
        )

        if record_ids is None:
            raise ValueError(
                "RAGPipeline result does not "
                "contain record_ids."
            )

        if not isinstance(
            record_ids,
            list
        ):
            raise TypeError(
                "RAGPipeline record_ids "
                "must be a list."
            )

        if indexed_count is None:
            indexed_count = len(
                record_ids
            )

        if not isinstance(
            indexed_count,
            int
        ):
            raise TypeError(
                "RAGPipeline indexed_count "
                "must be an int."
            )

        return {
            "document_id": document_id,
            "chunk_count": len(
                result.get(
                    "chunks",
                    []
                )
            ),
            "indexed_count": indexed_count,
            "record_ids": record_ids
        }

    # ========================================================
    # Process Batch
    # ========================================================

    def process_batch(
        self,
        articles,
        batch_number
    ):
        """
        處理本次指定的 Article Batch。

        預設：

            10 Articles

        注意：

            每次程式執行只會呼叫一次
            process_batch()。
        """

        if not isinstance(
            articles,
            list
        ):
            raise TypeError(
                "Batch articles must be a list."
            )

        if not articles:
            return {
                "batch": batch_number,
                "batch_size": 0,
                "indexed_articles": 0,
                "skipped_articles": 0,
                "failed_articles": 0,
                "results": []
            }

        print(
            f"Processing Batch {batch_number}"
        )

        print(
            f"Batch Size: {len(articles)}"
        )

        print(
            "-" * 60
        )

        indexed_articles = 0
        skipped_articles = 0
        failed_articles = 0

        results = []

        for article in articles:

            document_id = (
                self.get_document_id(
                    article
                )
            )

            # ------------------------------------------------
            # Missing Document ID
            # ------------------------------------------------

            if not document_id:

                skipped_articles += 1

                results.append(
                    {
                        "document_id": None,
                        "status": "skipped",
                        "reason": (
                            "missing_document_id"
                        )
                    }
                )

                continue

            # ------------------------------------------------
            # Index
            # ------------------------------------------------

            try:

                result = (
                    self.index_article(
                        document_id
                    )
                )

                result["status"] = (
                    "indexed"
                )

                results.append(
                    result
                )

                indexed_articles += 1

                print(
                    f"PASS: {document_id}"
                )

            except Exception as error:

                failed_articles += 1

                results.append(
                    {
                        "document_id": (
                            document_id
                        ),
                        "status": "failed",
                        "error": str(
                            error
                        )
                    }
                )

                print(
                    f"FAIL: {document_id}"
                )

                print(
                    f"      {error}"
                )

        return {
            "batch": batch_number,
            "batch_size": len(
                articles
            ),
            "indexed_articles": (
                indexed_articles
            ),
            "skipped_articles": (
                skipped_articles
            ),
            "failed_articles": (
                failed_articles
            ),
            "results": results
        }

    # ========================================================
    # Incremental Index
    # ========================================================

    def incremental_index(self):
        """
        每次只處理最多 10 篇
        尚未建立 ChromaDB Index 的 Article。

        本方法：

            1. 找出所有未 Index Article
            2. 只取前 10 篇
            3. 處理這 10 篇
            4. 重新計算剩餘數量

        注意：

            一次：

                python -m rag.chroma_pipeline

            = 最多處理 10 篇

            下次再次執行：

                python -m rag.chroma_pipeline

            = 再處理下一批 10 篇。
        """

        # ----------------------------------------------------
        # Get Pending Articles
        # ----------------------------------------------------

        pending_articles = (
            self.get_pending_articles()
        )

        pending_before = (
            len(pending_articles)
        )

        # ----------------------------------------------------
        # Nothing To Do
        # ----------------------------------------------------

        if pending_before == 0:

            return {
                "mode": "incremental",
                "batch_size": self.BATCH_SIZE,
                "pending_before": 0,
                "processed_this_run": 0,
                "indexed_articles": 0,
                "skipped_articles": 0,
                "failed_articles": 0,
                "remaining_articles": 0,
                "results": [],
                "chroma_count": (
                    self.count()
                )
            }

        # ----------------------------------------------------
        # Take Only One Batch
        # ----------------------------------------------------

        batch_articles = (
            pending_articles[
                :self.BATCH_SIZE
            ]
        )

        batch_result = (
            self.process_batch(
                batch_articles,
                1
            )
        )

        # ----------------------------------------------------
        # Recalculate Remaining
        # ----------------------------------------------------

        pending_after = (
            self.get_pending_articles()
        )

        remaining_articles = (
            len(pending_after)
        )

        return {
            "mode": "incremental",
            "batch_size": self.BATCH_SIZE,
            "pending_before": pending_before,
            "processed_this_run": len(
                batch_articles
            ),
            "indexed_articles": (
                batch_result[
                    "indexed_articles"
                ]
            ),
            "skipped_articles": (
                batch_result[
                    "skipped_articles"
                ]
            ),
            "failed_articles": (
                batch_result[
                    "failed_articles"
                ]
            ),
            "remaining_articles": (
                remaining_articles
            ),
            "results": batch_result[
                "results"
            ],
            "chroma_count": (
                self.count()
            )
        }

    # ========================================================
    # Full Index
    # ========================================================

    def full_index(self):
        """
        全量 Index。

        注意：

            Full Index 仍然會把目前所有
            Article 全部處理。

        若要：

            每次只做 10 筆

        請使用：

            incremental_index()
        """

        articles = (
            self.get_articles()
        )

        indexed_articles = 0
        skipped_articles = 0
        failed_articles = 0

        results = []

        for article in articles:

            document_id = (
                self.get_document_id(
                    article
                )
            )

            # ------------------------------------------------
            # Missing Document ID
            # ------------------------------------------------

            if not document_id:

                skipped_articles += 1

                results.append(
                    {
                        "document_id": None,
                        "status": "skipped",
                        "reason": (
                            "missing_document_id"
                        )
                    }
                )

                continue

            # ------------------------------------------------
            # Index
            # ------------------------------------------------

            try:

                result = (
                    self.index_article(
                        document_id
                    )
                )

                result["status"] = (
                    "indexed"
                )

                results.append(
                    result
                )

                indexed_articles += 1

            except Exception as error:

                failed_articles += 1

                results.append(
                    {
                        "document_id": (
                            document_id
                        ),
                        "status": "failed",
                        "error": str(
                            error
                        )
                    }
                )

        return {
            "mode": "full",
            "total_articles": len(
                articles
            ),
            "indexed_articles": (
                indexed_articles
            ),
            "skipped_articles": (
                skipped_articles
            ),
            "failed_articles": (
                failed_articles
            ),
            "results": results,
            "chroma_count": (
                self.count()
            )
        }

    # ========================================================
    # Count
    # ========================================================

    def count(self):
        """
        取得 ChromaDB Record Count。
        """

        chroma_indexer = (
            self.get_chroma_indexer()
        )

        return (
            chroma_indexer.count()
        )


# ============================================================
# Main
# ============================================================

def main():
    """
    每次執行只處理最多 10 筆。

    使用：

        python -m rag.chroma_pipeline

    行為：

        第一次：
            處理最多 10 筆
            顯示剩餘數量

        第二次：
            再處理最多 10 筆
            顯示剩餘數量

        持續執行直到：

            Remaining Articles = 0
    """

    print(
        "=" * 60
    )

    print(
        "AutoSearch V7 ChromaDB Index Pipeline"
    )

    print(
        "=" * 60
    )

    print()

    print(
        f"Batch Size: "
        f"{ChromaPipeline.BATCH_SIZE}"
    )

    print(
        "Mode: Incremental Index"
    )

    print()

    pipeline = (
        ChromaPipeline()
    )

    result = (
        pipeline.incremental_index()
    )

    print()

    print(
        "=" * 60
    )

    print(
        "Index Summary"
    )

    print(
        "=" * 60
    )

    print(
        f"Pending Before: "
        f"{result['pending_before']}"
    )

    print(
        f"Processed This Run: "
        f"{result['processed_this_run']}"
    )

    print(
        f"Indexed Articles: "
        f"{result['indexed_articles']}"
    )

    print(
        f"Skipped Articles: "
        f"{result['skipped_articles']}"
    )

    print(
        f"Failed Articles: "
        f"{result['failed_articles']}"
    )

    print(
        f"Remaining Articles: "
        f"{result['remaining_articles']}"
    )

    print(
        f"ChromaDB Count: "
        f"{result['chroma_count']}"
    )

    # --------------------------------------------------------
    # Failed Documents
    # --------------------------------------------------------

    failed_results = [
        item
        for item in result[
            "results"
        ]
        if item.get(
            "status"
        ) == "failed"
    ]

    if failed_results:

        print()

        print(
            "Failed Documents:"
        )

        for item in failed_results:

            print(
                f"  {item['document_id']}: "
                f"{item['error']}"
            )

    print()

    if (
        result["remaining_articles"]
        == 0
    ):

        print(
            "ALL PENDING ARTICLES "
            "HAVE BEEN INDEXED."
        )

    else:

        print(
            f"{result['remaining_articles']} "
            "articles remaining."
        )

    print()

    print(
        "=" * 60
    )

    print(
        "ChromaDB Incremental Index Completed"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()


__all__ = [
    "ChromaPipeline"
]