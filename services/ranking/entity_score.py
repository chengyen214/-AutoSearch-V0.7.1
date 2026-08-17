"""
services/ranking/entity_score.py

AutoSearch V4

P2.6 Step 3

Entity Score Calculator
"""

import json
import re


class EntityScoreCalculator:
    """
    Entity Score Calculator

    負責計算 Query 與
    SearchIndex.entities
    之間的 Entity 相關性。
    """

    SCORE_MAX = 10.0

    def _tokenize_keywords(self, query):
        """
        將 Query / Entity 拆成 Token。
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

    def _get_entities(self, search_index):
        """
        取得 SearchIndex.entities。

        支援：

            list
            tuple
            JSON string
            comma-separated string
            single string
            None
        """

        if search_index is None:
            return []

        entities = getattr(
            search_index,
            "entities",
            None
        )

        if not entities:
            return []

        if isinstance(
            entities,
            (list, tuple)
        ):

            return [
                str(entity)
                .strip()
                .lower()
                for entity in entities
                if str(entity).strip()
            ]

        if isinstance(
            entities,
            str
        ):

            value = entities.strip()

            if not value:
                return []

            try:

                parsed = json.loads(value)

                if isinstance(
                    parsed,
                    list
                ):

                    return [
                        str(entity)
                        .strip()
                        .lower()
                        for entity in parsed
                        if str(entity).strip()
                    ]

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError
            ):
                pass

            if "," in value:

                return [
                    entity.strip().lower()
                    for entity in value.split(",")
                    if entity.strip()
                ]

            return [
                value.lower()
            ]

        return []

    def calculate(self, query, search_index):
        """
        計算 Entity Score。

        Formula:

            matched_entities
            ---------------- × 10
            total_query_tokens
        """

        query_entities = self._tokenize_keywords(
            query
        )

        if not query_entities:
            return 0.0

        entities = self._get_entities(
            search_index
        )

        if not entities:
            return 0.0

        matched_count = 0

        for query_entity in query_entities:

            for entity in entities:

                entity_tokens = (
                    self._tokenize_keywords(entity)
                )

                if query_entity in entity_tokens:

                    matched_count += 1

                    break

        score = (
            matched_count
            / len(query_entities)
        ) * self.SCORE_MAX

        return round(
            min(
                score,
                self.SCORE_MAX
            ),
            2
        )