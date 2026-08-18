"""
services/ai_analysis_service.py

AutoSearch V4

P2.2.5 + P2.4

Async AI Analysis Pipeline

Pipeline:

Article
    |
    v
Content Safety / Input Limit
    |
    v
PromptBuilder
    |
    v
LLMClient
    |
    v
Groq LLM
    |
    v
JSONParser
    |
    v
AIAnalysis Result

功能：

    文章智慧分析
    Prompt 建立
    LLM 呼叫
    LLM JSON Parsing
    AIAnalysis Model 建立

輸出：

    summary
    keywords
    entities
    relations
    category
    importance

P2.4:

    支援 Async AI Worker
    使用真正 LLM 進行 AI Analysis。

目前 Provider / Model
由 config/ai_config.py + .env 控制。

例如：

    LLM_PROVIDER=groq
    LLM_MODEL=openai/gpt-oss-120b

Input Safety:

    Groq Free / On-Demand
    可能受到 TPM / request size 限制。

    因此本 Service 對文章內容
    進行最大輸入長度限制。

目前預設：

    6000 characters

策略：

    前 4500
    +
    後 1500

避免超長文章直接造成
Groq 413 Request Too Large。
"""


import os


from utils.logger import logger


from models.ai_analysis import AIAnalysis


from ai.llm_client import LLMClient


from ai.prompt import PromptBuilder


from ai.json_parser import JSONParser


from config.ai_config import (
    LLM_PROVIDER,
    LLM_MODEL
)


# ==================================================
# LLM Input Safety
# ==================================================

DEFAULT_MAX_CONTENT_CHARS = 6000

DEFAULT_HEAD_CHARS = 4500

DEFAULT_TAIL_CHARS = 1500


def _get_env_int(
    name,
    default
):
    """
    取得整數環境設定。

    如果環境變數不存在、
    格式錯誤或小於 1，
    使用 default。
    """

    try:

        value = int(
            os.getenv(
                name,
                str(default)
            )
        )

        if value < 1:

            return default

        return value

    except (
        TypeError,
        ValueError
    ):

        return default


# ==================================================
# Configurable Input Limit
# ==================================================

MAX_CONTENT_CHARS = _get_env_int(
    "AI_MAX_CONTENT_CHARS",
    DEFAULT_MAX_CONTENT_CHARS
)


