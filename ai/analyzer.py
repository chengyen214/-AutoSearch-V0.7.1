"""
ai/analyzer.py

AutoSearch V4

P1.6 AI Knowledge Intelligence Integration

AI Analyzer

流程:

Article / Article Content
        |
        v
    AI Analyzer
        |
        v
    AIAnalysis
        |
        v
KnowledgeExtractor
        |
        v
Knowledge Archive


功能:

1. Summary
2. Category Detection
3. Keyword Extraction
4. Importance Score
5. AI Metadata
6. Article Relation
"""


from models.ai_analysis import AIAnalysis
from utils.logger import logger


class AIAnalyzer:

    """
    Rule Based AI Analyzer

    V3 P4.4.3

    V4 P1.6 Compatible

    支援:

    - Article object
    - 純文字 content
    """

    def __init__(self):

        # ==========================
        # AI Metadata
        # ==========================

        self.ai_model = "RuleBased-V3"

        self.ai_version = "3.0"

        self.confidence = 0.9

        # ==========================
        # Category Dictionary
        # ==========================

        self.categories = {

            "Semiconductor": [

                "IC",
                "半導體",
                "晶片",
                "Chip",
                "AI Chip",
                "TSMC",
                "台積電",
                "晶圓",
                "2nm",
                "3nm",
                "CoWoS",
                "HBM",
                "封裝",
                "先進製程"

            ],

            "AI": [

                "AI",
                "人工智慧",
                "Machine Learning",
                "Deep Learning",
                "LLM",
                "GPT",
                "生成式AI"

            ],

            "Software": [

                "Software",
                "Cloud",
                "SaaS",
                "平台",
                "系統"

            ]

        }

        # ==========================
        # Keyword Priority
        # ==========================

        self.keyword_priority = [

            "2nm",
            "3nm",
            "AI Chip",
            "HBM",
            "CoWoS",
            "TSMC",
            "台積電",
            "半導體",
            "IC",
            "AI",
            "封裝"

        ]

    # ==================================================
    # Content Normalization
    # ==================================================

    def _get_content(self, article_or_content):

        """
        將 Article / str 統一轉換成文字。

        支援:

            analyze(article)

        以及:

            analyze("article content")
        """

        if article_or_content is None:

            return ""

        # 純文字

        if isinstance(article_or_content, str):

            return article_or_content

        # Article object

        content = getattr(
            article_or_content,
            "content",
            None
        )

        if content is None:

            return ""

        return str(content)

    # ==================================================
    # Article ID
    # ==================================================

    def _get_article_id(self, article):

        """
        從 Article 取得 database article_id。
        """

        if article is None:

            return None

        return getattr(
            article,
            "id",
            None
        )

    # ==================================================
    # Main Analyze
    # ==================================================

    def analyze(
        self,
        article_or_content,
        article_id=None
    ):

        """
        執行 AI Analysis。

        支援:

            analyzer.analyze(article)

        或:

            analyzer.analyze(content)

        或:

            analyzer.analyze(
                article,
                article_id=123
            )
        """

        # ==========================
        # Normalize Content
        # ==========================

        content = self._get_content(
            article_or_content
        )

        # ==========================
        # Article ID
        # ==========================

        if article_id is None:

            article_id = self._get_article_id(
                article_or_content
            )

        # ==========================
        # Category
        # ==========================

        category = self.detect_category(
            content
        )

        # ==========================
        # Summary
        # ==========================

        summary = self.generate_summary(
            content
        )

        # ==========================
        # Keywords
        # ==========================

        keywords = self.extract_keywords(
            content
        )

        # ==========================
        # Importance
        # ==========================

        importance = self.calculate_importance(
            content,
            keywords,
            category
        )

        # ==========================
        # AIAnalysis
        # ==========================

        result = AIAnalysis(

            article_id=article_id,

            summary=summary,

            category=category,

            keywords=keywords,

            importance=importance,

            ai_model=self.ai_model,

            ai_version=self.ai_version,

            confidence=self.confidence

        )

        logger.info(
            f"AI Analyze complete: "
            f"article_id={article_id}, "
            f"category={category}, "
            f"importance={importance}"
        )

        return result

    # ==================================================
    # Summary
    # ==================================================

    def generate_summary(
        self,
        content
    ):

        if not content:

            return ""

        text = str(content)

        text = text.replace(
            "\n",
            " "
        )

        text = " ".join(
            text.split()
        )

        return text[:200]

    # ==================================================
    # Category
    # ==================================================

    def detect_category(
        self,
        content
    ):

        if not content:

            return "Unknown"

        text = str(content).lower()

        scores = {}

        for category, words in self.categories.items():

            score = 0

            for word in words:

                if word.lower() in text:

                    score += 1

            scores[category] = score

        if not scores:

            return "Other"

        result = max(
            scores,
            key=scores.get
        )

        if scores[result] == 0:

            return "Other"

        return result

    # ==================================================
    # Keyword Extraction
    # ==================================================

    def extract_keywords(
        self,
        content
    ):

        if not content:

            return []

        text = str(content).lower()

        keywords = []

        for words in self.categories.values():

            for word in words:

                if word.lower() in text:

                    keywords.append(word)

        # Remove duplicate

        keywords = list(
            dict.fromkeys(
                keywords
            )
        )

        # Remove generic words

        remove_words = [

            "Chip"

        ]

        keywords = [

            keyword

            for keyword in keywords

            if keyword not in remove_words

        ]

        # Priority Sort

        keywords.sort(

            key=lambda keyword:

            self.keyword_priority.index(keyword)

            if keyword in self.keyword_priority

            else 99

        )

        return keywords[:8]

    # ==================================================
    # Importance
    # ==================================================

    def calculate_importance(
        self,
        content,
        keywords,
        category
    ):

        score = 0

        # ==========================
        # Keyword Bonus
        # ==========================

        score += len(
            keywords
        )

        # ==========================
        # Category Bonus
        # ==========================

        if category in [

            "Semiconductor",
            "AI"

        ]:

            score += 2

        # ==========================
        # Important Words
        # ==========================

        important_words = [

            "2nm",
            "3nm",
            "量產",
            "IPO",
            "投資",
            "收購",
            "突破",
            "重大"

        ]

        text = str(content).lower()

        for word in important_words:

            if word.lower() in text:

                score += 1

        # ==========================
        # Clamp 1 ~ 10
        # ==========================

        if score > 10:

            score = 10

        if score < 1:

            score = 1

        return score
