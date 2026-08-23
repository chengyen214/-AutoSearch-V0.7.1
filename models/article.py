"""
models/article.py

AutoSearch V5

Article Data Model

用途：

    表示 Parser 完成後的 Article。

目前 Pipeline：

    Crawl
      ↓
    Parser
      ↓
    Article
      ↓
    ArticleRepository
      ↓
    SQL
      ↓
    AI Task / AI Batch Trigger

設計原則：

    Article 負責保存：

        - 非 AI 分析資料
        - AI Pipeline 狀態
        - AI 分析結果容器
        - Raw Document 關聯
        - Metadata 關聯
        - Knowledge 關聯

    Article 不負責：

        - SQL 儲存
        - AI 分析
        - AI Pool Trigger
        - AI Threshold 判斷
        - Scheduler
        - Worker
        - Archive Pipeline 執行
"""

from datetime import datetime


class Article:
    """
    Article Data Model。

    Pipeline 中的位置：

        CrawlResult
            ↓
        Parser
            ↓
        Article
            ↓
        ArticleRepository
            ↓
        SQL

    AI 分析屬於後續 Async Pipeline。
    """

    def __init__(
        self,
        keyword="",
        title="",
        url="",
        published=None,
        source="",
        content="",
        crawl_time=None,
        status="Success",
        document_id="",
    ):
        # ==================================================
        #
        # Database ID
        #
        # ==================================================

        self.id = None

        # ==================================================
        #
        # Article Basic Data
        #
        # Parser 完成後即應存在。
        #
        # ==================================================

        self.keyword = keyword

        self.title = title

        self.url = url

        self.published = published

        self.source = source

        self.content = content

        self.crawl_time = (
            crawl_time
            if crawl_time is not None
            else datetime.now()
        )

        self.status = status

        self.document_id = document_id

        # ==================================================
        #
        # Async AI Pipeline Status
        #
        # pending
        # processing
        # completed
        # failed
        #
        # 注意：
        #
        # ai_status 只是 Article 的狀態。
        #
        # Pool threshold / Trigger
        # 由外部 AI Batch Trigger Service 負責。
        #
        # ==================================================

        self.ai_status = "pending"

        # ==================================================
        #
        # AI Analysis
        #
        # ==================================================

        # Parser / Article 建立時：
        #
        #     尚未進行 AI Analysis
        #
        # 因此保持 None。
        #
        # 後續 AI Service 完成分析後，
        # 才會將 AIAnalysis instance 放入此欄位。
        #
        self.ai_analysis = None

        # ==================================================
        #
        # V4 / V5 Archive Relations
        #
        # ==================================================

        # RawDocument instance
        self.raw_document = None

        # ArticleMetadata instance
        self.metadata = None

        # Knowledge instance
        self.knowledge = None

    # ==================================================
    #
    # AI Properties
    #
    # ==================================================

    @property
    def ai_summary(self):
        """
        取得 AI Summary。

        尚未分析：

            None

        已完成分析：

            AI Analysis Summary
        """

        if self.ai_analysis is not None:

            return getattr(
                self.ai_analysis,
                "summary",
                None,
            )

        return None

    @property
    def ai_category(self):
        """
        取得 AI Category。

        尚未分析：

            None
        """

        if self.ai_analysis is not None:

            return getattr(
                self.ai_analysis,
                "category",
                None,
            )

        return None

    @property
    def ai_keywords(self):
        """
        取得 AI Keywords。

        尚未分析：

            None

        已完成分析：

            list
        """

        if self.ai_analysis is not None:

            return getattr(
                self.ai_analysis,
                "keywords",
                None,
            )

        return None

    @property
    def ai_importance(self):
        """
        取得 AI Importance。

        尚未分析：

            None
        """

        if self.ai_analysis is not None:

            value = getattr(
                self.ai_analysis,
                "importance",
                None,
            )

            if value is None:
                return None

            return int(value)

        return None

    @property
    def ai_model(self):
        """
        取得實際執行 AI Analysis 的模型。

        尚未分析：

            None
        """

        if self.ai_analysis is not None:

            return getattr(
                self.ai_analysis,
                "ai_model",
                None,
            )

        return None

    @property
    def ai_version(self):
        """
        取得 AI Analysis Version。

        尚未分析：

            None
        """

        if self.ai_analysis is not None:

            return getattr(
                self.ai_analysis,
                "ai_version",
                None,
            )

        return None

    @property
    def ai_analyze_time(self):
        """
        取得 AI Analysis 時間。

        尚未分析：

            None
        """

        if self.ai_analysis is not None:

            return getattr(
                self.ai_analysis,
                "analyze_time",
                None,
            )

        return None

    @property
    def ai_confidence(self):
        """
        取得 AI Analysis Confidence。

        尚未分析：

            None
        """

        if self.ai_analysis is not None:

            value = getattr(
                self.ai_analysis,
                "confidence",
                None,
            )

            if value is None:
                return None

            return float(value)

        return None

    # ==================================================
    #
    # V4 / V5 Archive Properties
    #
    # ==================================================

    @property
    def archive_path(self):
        """
        取得 Raw Document Storage Path。
        """

        if self.raw_document is not None:

            return getattr(
                self.raw_document,
                "storage_path",
                None,
            )

        return None

    @property
    def knowledge_topic(self):
        """
        取得 Knowledge Topic。
        """

        if self.knowledge is not None:

            return getattr(
                self.knowledge,
                "topic",
                None,
            )

        return None

    # ==================================================
    #
    # Dictionary
    #
    # ==================================================

    def to_dict(self):
        """
        將 Article 轉換成 Dictionary。

        注意：

            Parser 完成後，
            AI 尚未執行時：

                ai_summary       = None
                ai_category      = None
                ai_keywords      = None
                ai_importance    = None
                ai_model         = None
                ai_version       = None
                ai_analyze_time  = None
                ai_confidence    = None

            這與 SQL articles table
            的 NULL 設計一致。
        """

        return {
            # ==================================================
            # Database
            # ==================================================

            "id": self.id,

            "document_id": self.document_id,

            # ==================================================
            # Article Basic Data
            # ==================================================

            "keyword": self.keyword,

            "title": self.title,

            "url": self.url,

            "source": self.source,

            "published": self.published,

            "content": self.content,

            "crawl_time": self.crawl_time,

            "status": self.status,

            # ==================================================
            # Async AI Status
            # ==================================================

            "ai_status": self.ai_status,

            # ==================================================
            # AI Analysis
            #
            # 尚未分析時全部為 None。
            # ==================================================

            "ai_summary": self.ai_summary,

            "ai_category": self.ai_category,

            "ai_keywords": self.ai_keywords,

            "ai_importance": self.ai_importance,

            "ai_model": self.ai_model,

            "ai_version": self.ai_version,

            "ai_analyze_time": self.ai_analyze_time,

            "ai_confidence": self.ai_confidence,

            # ==================================================
            # Archive / Knowledge
            # ==================================================

            "archive_path": self.archive_path,

            "knowledge_topic": self.knowledge_topic,
        }

    # ==================================================
    #
    # Representation
    #
    # ==================================================

    def __repr__(self):
        """
        Article Debug Representation。
        """

        return (
            f"Article("
            f"id={self.id}, "
            f"title={self.title}, "
            f"AI={self.ai_category}, "
            f"importance={self.ai_importance}, "
            f"status={self.ai_status}"
            ")"
        )