class AIAnalysisService:
    """
    AI Analysis Service

    負責：

        文章智慧分析
        Prompt 建立
        LLM 呼叫
        LLM JSON Parsing
        AIAnalysis Model 建立

    不負責：

        Database
        API
        Queue
        Worker Lifecycle
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self
    ):

        # ==============================================
        # LLM Client
        # ==============================================

        self.llm_client = (
            LLMClient()
        )

        # ==============================================
        # Prompt Builder
        # ==============================================

        self.prompt_builder = (
            PromptBuilder()
        )

        # ==============================================
        # JSON Parser
        # ==============================================

        self.json_parser = (
            JSONParser()
        )

        # ==============================================
        # Log Configuration
        # ==============================================

        logger.info(
            "AIAnalysisService initialized."
        )

        logger.info(
            f"AI Provider : {LLM_PROVIDER}"
        )

        logger.info(
            f"AI Model    : {LLM_MODEL}"
        )

        logger.info(
            "AI Max Content Chars : "
            f"{MAX_CONTENT_CHARS}"
        )

    # ==================================================
    #
    # Main Analyze Function
    #
    # ==================================================

    def analyze(
        self,
        article
    ):
        """
        分析文章。

        Input:

            Article Model

            or

            dict

        Pipeline:

            Article
                |
                v
            Content Limit
                |
                v
            PromptBuilder
                |
                v
            LLMClient
                |
                v
            Groq
                |
                v
            JSONParser
                |
                v
            AIAnalysis

        Return:

            AIAnalysis Object

        """

        try:

            logger.info(
                "===== AI ANALYSIS START ====="
            )

            article_id = (
                self._get_article_id(
                    article
                )
            )

            logger.info(
                f"Article ID : {article_id}"
            )

            # ==========================================
            # Content Check
            # ==========================================

            content = (
                self._get_content(
                    article
                )
            )

            if not content.strip():

                raise ValueError(
                    "Article content is empty."
                )

            original_length = len(
                content
            )

            logger.info(
                "Original article content length : "
                f"{original_length}"
            )

            # ==========================================
            # Content Limit
            # ==========================================

            limited_content = (
                self._limit_content(
                    content
                )
            )

            limited_length = len(
                limited_content
            )

            logger.info(
                "LLM article content length : "
                f"{limited_length}"
            )

            if (
                limited_length
                < original_length
            ):

                logger.warning(
                    "Article content truncated "
                    "before LLM request: "
                    f"{original_length} -> "
                    f"{limited_length}"
                )

            # ==========================================
            # Prepare Article For Prompt
            # ==========================================

            prompt_article = (
                self._prepare_article_for_prompt(
                    article,
                    limited_content
                )
            )

            # ==========================================
            # Build Prompt
            # ==========================================

            prompt = self._build_prompt(
                prompt_article
            )

            logger.info(
                "AI Prompt generated."
            )

            logger.info(
                "Prompt length : "
                f"{len(prompt)}"
            )

            # ==========================================
            # LLM Request
            # ==========================================

            logger.info(
                "Sending article to LLM..."
            )

            response = (
                self.llm_client.analyze(
                    prompt
                )
            )

            if not response:

                raise ValueError(
                    "LLM returned empty response."
                )

            logger.info(
                "LLM response received."
            )

            # ==========================================
            # Parse JSON
            # ==========================================

            logger.info(
                "AI JSON parsing started"
            )

            data = (
                self.json_parser.parse(
                    response
                )
            )

            logger.info(
                "LLM JSON parsing completed."
            )

            # ==========================================
            # Build AIAnalysis
            # ==========================================

            analysis = AIAnalysis(

                article_id=article_id,

                summary=data.get(
                    "summary",
                    ""
                ),

                category=data.get(
                    "category",
                    ""
                ),

                keywords=data.get(
                    "keywords",
                    []
                ),

                # ======================================
                # Entity
                # ======================================

                entities=data.get(
                    "entities",
                    []
                ),

                # ======================================
                # Relation
                # ======================================

                relations=data.get(
                    "relations",
                    []
                ),

                importance=data.get(
                    "importance",
                    0
                ),

                # ======================================
                # AI Metadata
                # ======================================

                ai_model=LLM_MODEL,

                ai_version="4.0",

                confidence=0.8,

                status="completed"

            )

            logger.info(
                "===== AI ANALYSIS SUCCESS ====="
            )

            logger.info(
                f"Article ID : {article_id}"
            )

            logger.info(
                f"Category   : {analysis.category}"
            )

            logger.info(
                f"Importance : {analysis.importance}"
            )

            logger.info(
                f"Keywords   : "
                f"{len(analysis.keywords)}"
            )

            logger.info(
                f"Entities   : "
                f"{len(analysis.entities)}"
            )

            logger.info(
                f"Relations  : "
                f"{len(analysis.relations)}"
            )

            logger.info(
                f"Model      : {analysis.ai_model}"
            )

            return analysis

        except Exception as e:

            logger.exception(
                "AI Analysis failed."
            )

            logger.error(
                f"Article ID : "
                f"{self._get_article_id(article)}"
            )

            logger.error(
                f"Error      : {e}"
            )

            return None

    # ==================================================
    #
    # Content Limit
    #
    # ==================================================

    def _limit_content(
        self,
        content
    ):
        """
        限制送給 LLM 的文章內容長度。

        預設：

            MAX_CONTENT_CHARS = 6000

        策略：

            前 4500 字
            +
            後 1500 字

        如果文章長度不超過限制，
        則原樣返回。

        不修改 Database 裡的原始文章內容。
        """

        if content is None:

            return ""

        text = str(
            content
        )

        max_chars = (
            MAX_CONTENT_CHARS
        )

        if len(text) <= max_chars:

            return text

        # ==========================================
        # Head / Tail
        # ==========================================

        head_chars = min(
            DEFAULT_HEAD_CHARS,
            max_chars
        )

        tail_chars = (
            max_chars
            - head_chars
        )

        if tail_chars < 0:

            tail_chars = 0

        head = text[
            :head_chars
        ]

        tail = (
            text[-tail_chars:]
            if tail_chars > 0
            else ""
        )

        separator = (
            "\n\n"
            "[文章內容因 LLM 輸入限制而截斷]\n\n"
        )

        # ==========================================
        # Ensure Max Length
        # ==========================================

        available_chars = (
            max_chars
            - len(separator)
        )

        if available_chars < 1:

            return text[
                :max_chars
            ]

        # ==========================================
        # Recalculate Head / Tail
        # ==========================================

        adjusted_head = min(
            head_chars,
            available_chars
        )

        adjusted_tail = (
            available_chars
            - adjusted_head
        )

        result = (
            text[:adjusted_head]
            + separator
            + (
                text[-adjusted_tail:]
                if adjusted_tail > 0
                else ""
            )
        )

        # ==========================================
        # Final Safety
        # ==========================================

        if len(result) > max_chars:

            result = result[
                :max_chars
            ]

        return result

    # ==================================================
    #
    # Prepare Article For Prompt
    #
    # ==================================================

    def _prepare_article_for_prompt(
        self,
        article,
        limited_content
    ):
        """
        建立給 PromptBuilder 使用的 Article。

        注意：

            不修改真正 Database Article。

        只建立：

            Prompt Adapter
        """

        if isinstance(
            article,
            dict
        ):

            return self._dict_to_article_adapter(
                article,
                limited_content
            )

        class ArticleAdapter:
            pass

        adapter = ArticleAdapter()

        adapter.id = getattr(
            article,
            "id",
            None
        )

        adapter.title = getattr(
            article,
            "title",
            ""
        )

        adapter.source = getattr(
            article,
            "source",
            ""
        )

        adapter.published = getattr(
            article,
            "published",
            ""
        )

        adapter.content = (
            limited_content
        )

        return adapter

    # ==================================================
    #
    # Prompt Builder
    #
    # ==================================================

    def _build_prompt(
        self,
        article
    ):
        """
        建立 LLM Prompt。

        PromptBuilder 主要支援
        Article object。
        """

        if isinstance(
            article,
            dict
        ):

            article = (
                self._dict_to_article_adapter(
                    article,
                    self._get_content(
                        article
                    )
                )
            )

        return (
            self.prompt_builder.build(
                article
            )
        )

    # ==================================================
    #
    # Dict -> Article Adapter
    #
    # ==================================================

    def _dict_to_article_adapter(
        self,
        article,
        content=None
    ):
        """
        將 dict 轉換成 PromptBuilder
        可以使用的簡單物件。

        不修改真正的 Article Model。
        """

        class ArticleAdapter:
            pass

        adapter = ArticleAdapter()

        adapter.id = article.get(
            "id"
        )

        adapter.title = article.get(
            "title",
            ""
        )

        adapter.source = article.get(
            "source",
            ""
        )

        adapter.published = article.get(
            "published",
            ""
        )

        if content is None:

            content = article.get(
                "content",
                ""
            )

        adapter.content = content

        return adapter

    # ==================================================
    #
    # Article ID
    #
    # ==================================================

    def _get_article_id(
        self,
        article
    ):
        """
        取得 Article ID。
        """

        if isinstance(
            article,
            dict
        ):

            return article.get(
                "id"
            )

        return getattr(
            article,
            "id",
            None
        )

    # ==================================================
    #
    # Content Extract
    #
    # ==================================================

    def _get_content(
        self,
        article
    ):
        """
        取得文章內容。

        支援：

            Article Model

        以及：

            dict
        """

        if isinstance(
            article,
            dict
        ):

            title = article.get(
                "title",
                ""
            )

            content = article.get(
                "content",
                ""
            )

        else:

            title = getattr(
                article,
                "title",
                ""
            )

            content = getattr(
                article,
                "content",
                ""
            )

        title = (
            str(title)
            if title is not None
            else ""
        )

        content = (
            str(content)
            if content is not None
            else ""
        )

        return (
            title
            + "\n"
            + content
        )