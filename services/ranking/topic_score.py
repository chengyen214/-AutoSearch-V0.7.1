"""
services/ranking/topic_score.py

AutoSearch V4

P2.6 Step 4

Topic Score Calculator
"""

import re


class TopicScoreCalculator:
    """
    Topic Score Calculator

    負責計算 Query 與
    SearchIndex.topic
    之間的 Topic 相關性。
    """

    SCORE_MAX = 10.0

    def _tokenize_keywords(self, query):
        """
        將 Query / Topic 拆成 Token。
        """

        if not query:
            return []

        text = str(query).lower()

        tokens = re.findall(
            r"[^\W_]+",
            text,
            flags=re.UNICODE
        )

        return [
            token.strip()
            for token in tokens
            if token.strip()
        ]

    def _get_topic(self, search_index):
        """
        取得 SearchIndex.topic。
        """

        if search_index is None:
            return ""

        topic = getattr(
            search_index,
            "topic",
            ""
        )

        if topic is None:
            return ""

        return str(
            topic
        ).strip().lower()

    def calculate(self, query, search_index):
        """
        計算 Topic Score。

        Formula:

            matched_keywords
            ---------------- × 10
            total_query_tokens
        """

        query_tokens = self._tokenize_keywords(
            query
        )

        if not query_tokens:
            return 0.0

        topic = self._get_topic(
            search_index
        )

        if not topic:
            return 0.0

        topic_tokens = self._tokenize_keywords(
            topic
        )

        if not topic_tokens:
            return 0.0

        matched_count = 0

        for query_token in query_tokens:

            if query_token in topic_tokens:

                matched_count += 1

        score = (
            matched_count
            / len(query_tokens)
        ) * self.SCORE_MAX

        return round(
            min(
                score,
                self.SCORE_MAX
            ),
            2
        )